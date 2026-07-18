from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.market.providers.polarium.bootstrap import BootstrapAction, BootstrapRequest, BootstrapRequestFactory, HistoricalBootstrapManager
from app.market.providers.polarium.get_candles_envelope import GetCandlesEnvelopeDiagnostic
from app.market.providers.polarium.historical_request_sequence import HistoricalRequestSequenceDiagnostic
from app.market.providers.polarium.live_bootstrap_diagnostic import LiveBootstrapRequestDiagnostic
from app.market.providers.polarium.market_socket import MARKET_WS_HOST_FRAGMENT
from app.market.providers.polarium.native_bootstrap import (
    NativeBootstrapSendResult,
    NativeBootstrapStatus,
    NativeHistoricalBootstrapOrchestrator,
)
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.providers.polarium.target_manager import CDPTarget, DualTabCDPSessionManager
from app.market.store import CandleStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PolariumCDPLiveSourceConfig:
    enabled: bool
    chrome_path: str
    profile_dir: str
    trade_url: str
    friday_frontend_url: str
    cdp_port: int
    programmatic_selection_enabled: bool = False


@dataclass(frozen=True)
class PolariumCDPLiveSourceStatus:
    enabled: bool
    running: bool
    connected: bool
    last_error_code: str | None
    started_at: float | None
    received_events: int

    def sanitized(self) -> dict[str, Any]:
        return {
            "provider": "POLARIUM",
            "enabled": self.enabled,
            "running": self.running,
            "connected": self.connected,
            "last_error_code": self.last_error_code,
            "started_at": self.started_at,
            "received_events": self.received_events,
        }


@dataclass(frozen=True)
class ProgrammaticMarketSelectionResult:
    accepted: bool
    active_id: int
    raw_size: int
    subscribe_sent: bool
    bootstrap_sent: bool
    bootstrap_ready: bool
    chart_count: int
    session_context: dict[str, Any]
    error_code: str | None = None
    bootstrap_complete: bool = False

    def sanitized(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "active_id": self.active_id,
            "raw_size": self.raw_size,
            "subscribe_sent": self.subscribe_sent,
            "bootstrap_sent": self.bootstrap_sent,
            "bootstrap_ready": self.bootstrap_ready,
            "bootstrap_complete": self.bootstrap_complete,
            "chart_count": self.chart_count,
            "session_context": self.session_context,
            "error_code": self.error_code,
            "development_only": True,
            "source": "POLARIUM_CDP_PROGRAMMATIC_SELECTION",
        }


@dataclass(frozen=True)
class MarketSocketSendResult:
    sent: bool
    error_code: str | None = None
    socket_count: int | None = None
    open_socket_count: int | None = None
    selected_ready_state: int | None = None
    runtime_exception: str | None = None

    def sanitized(self) -> dict[str, Any]:
        return {
            "sent": self.sent,
            "error_code": self.error_code,
            "socket_count": self.socket_count,
            "open_socket_count": self.open_socket_count,
            "selected_ready_state": self.selected_ready_state,
            "runtime_exception": self.runtime_exception,
        }


class PolariumCDPLiveSource:
    """Read-only CDP observer that forwards market frames into Polarium runtime.

    The source never accepts credentials, cookies, tokens, HAR files, or browser
    extension data. It observes WebSocket frames from a dedicated Chrome profile
    and forwards only allowlisted market messages to PolariumMarketFeedRuntime.
    """

    def __init__(
        self,
        runtime: PolariumMarketFeedRuntime,
        config: PolariumCDPLiveSourceConfig,
        candle_store: CandleStore | None = None,
        historical_request_sequence: HistoricalRequestSequenceDiagnostic | None = None,
        get_candles_envelope: GetCandlesEnvelopeDiagnostic | None = None,
        live_bootstrap_diagnostic: LiveBootstrapRequestDiagnostic | None = None,
    ) -> None:
        self._runtime = runtime
        self._config = config
        self._candle_store = candle_store
        self._task: asyncio.Task[None] | None = None
        self._chrome: subprocess.Popen[bytes] | None = None
        self._running = False
        self._last_error_code: str | None = None
        self._started_at: float | None = None
        self._received_events = 0
        self._bootstrap = HistoricalBootstrapManager()
        self._native_bootstrap = NativeHistoricalBootstrapOrchestrator()
        self._historical_request_sequence = historical_request_sequence or HistoricalRequestSequenceDiagnostic()
        self._get_candles_envelope = get_candles_envelope or GetCandlesEnvelopeDiagnostic()
        self._live_bootstrap_diagnostic = live_bootstrap_diagnostic or LiveBootstrapRequestDiagnostic()
        self._programmatic_outbound_signatures: list[tuple[Any, ...]] = []
        self._programmatic_bootstrap_contexts: set[tuple[int, int]] = set()
        self._dual_tab = DualTabCDPSessionManager(friday_frontend_url=config.friday_frontend_url)
        self._cdp: _CDPClient | None = None

    def start_background(self) -> None:
        if not self._config.enabled or self._task is not None:
            return
        self._running = True
        self._started_at = time.time()
        self._task = asyncio.create_task(self._run(), name="polarium-cdp-live-source")

    async def stop(self) -> None:
        self._running = False
        self._programmatic_bootstrap_contexts.clear()
        self._programmatic_outbound_signatures.clear()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._chrome is not None and self._chrome.poll() is None:
            self._chrome.terminate()
            try:
                self._chrome.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._chrome.kill()

    def status(self) -> PolariumCDPLiveSourceStatus:
        runtime_status = self._runtime.status()
        return PolariumCDPLiveSourceStatus(
            enabled=self._config.enabled,
            running=self._running,
            connected=runtime_status.connected and runtime_status.market_socket_ready,
            last_error_code=self._last_error_code,
            started_at=self._started_at,
            received_events=self._received_events,
        )

    def observe_cdp_event(self, event: dict[str, Any]) -> None:
        self._observe_cdp_event(event)

    async def select_market(self, *, active_id: int, raw_size: int, timeout_seconds: float = 10.0) -> ProgrammaticMarketSelectionResult:
        if not self._config.programmatic_selection_enabled:
            return self._selection_result(active_id=active_id, raw_size=raw_size, error_code="PROGRAMMATIC_SELECTION_DISABLED")
        if active_id <= 0 or raw_size not in {60, 300, 900}:
            return self._selection_result(active_id=active_id, raw_size=raw_size, error_code="INVALID_MARKET_CONTEXT")
        status = self._runtime.status()
        if not (status.connected and status.authenticated and status.market_socket_ready):
            return self._selection_result(active_id=active_id, raw_size=raw_size, error_code="MARKET_SOCKET_NOT_READY")
        cdp = self._cdp
        if cdp is None:
            return self._selection_result(active_id=active_id, raw_size=raw_size, error_code="CDP_SESSION_NOT_READY")

        context_key = (active_id, raw_size)
        self._programmatic_bootstrap_contexts.add(context_key)
        try:
            native_result = await self._native_bootstrap.run(
                active_id=active_id,
                raw_size=raw_size,
                send=lambda payload: self._send_native_payload(cdp, payload),
                status=lambda: self._native_bootstrap_status(active_id=active_id, raw_size=raw_size),
                timeout_seconds=timeout_seconds,
            )
        finally:
            self._programmatic_bootstrap_contexts.discard(context_key)
        accepted = native_result.subscribe_sent and native_result.bootstrap_sent
        if not accepted:
            return self._selection_result(
                active_id=active_id,
                raw_size=raw_size,
                subscribe_sent=native_result.subscribe_sent,
                bootstrap_sent=native_result.bootstrap_sent,
                error_code=native_result.error_code or "NATIVE_BOOTSTRAP_SEND_FAILED",
            )
        return ProgrammaticMarketSelectionResult(
            accepted=accepted,
            active_id=active_id,
            raw_size=raw_size,
            subscribe_sent=native_result.subscribe_sent,
            bootstrap_sent=native_result.bootstrap_sent,
            bootstrap_ready=native_result.bootstrap_ready,
            bootstrap_complete=native_result.bootstrap_complete,
            chart_count=native_result.chart_count,
            session_context=native_result.session_context,
            error_code=native_result.error_code,
        )

    def _observe_cdp_event(self, event: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None, bool]:
        method = event.get("method")
        params = event.get("params")
        if not isinstance(params, dict):
            return (None, None, False)
        request_id = str(params.get("requestId", ""))
        if method == "Network.webSocketCreated":
            url = str(params.get("url", ""))
            if MARKET_WS_HOST_FRAGMENT in url:
                self._runtime.socket_discovery.register_socket(request_id=request_id, url=url)
            return (method, None, False)
        if method == "Network.webSocketClosed":
            self._runtime.socket_discovery.close_socket(request_id)
            return (method, None, False)
        if method not in {"Network.webSocketFrameReceived", "Network.webSocketFrameSent"}:
            return (method, None, False)
        response = params.get("response")
        if not isinstance(response, dict):
            return (method, None, False)
        payload_data = response.get("payloadData")
        if not isinstance(payload_data, str):
            return (method, None, False)
        message = _json_object(payload_data)
        if message is None:
            return (method, None, False)
        self._runtime.socket_discovery.observe_frame(request_id=request_id, message=message)
        is_market_socket_frame = self._is_market_socket_request(request_id)
        origin = "PAGE_NATIVE" if method == "Network.webSocketFrameSent" else "SERVER_INBOUND"
        self._runtime.observe_cdp_context_event(
            message,
            origin="PAGE_NATIVE" if origin == "PAGE_NATIVE" else "MARKET_WS",
            frame=method,
            request_id=_request_id(message),
            websocket=request_id,
            target_id=str(params.get("targetId")) if params.get("targetId") else None,
            now_ms=_epoch_ms(),
        )
        if origin == "PAGE_NATIVE":
            visible_active_id, visible_raw_size = _visible_context(message)
            self._live_bootstrap_diagnostic.observe_visible_context(
                active_id=visible_active_id,
                raw_size=visible_raw_size,
                now_ms=_epoch_ms(),
            )
            signature = _outbound_signature(message)
            if signature in self._programmatic_outbound_signatures:
                self._programmatic_outbound_signatures.remove(signature)
                return (method, message, is_market_socket_frame)
            else:
                self._historical_request_sequence.observe_outbound(message, origin="PAGE_NATIVE", now_ms=_epoch_ms())
                self._get_candles_envelope.observe_outbound(message, origin="PAGE_NATIVE", now_ms=_epoch_ms())
        result = self._runtime.process_message(message, origin=origin)
        self._received_events += 1
        if result.status == "dropped" and result.dropped_reason == "FORBIDDEN_INBOUND":
            self._last_error_code = "FORBIDDEN_INBOUND_DROPPED"
        if method == "Network.webSocketFrameReceived" and _event_name(message) in {"first-candles", "candles"}:
            current_context = self._runtime.status().sanitized()["session_context"]
            response_active_id = _find_first_int(message, {"active_id", "activeId"}) or _as_int(current_context.get("active_id"))
            response_raw_size = _find_first_int(message, {"size", "raw_size", "rawSize"}) or _as_int(current_context.get("raw_size"))
            self._native_bootstrap.observe_response(
                message,
                status=self._native_bootstrap_status(active_id=response_active_id, raw_size=response_raw_size),
                now_ms=_epoch_ms(),
            )
        if method == "Network.webSocketFrameSent" and _inner_name(message) == "get-first-candles":
            active_id, raw_size = _visible_context(message)
            now_ms = _epoch_ms()
            self._live_bootstrap_diagnostic.observe_owner(
                active_id=active_id,
                raw_size=raw_size,
                owner="PAGE_NATIVE",
                reason="MARKET_SOCKET" if is_market_socket_frame else "NON_MARKET_SOCKET",
                request_id=_request_id(message),
                market_socket_match=is_market_socket_frame,
                socket_request_id=request_id,
                now_ms=now_ms,
            )
            self._get_candles_envelope.observe_bootstrap_owner(
                owner="PAGE_NATIVE",
                active_id=active_id,
                raw_size=raw_size,
                request_id=_request_id(message),
                now_ms=now_ms,
            )
            if is_market_socket_frame:
                self._bootstrap.on_external_request(active_id=active_id, raw_size=raw_size, request_id=_request_id(message), now_ms=now_ms)
                self._live_bootstrap_diagnostic.observe_pending_registered(
                    active_id=active_id,
                    raw_size=raw_size,
                    request_id=_request_id(message),
                    now_ms=now_ms,
                )
        if method == "Network.webSocketFrameReceived" and _event_name(message) in {"first-candles", "candles"}:
            active_id, raw_size = _history_context(message)
            self._bootstrap.on_response(request_id=_request_id(message), active_id=active_id, raw_size=raw_size)
            response_context = self._runtime.status().sanitized()["session_context"]
            response_active_id = active_id or _as_int(response_context.get("active_id"))
            response_raw_size = raw_size or _as_int(response_context.get("raw_size"))
            self._live_bootstrap_diagnostic.observe_response(
                active_id=response_active_id,
                raw_size=response_raw_size,
                response_type=_event_name(message),
                response_request_id=_request_id(message),
                correlation_result="matched" if response_active_id is not None and response_raw_size is not None else "unresolved",
                parser_count=result.processed if result.status == "processed" else 0,
                store_results=result.store_results,
                history_count=_as_int(response_context.get("history_count")) or 0,
                readiness=response_context.get("history_state") if isinstance(response_context.get("history_state"), str) else None,
                now_ms=_epoch_ms(),
            )
        return (method, message, is_market_socket_frame)

    async def _handle_cdp_event(self, cdp: "_CDPClient", event: dict[str, Any]) -> None:
        method, message, is_market_socket_frame = self._observe_cdp_event(event)
        if method in {"Network.webSocketFrameReceived", "Network.webSocketFrameSent"}:
            if method == "Network.webSocketFrameSent" and message is not None and _inner_name(message) == "get-first-candles" and is_market_socket_frame:
                return
            await self._maybe_send_bootstrap(cdp)

    async def _process_cdp_tick(self, cdp: "_CDPClient", event: dict[str, Any] | None) -> None:
        try:
            if event is not None:
                await self._handle_cdp_event(cdp, event)
            else:
                await self._maybe_send_bootstrap(cdp)
            await self._maybe_open_friday_tab(cdp)
        except Exception as exc:
            self._last_error_code = exc.__class__.__name__.upper()

    async def _run(self) -> None:
        try:
            self._start_chrome()
            target_ws = await asyncio.to_thread(_wait_for_page_target, self._config.cdp_port, _target_url_fragment(self._config.trade_url))
            async with _CDPClient(target_ws) as cdp:
                self._cdp = cdp
                await cdp.call("Network.enable")
                await cdp.call("Runtime.enable")
                await cdp.call("Page.enable")
                await cdp.install_market_socket_bridge()
                await cdp.call("Page.navigate", {"url": self._config.trade_url})
                while self._running:
                    try:
                        event = await cdp.next_event(timeout=1.0)
                        await self._process_cdp_tick(cdp, event)
                    except Exception as exc:
                        self._last_error_code = exc.__class__.__name__.upper()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._last_error_code = exc.__class__.__name__.upper()
        finally:
            self._cdp = None
            self._programmatic_bootstrap_contexts.clear()
            self._programmatic_outbound_signatures.clear()
            self._running = False

    def _start_chrome(self) -> None:
        chrome_path = Path(self._config.chrome_path)
        if not chrome_path.exists():
            raise RuntimeError("POLARIUM_CHROME_NOT_FOUND")
        Path(self._config.profile_dir).mkdir(parents=True, exist_ok=True)
        self._chrome = subprocess.Popen(
            [
                str(chrome_path),
                f"--remote-debugging-port={self._config.cdp_port}",
                f"--user-data-dir={self._config.profile_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                self._config.trade_url,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info("[POLARIUM_CDP] START_CHROME")

    def _is_market_socket_request(self, request_id: str) -> bool:
        market_socket = self._runtime.socket_discovery.market_socket
        return bool(market_socket and market_socket.active and market_socket.request_id == request_id)

    async def _maybe_send_bootstrap(self, cdp: "_CDPClient") -> None:
        status = self._runtime.status()
        context = status.session_context or {}
        now_ms = _epoch_ms()
        socket_ready = bool(status.connected and status.authenticated and status.market_socket_ready)
        active_id = _as_int(context.get("active_id"))
        raw_size = _as_int(context.get("raw_size"))
        if not self._config.programmatic_selection_enabled:
            self._live_bootstrap_diagnostic.observe_programmatic_state(
                active_contexts=len(self._programmatic_bootstrap_contexts),
                outbound_signatures=len(self._programmatic_outbound_signatures),
                now_ms=now_ms,
            )
        if active_id is not None and raw_size is not None and (active_id, raw_size) in self._programmatic_bootstrap_contexts:
            self._live_bootstrap_diagnostic.observe_decision(
                active_id=active_id,
                raw_size=raw_size,
                decision="none",
                reason="PROGRAMMATIC_CONTEXT_ACTIVE",
                now_ms=now_ms,
            )
            return
        action = self._bootstrap.on_visible_context(active_id=active_id, raw_size=raw_size, now_ms=now_ms, socket_ready=socket_ready)
        self._live_bootstrap_diagnostic.observe_decision(
            active_id=active_id,
            raw_size=raw_size,
            decision=action.kind,
            reason=action.reason,
            now_ms=now_ms,
        )
        if action.kind in {"send", "retry"} and action.request is not None:
            await self._send_bootstrap_request(cdp, action)
            return
        retry_action = self._bootstrap.tick(now_ms=now_ms, socket_ready=socket_ready)
        self._live_bootstrap_diagnostic.observe_decision(
            active_id=active_id,
            raw_size=raw_size,
            decision=retry_action.kind,
            reason=retry_action.reason,
            now_ms=now_ms,
        )
        if retry_action.kind in {"send", "retry"} and retry_action.request is not None:
            await self._send_bootstrap_request(cdp, retry_action)
        elif retry_action.kind == "failed":
            self._last_error_code = "BOOTSTRAP_FAILED"

    async def _send_bootstrap_request(self, cdp: "_CDPClient", action: BootstrapAction) -> bool:
        request = action.request
        if request is None:
            return False
        self._live_bootstrap_diagnostic.observe_request_created(
            active_id=request.active_id,
            raw_size=request.raw_size,
            request_id=request.request_id,
            now_ms=request.created_at,
        )
        send_result = await self._send_programmatic_payload(cdp, request.payload, now_ms=request.created_at)
        market_socket = self._runtime.socket_discovery.market_socket
        socket_request_id = market_socket.request_id if market_socket else None
        self._live_bootstrap_diagnostic.observe_send(
            active_id=request.active_id,
            raw_size=request.raw_size,
            request_id=request.request_id,
            socket_request_id=socket_request_id,
            market_socket_match=bool(market_socket and market_socket.active),
            attempted=True,
            succeeded=send_result.sent,
            error_code=send_result.error_code,
            now_ms=request.created_at,
        )
        if send_result.sent:
            self._get_candles_envelope.observe_bootstrap_owner(
                owner="AUTO_VISIBLE_CONTEXT",
                active_id=request.active_id,
                raw_size=request.raw_size,
                request_id=request.request_id,
                now_ms=request.created_at,
            )
            self._bootstrap.on_external_request(active_id=request.active_id, raw_size=request.raw_size, request_id=request.request_id, now_ms=request.created_at)
            self._live_bootstrap_diagnostic.observe_pending_registered(
                active_id=request.active_id,
                raw_size=request.raw_size,
                request_id=request.request_id,
                now_ms=request.created_at,
            )
            self._runtime.process_message(request.payload, origin="PAGE_NATIVE", now_ms=request.created_at)
            return True
        self._last_error_code = send_result.error_code or "BOOTSTRAP_MARKET_SOCKET_SEND_FAILED"
        return False

    async def _send_programmatic_payload(self, cdp: "_CDPClient", payload: dict[str, Any], *, now_ms: int | None = None) -> MarketSocketSendResult:
        sent_at = now_ms or _epoch_ms()
        send_result = await cdp.send_market_websocket_payload(payload)
        if send_result.sent:
            self._programmatic_outbound_signatures.append(_outbound_signature(payload))
            self._historical_request_sequence.observe_outbound(payload, origin="FRIDAY_PROGRAMMATIC", now_ms=sent_at)
            self._get_candles_envelope.observe_outbound(payload, origin="FRIDAY_PROGRAMMATIC", now_ms=sent_at)
            self._runtime.process_message(payload, origin="PAGE_NATIVE", now_ms=sent_at)
        return send_result

    async def _send_native_payload(self, cdp: "_CDPClient", payload: dict[str, Any]) -> NativeBootstrapSendResult:
        result = await self._send_programmatic_payload(cdp, payload)
        if result.sent and _inner_name(payload) == "get-first-candles":
            self._get_candles_envelope.observe_bootstrap_owner(
                owner="NATIVE_ORCHESTRATOR",
                active_id=_find_first_int(payload, {"active_id", "activeId"}),
                raw_size=_find_first_int(payload, {"size", "raw_size", "rawSize"}),
                request_id=_request_id(payload),
                now_ms=_epoch_ms(),
            )
        return NativeBootstrapSendResult(sent=result.sent, error_code=result.error_code)

    def _bootstrap_request(self, *, active_id: int, raw_size: int) -> BootstrapRequest:
        return BootstrapRequestFactory().create(active_id=active_id, raw_size=raw_size, now_ms=_epoch_ms(), attempt=1)

    def _selection_ready(self, *, active_id: int, raw_size: int) -> ProgrammaticMarketSelectionResult:
        context = self._runtime.status().sanitized()["session_context"]
        chart_count = len(self._candle_store.series(active_id=active_id, raw_size=raw_size)) if self._candle_store is not None else 0
        history_count = _as_int(context.get("history_count")) or 0
        history_required = _as_int(context.get("history_required")) or 0
        bootstrap_ready = (
            context.get("active_id") == active_id
            and context.get("raw_size") == raw_size
            and context.get("history_state") == "READY"
            and history_required > 0
            and history_count >= history_required
        )
        return ProgrammaticMarketSelectionResult(
            accepted=True,
            active_id=active_id,
            raw_size=raw_size,
            subscribe_sent=True,
            bootstrap_sent=True,
            bootstrap_ready=bootstrap_ready,
            bootstrap_complete=bootstrap_ready,
            chart_count=chart_count,
            session_context=context,
        )

    def _native_bootstrap_status(self, *, active_id: int | None, raw_size: int | None) -> NativeBootstrapStatus:
        if active_id is None or raw_size is None:
            context = self._runtime.status().sanitized()["session_context"]
            return NativeBootstrapStatus(
                bootstrap_ready=False,
                bootstrap_complete=False,
                chart_count=0,
                session_context=context,
            )
        ready = self._selection_ready(active_id=active_id, raw_size=raw_size)
        return NativeBootstrapStatus(
            bootstrap_ready=ready.bootstrap_ready,
            bootstrap_complete=ready.bootstrap_complete,
            chart_count=ready.chart_count,
            session_context=ready.session_context,
        )

    def _selection_result(
        self,
        *,
        active_id: int,
        raw_size: int,
        subscribe_sent: bool = False,
        bootstrap_sent: bool = False,
        error_code: str,
    ) -> ProgrammaticMarketSelectionResult:
        return ProgrammaticMarketSelectionResult(
            accepted=False,
            active_id=active_id,
            raw_size=raw_size,
            subscribe_sent=subscribe_sent,
            bootstrap_sent=bootstrap_sent,
            bootstrap_ready=False,
            bootstrap_complete=False,
            chart_count=0,
            session_context=self._runtime.status().sanitized()["session_context"],
            error_code=error_code,
        )

    async def _maybe_open_friday_tab(self, cdp: "_CDPClient") -> None:
        status = self._runtime.status()
        market_ready = bool(status.connected and status.authenticated and status.market_socket_ready)
        targets = await asyncio.to_thread(_list_cdp_targets, self._config.cdp_port)
        frontend_available = await asyncio.to_thread(_url_available, self._config.friday_frontend_url)
        if frontend_available:
            logger.info("[POLARIUM_CDP] FRONTEND_FOUND")
        plan = self._dual_tab.plan(targets=targets, market_ready=market_ready, frontend_available=frontend_available, now_ms=_epoch_ms())
        if plan.action == "open_friday":
            logger.info("[POLARIUM_CDP] OPEN_FRIDAY_START")
            logger.info("[POLARIUM_CDP] TARGET_CREATE_REQUEST")
            try:
                target_id = await cdp.create_target(plan.friday_url)
            except Exception as exc:
                self._last_error_code = exc.__class__.__name__.upper()
                logger.info("[POLARIUM_CDP] TARGET_CREATE_FAILED")
                return
            if target_id is None:
                self._last_error_code = "TARGET_CREATE_FAILED"
                logger.info("[POLARIUM_CDP] TARGET_CREATE_FAILED")
                return
            self._dual_tab.mark_opened(target_id)
            logger.info("[POLARIUM_CDP] TARGET_CREATE_SUCCESS")
        elif plan.action == "reuse_friday":
            self._dual_tab.mark_opened(plan.friday_target_id)
            logger.info("[POLARIUM_CDP] FRIDAY_ALREADY_OPEN")
        elif plan.action == "skip":
            logger.info("[POLARIUM_CDP] OPEN_FRIDAY_SKIPPED reason=%s", plan.reason)
        elif plan.action == "wait":
            logger.info("[POLARIUM_CDP] OPEN_FRIDAY_WAIT reason=%s", plan.reason)


class _CDPClient:
    def __init__(self, websocket_url: str) -> None:
        self.websocket_url = websocket_url
        self._next_id = 1
        self._pending: dict[int, asyncio.Future[dict[str, Any]]] = {}
        self._events: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._ws: Any = None

    async def __aenter__(self) -> "_CDPClient":
        import websockets

        self._ws = await websockets.connect(self.websocket_url, max_size=8_000_000)
        asyncio.create_task(self._reader())
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._ws is not None:
            await self._ws.close()

    async def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        message_id = self._next_id
        self._next_id += 1
        future: asyncio.Future[dict[str, Any]] = asyncio.get_running_loop().create_future()
        self._pending[message_id] = future
        await self._ws.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        response = await asyncio.wait_for(future, timeout=10)
        if "error" in response:
            raise RuntimeError("CDP_CALL_FAILED")
        return response.get("result", {})

    async def install_market_socket_bridge(self) -> None:
        await self.call(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": _MARKET_SOCKET_BRIDGE_SCRIPT},
        )

    async def send_market_websocket_payload(self, payload: dict[str, Any]) -> MarketSocketSendResult:
        payload_json = json.dumps(json.dumps(payload, separators=(",", ":")))
        expression = (
            "(() => {"
            "try {"
            "const bridge = window.__FRIDAY_POLARIUM_CDP_BOOTSTRAP__;"
            "if (!bridge || typeof bridge.send !== 'function') return {sent:false,error_code:'MARKET_SOCKET_REFERENCE_MISSING'};"
            f"const result = bridge.send({payload_json});"
            "if (result && typeof result === 'object') return result;"
            "return {sent:Boolean(result),error_code:Boolean(result)?null:'SUBSCRIBE_MESSAGE_SEND_FAILED'};"
            "} catch (error) {"
            "return {sent:false,error_code:'RUNTIME_EVALUATE_FAILED',runtime_exception:String(error && error.name ? error.name : 'Error')};"
            "}"
            "})()"
        )
        try:
            result = await self.call(
                "Runtime.evaluate",
                {"expression": expression, "returnByValue": True},
            )
        except Exception:
            return MarketSocketSendResult(sent=False, error_code="RUNTIME_EVALUATE_FAILED")
        value = _runtime_evaluate_value(result)
        if not isinstance(value, dict):
            return MarketSocketSendResult(sent=bool(value), error_code=None if bool(value) else "RUNTIME_EVALUATE_FAILED")
        return MarketSocketSendResult(
            sent=bool(value.get("sent")),
            error_code=_safe_error_code(value.get("error_code")),
            socket_count=_as_int(value.get("socket_count")),
            open_socket_count=_as_int(value.get("open_socket_count")),
            selected_ready_state=_as_int(value.get("selected_ready_state")),
            runtime_exception=_safe_error_code(value.get("runtime_exception")),
        )

    async def create_target(self, url: str) -> str | None:
        result = await self.call("Target.createTarget", {"url": url})
        target_id = result.get("targetId")
        return target_id if isinstance(target_id, str) else None

    async def next_event(self, *, timeout: float) -> dict[str, Any] | None:
        try:
            return await asyncio.wait_for(self._events.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    async def _reader(self) -> None:
        try:
            async for raw in self._ws:
                message = json.loads(raw)
                message_id = message.get("id")
                if isinstance(message_id, int) and message_id in self._pending:
                    self._pending.pop(message_id).set_result(message)
                elif isinstance(message.get("method"), str):
                    await self._events.put(message)
        except Exception:
            return


def _wait_for_page_target(cdp_port: int, url_fragment: str = "trade.polariumbroker.com") -> str:
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=1) as response:
                targets = json.loads(response.read().decode("utf-8"))
            for target in targets:
                if (
                    target.get("type") == "page"
                    and target.get("webSocketDebuggerUrl")
                    and url_fragment in str(target.get("url", ""))
                ):
                    logger.info("[POLARIUM_CDP] POLARIUM_TARGET_FOUND")
                    return str(target["webSocketDebuggerUrl"])
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("POLARIUM_CDP_TARGET_NOT_FOUND")


def _target_url_fragment(url: str) -> str:
    if "trade.polariumbroker.com" in url:
        return "trade.polariumbroker.com"
    return url.rstrip("/")


def _list_cdp_targets(cdp_port: int) -> tuple[CDPTarget, ...]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=1) as response:
            targets = json.loads(response.read().decode("utf-8"))
    except Exception:
        return ()
    parsed: list[CDPTarget] = []
    if not isinstance(targets, list):
        return ()
    for target in targets:
        if not isinstance(target, dict):
            continue
        parsed.append(
            CDPTarget(
                target_id=str(target.get("id", "")),
                url=str(target.get("url", "")),
                kind=str(target.get("type", "")),
            )
        )
    return tuple(parsed)


def _url_available(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            return 200 <= int(response.status) < 500
    except Exception:
        return False


def _json_object(raw: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _epoch_ms() -> int:
    return int(time.time() * 1000)


def _event_name(message: dict[str, Any]) -> str | None:
    value = message.get("name")
    if isinstance(value, str) and value != "sendMessage":
        return value
    inner = _inner_name(message)
    return inner or value if isinstance(value, str) else inner


def _inner_name(message: dict[str, Any]) -> str | None:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return None
    value = msg.get("name")
    return value if isinstance(value, str) else None


def _request_id(message: dict[str, Any]) -> str | None:
    value = message.get("request_id") or message.get("requestId")
    return value if isinstance(value, str) and value else None


def _visible_context(message: dict[str, Any]) -> tuple[int | None, int | None]:
    body = _body(message)
    routing_filters = _routing_filters(message)
    active_id = _as_int(body.get("active_id")) or _as_int(routing_filters.get("active_id"))
    raw_size = _as_int(body.get("size")) or _as_int(body.get("raw_size")) or _as_int(routing_filters.get("size"))
    return (active_id, raw_size)


def _history_context(message: dict[str, Any]) -> tuple[int | None, int | None]:
    return (_find_first_int(message, {"active_id", "activeId"}), _find_first_int(message, {"size", "raw_size", "rawSize"}))


def _outbound_signature(message: dict[str, Any]) -> tuple[Any, ...]:
    return (
        _event_name(message),
        _inner_name(message),
        _find_first_int(message, {"active_id", "activeId"}),
        _find_first_int(message, {"size", "raw_size", "rawSize"}),
        _find_first_int(message, {"count", "limit"}),
        _find_first_int(message, {"from", "start", "startTime", "start_time"}),
        _find_first_int(message, {"to", "end", "endTime", "end_time"}),
        _find_first_int(message, {"offset"}),
    )


def _body(message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return {}
    body = msg.get("body")
    return body if isinstance(body, dict) else {}


def _routing_filters(message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return {}
    params = msg.get("params")
    if not isinstance(params, dict):
        return {}
    filters = params.get("routingFilters")
    return filters if isinstance(filters, dict) else {}


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _runtime_evaluate_value(result: dict[str, Any]) -> Any:
    nested = result.get("result")
    if isinstance(nested, dict) and "value" in nested:
        return nested.get("value")
    if "value" in result:
        return result.get("value")
    return None


def _safe_error_code(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    if not normalized:
        return None
    if any(term in normalized.lower() for term in ("token", "cookie", "authorization", "bearer", "ssid", "password")):
        return "SANITIZED_ERROR"
    return normalized[:80]


def _find_first_int(value: Any, keys: set[str]) -> int | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys:
                parsed = _as_int(item)
                if parsed is not None:
                    return parsed
            parsed = _find_first_int(item, keys)
            if parsed is not None:
                return parsed
    if isinstance(value, list):
        for item in value:
            parsed = _find_first_int(item, keys)
            if parsed is not None:
                return parsed
    return None


_MARKET_SOCKET_BRIDGE_SCRIPT = """
(() => {
  if (window.__FRIDAY_POLARIUM_CDP_BOOTSTRAP_INSTALLED__) return;
  window.__FRIDAY_POLARIUM_CDP_BOOTSTRAP_INSTALLED__ = true;
  const NativeWebSocket = window.WebSocket;
  const marketSockets = [];
  const marketHost = "ws.trade.polariumbroker.com";

  function remember(socket, url) {
    if (String(url || "").includes(marketHost) && !marketSockets.includes(socket)) {
      marketSockets.push(socket);
    }
  }

  function FridayPolariumWebSocket(url, protocols) {
    const socket = protocols ? new NativeWebSocket(url, protocols) : new NativeWebSocket(url);
    remember(socket, url);
    return socket;
  }

  FridayPolariumWebSocket.prototype = NativeWebSocket.prototype;
  FridayPolariumWebSocket.CONNECTING = NativeWebSocket.CONNECTING;
  FridayPolariumWebSocket.OPEN = NativeWebSocket.OPEN;
  FridayPolariumWebSocket.CLOSING = NativeWebSocket.CLOSING;
  FridayPolariumWebSocket.CLOSED = NativeWebSocket.CLOSED;
  FridayPolariumWebSocket.__originalWebSocket = NativeWebSocket;

  Object.defineProperty(window, "WebSocket", {
    configurable: true,
    writable: true,
    value: FridayPolariumWebSocket
  });

  window.__FRIDAY_POLARIUM_CDP_BOOTSTRAP__ = {
    send(payload) {
      const socketCount = marketSockets.length;
      const openSockets = marketSockets.filter((item) => item && item.readyState === NativeWebSocket.OPEN);
      if (typeof payload !== "string") {
        return { sent: false, error_code: "SUBSCRIBE_PAYLOAD_INVALID", socket_count: socketCount, open_socket_count: openSockets.length };
      }
      const socket = [...openSockets].reverse()[0];
      if (!socket && socketCount === 0) {
        return { sent: false, error_code: "MARKET_SOCKET_REFERENCE_MISSING", socket_count: socketCount, open_socket_count: openSockets.length };
      }
      if (!socket) {
        const lastSocket = [...marketSockets].reverse().find((item) => item);
        return { sent: false, error_code: "MARKET_SOCKET_NOT_OPEN", socket_count: socketCount, open_socket_count: openSockets.length, selected_ready_state: lastSocket ? lastSocket.readyState : null };
      }
      try {
        socket.send(payload);
        return { sent: true, error_code: null, socket_count: socketCount, open_socket_count: openSockets.length, selected_ready_state: socket.readyState };
      } catch (error) {
        return { sent: false, error_code: "WEBSOCKET_SEND_EXCEPTION", socket_count: socketCount, open_socket_count: openSockets.length, selected_ready_state: socket.readyState, runtime_exception: String(error && error.name ? error.name : "Error") };
      }
    },
    status() {
      return { installed: true, sockets: marketSockets.length };
    }
  };
})();
"""
