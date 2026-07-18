from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from app.market.providers.polarium.market_subscription import PolariumMarketSubscriptionFactory
from app.market.providers.polarium.runtime_guard import PolariumRuntimeGuard

NativeBootstrapStepKind = Literal["subscribe", "get-first-candles", "get-candles"]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "native_bootstrap_sequence_report.json"
REPORT_TXT = REPORT_DIR / "native_bootstrap_sequence_report.txt"


@dataclass(frozen=True)
class NativeBootstrapStatus:
    bootstrap_ready: bool
    bootstrap_complete: bool
    chart_count: int
    session_context: dict[str, Any]


@dataclass(frozen=True)
class NativeBootstrapSendResult:
    sent: bool
    error_code: str | None = None


@dataclass(frozen=True)
class NativeBootstrapResult:
    subscribe_sent: bool
    bootstrap_sent: bool
    bootstrap_complete: bool
    bootstrap_ready: bool
    chart_count: int
    session_context: dict[str, Any]
    error_code: str | None = None


@dataclass(frozen=True)
class NativeBootstrapStep:
    order: int
    kind: NativeBootstrapStepKind
    payload: dict[str, Any]


@dataclass
class NativeBootstrapReportEntry:
    step: int
    phase: str
    request_id: str | None
    name: str | None
    inner_name: str | None
    active_id: int | None
    raw_size: int | None
    sent: bool | None
    response_type: str | None
    history_count: int
    history_required: int
    readiness: str | None
    bootstrap_complete: bool
    chart_count: int
    elapsed_ms: int
    error_code: str | None = None

    def sanitized(self) -> dict[str, Any]:
        return asdict(self)


class NativeBootstrapSequenceReport:
    def __init__(
        self,
        *,
        report_json: Path | str = REPORT_JSON,
        report_txt: Path | str = REPORT_TXT,
        auto_write: bool = True,
    ) -> None:
        self._report_json = Path(report_json)
        self._report_txt = Path(report_txt)
        self._auto_write = auto_write
        self._entries: list[NativeBootstrapReportEntry] = []

    @property
    def entries(self) -> tuple[NativeBootstrapReportEntry, ...]:
        return tuple(self._entries)

    def clear(self) -> None:
        self._entries.clear()
        self._write_if_enabled()

    def record_request(
        self,
        *,
        step: NativeBootstrapStep,
        sent: bool,
        status: NativeBootstrapStatus,
        started_at_ms: int,
        now_ms: int,
        error_code: str | None = None,
    ) -> None:
        self._entries.append(
            NativeBootstrapReportEntry(
                step=step.order,
                phase="REQUEST",
                request_id=_request_id(step.payload),
                name=_event_name(step.payload),
                inner_name=_inner_name(step.payload),
                active_id=_find_first_int(step.payload, {"active_id", "activeId"}),
                raw_size=_find_first_int(step.payload, {"size", "raw_size", "rawSize"}),
                sent=sent,
                response_type=None,
                history_count=_history_count(status.session_context),
                history_required=_history_required(status.session_context),
                readiness=_history_state(status.session_context),
                bootstrap_complete=status.bootstrap_complete,
                chart_count=status.chart_count,
                elapsed_ms=max(0, now_ms - started_at_ms),
                error_code=error_code,
            )
        )
        self._write_if_enabled()

    def record_response(
        self,
        *,
        message: dict[str, Any],
        status: NativeBootstrapStatus,
        started_at_ms: int,
        now_ms: int,
    ) -> None:
        self._entries.append(
            NativeBootstrapReportEntry(
                step=len(self._entries) + 1,
                phase="RESPONSE",
                request_id=_request_id(message),
                name=_event_name(message),
                inner_name=_inner_name(message),
                active_id=_find_first_int(message, {"active_id", "activeId"}),
                raw_size=_find_first_int(message, {"size", "raw_size", "rawSize"}),
                sent=None,
                response_type=_event_name(message),
                history_count=_history_count(status.session_context),
                history_required=_history_required(status.session_context),
                readiness=_history_state(status.session_context),
                bootstrap_complete=status.bootstrap_complete,
                chart_count=status.chart_count,
                elapsed_ms=max(0, now_ms - started_at_ms),
            )
        )
        self._write_if_enabled()

    def write_reports(self) -> None:
        self._report_json.parent.mkdir(parents=True, exist_ok=True)
        payload = self.sanitized()
        self._report_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._report_txt.write_text(_render_text(payload), encoding="utf-8")

    def sanitized(self) -> dict[str, Any]:
        entries = [entry.sanitized() for entry in self._entries]
        return {
            "summary": {
                "total_entries": len(entries),
                "requests": sum(1 for item in entries if item["phase"] == "REQUEST"),
                "responses": sum(1 for item in entries if item["phase"] == "RESPONSE"),
                "last_readiness": entries[-1]["readiness"] if entries else None,
                "last_history_count": entries[-1]["history_count"] if entries else 0,
                "bootstrap_complete": entries[-1]["bootstrap_complete"] if entries else False,
            },
            "entries": entries,
        }

    def _write_if_enabled(self) -> None:
        if self._auto_write:
            self.write_reports()


class NativeHistoricalBootstrapOrchestrator:
    """Replays the sanitized native Polarium historical bootstrap sequence."""

    def __init__(
        self,
        *,
        guard: PolariumRuntimeGuard | None = None,
        subscription_factory: PolariumMarketSubscriptionFactory | None = None,
        report: NativeBootstrapSequenceReport | None = None,
        response_timeout_seconds: float = 3.0,
        request_spacing_seconds: float = 0.05,
    ) -> None:
        self._guard = guard or PolariumRuntimeGuard()
        self._subscription_factory = subscription_factory or PolariumMarketSubscriptionFactory()
        self._report = report or NativeBootstrapSequenceReport()
        self._response_timeout_seconds = response_timeout_seconds
        self._request_spacing_seconds = request_spacing_seconds
        self._active_context: tuple[int, int] | None = None
        self._first_response_seen = asyncio.Event()
        self._last_started_at_ms = 0

    @property
    def report(self) -> NativeBootstrapSequenceReport:
        return self._report

    async def run(
        self,
        *,
        active_id: int,
        raw_size: int,
        send: Callable[[dict[str, Any]], Awaitable[NativeBootstrapSendResult]],
        status: Callable[[], NativeBootstrapStatus],
        timeout_seconds: float,
    ) -> NativeBootstrapResult:
        self._active_context = (active_id, raw_size)
        self._first_response_seen = asyncio.Event()
        self._last_started_at_ms = _epoch_ms()
        self._report.clear()

        steps = self._build_steps(active_id=active_id, raw_size=raw_size)
        subscribe_sent = False
        bootstrap_sent = False

        for step in steps[:2]:
            result = await self._send_step(step=step, send=send, status=status)
            if step.kind == "subscribe":
                subscribe_sent = result.sent
            if step.kind == "get-first-candles":
                bootstrap_sent = bootstrap_sent or result.sent
            if not result.sent:
                current = status()
                return NativeBootstrapResult(
                    subscribe_sent=subscribe_sent,
                    bootstrap_sent=bootstrap_sent,
                    bootstrap_complete=current.bootstrap_complete,
                    bootstrap_ready=current.bootstrap_ready,
                    chart_count=current.chart_count,
                    session_context=current.session_context,
                    error_code=result.error_code or "NATIVE_BOOTSTRAP_SEND_FAILED",
                )

        if not await self._wait_for_first_response(timeout_seconds=min(self._response_timeout_seconds, max(0.1, timeout_seconds))):
            current = status()
            return NativeBootstrapResult(
                subscribe_sent=subscribe_sent,
                bootstrap_sent=bootstrap_sent,
                bootstrap_complete=current.bootstrap_complete,
                bootstrap_ready=current.bootstrap_ready,
                chart_count=current.chart_count,
                session_context=current.session_context,
                error_code="FIRST_CANDLES_RESPONSE_TIMEOUT",
            )

        for step in steps[2:]:
            result = await self._send_step(step=step, send=send, status=status)
            if step.kind in {"get-first-candles", "get-candles"}:
                bootstrap_sent = bootstrap_sent or result.sent
            if not result.sent:
                current = status()
                return NativeBootstrapResult(
                    subscribe_sent=subscribe_sent,
                    bootstrap_sent=bootstrap_sent,
                    bootstrap_complete=current.bootstrap_complete,
                    bootstrap_ready=current.bootstrap_ready,
                    chart_count=current.chart_count,
                    session_context=current.session_context,
                    error_code=result.error_code or "NATIVE_BOOTSTRAP_SEND_FAILED",
                )
            await asyncio.sleep(self._request_spacing_seconds)

        current = await self._wait_for_ready(status=status, timeout_seconds=timeout_seconds)
        return NativeBootstrapResult(
            subscribe_sent=subscribe_sent,
            bootstrap_sent=bootstrap_sent,
            bootstrap_complete=current.bootstrap_complete,
            bootstrap_ready=current.bootstrap_ready,
            chart_count=current.chart_count,
            session_context=current.session_context,
            error_code=None if current.bootstrap_ready else "BOOTSTRAP_WAIT_TIMEOUT",
        )

    def observe_response(self, message: dict[str, Any], *, status: NativeBootstrapStatus, now_ms: int | None = None) -> None:
        if _event_name(message) not in {"first-candles", "candles"}:
            return
        if self._active_context is None:
            return
        active_id, raw_size = self._active_context
        response_active_id = _find_first_int(message, {"active_id", "activeId"})
        response_raw_size = _find_first_int(message, {"size", "raw_size", "rawSize"})
        if response_active_id is not None and response_active_id != active_id:
            return
        if response_raw_size is not None and response_raw_size != raw_size:
            return
        if _event_name(message) == "first-candles":
            self._first_response_seen.set()
        self._report.record_response(
            message=message,
            status=status,
            started_at_ms=self._last_started_at_ms,
            now_ms=now_ms or _epoch_ms(),
        )

    async def _send_step(
        self,
        *,
        step: NativeBootstrapStep,
        send: Callable[[dict[str, Any]], Awaitable[NativeBootstrapSendResult]],
        status: Callable[[], NativeBootstrapStatus],
    ) -> NativeBootstrapSendResult:
        self._guard.validate_outbound(step.payload)
        result = await send(step.payload)
        self._report.record_request(
            step=step,
            sent=result.sent,
            status=status(),
            started_at_ms=self._last_started_at_ms,
            now_ms=_epoch_ms(),
            error_code=result.error_code,
        )
        return result

    async def _wait_for_first_response(self, *, timeout_seconds: float) -> bool:
        try:
            await asyncio.wait_for(self._first_response_seen.wait(), timeout=timeout_seconds)
            return True
        except asyncio.TimeoutError:
            return False

    async def _wait_for_ready(self, *, status: Callable[[], NativeBootstrapStatus], timeout_seconds: float) -> NativeBootstrapStatus:
        deadline = time.time() + max(0.0, timeout_seconds)
        current = status()
        while time.time() < deadline:
            current = status()
            if current.bootstrap_ready:
                return current
            await asyncio.sleep(0.1)
        return status()

    def _build_steps(self, *, active_id: int, raw_size: int) -> tuple[NativeBootstrapStep, ...]:
        return (
            NativeBootstrapStep(order=1, kind="subscribe", payload=self._subscription_factory.subscribe_candles_generated(active_id)),
            NativeBootstrapStep(order=2, kind="get-first-candles", payload=_history_payload("get-first-candles", active_id, raw_size, 1)),
            NativeBootstrapStep(order=3, kind="get-first-candles", payload=_history_payload("get-first-candles", active_id, raw_size, 2)),
            NativeBootstrapStep(order=4, kind="get-candles", payload=_history_payload("get-candles", active_id, raw_size, 1)),
            NativeBootstrapStep(order=5, kind="get-candles", payload=_history_payload("get-candles", active_id, raw_size, 2)),
            NativeBootstrapStep(order=6, kind="get-candles", payload=_history_payload("get-candles", active_id, raw_size, 3)),
        )


def _history_payload(name: str, active_id: int, raw_size: int, index: int) -> dict[str, Any]:
    return {
        "name": "sendMessage",
        "request_id": f"friday_native_{name.replace('-', '_')}_{active_id}_{raw_size}_{_epoch_ms()}_{index}",
        "msg": {
            "name": name,
            "body": {"active_id": active_id, "size": raw_size},
        },
    }


def _history_count(context: dict[str, Any]) -> int:
    return _as_int(context.get("history_count")) or 0


def _history_required(context: dict[str, Any]) -> int:
    return _as_int(context.get("history_required")) or 0


def _history_state(context: dict[str, Any]) -> str | None:
    value = context.get("history_state")
    return value if isinstance(value, str) else None


def _event_name(message: dict[str, Any]) -> str | None:
    value = message.get("name")
    return value if isinstance(value, str) else None


def _inner_name(message: dict[str, Any]) -> str | None:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return None
    value = msg.get("name")
    return value if isinstance(value, str) else None


def _request_id(message: dict[str, Any]) -> str | None:
    value = message.get("request_id") or message.get("requestId")
    return value if isinstance(value, str) and value else None


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


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _epoch_ms() -> int:
    return int(time.time() * 1000)


def _render_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Native Bootstrap Sequence", ""]
    summary = payload.get("summary", {})
    lines.append(f"total_entries: {summary.get('total_entries', 0)}")
    lines.append(f"requests: {summary.get('requests', 0)}")
    lines.append(f"responses: {summary.get('responses', 0)}")
    lines.append(f"last_readiness: {summary.get('last_readiness')}")
    lines.append(f"last_history_count: {summary.get('last_history_count', 0)}")
    lines.append(f"bootstrap_complete: {summary.get('bootstrap_complete', False)}")
    lines.append("")
    for entry in payload.get("entries", []):
        lines.append(
            f"{entry.get('step')}. {entry.get('phase')} name={entry.get('name')} inner={entry.get('inner_name')} "
            f"request_id={entry.get('request_id')} active_id={entry.get('active_id')} raw_size={entry.get('raw_size')} "
            f"sent={entry.get('sent')} response={entry.get('response_type')} history={entry.get('history_count')}/{entry.get('history_required')} "
            f"readiness={entry.get('readiness')} complete={entry.get('bootstrap_complete')} chart_count={entry.get('chart_count')} "
            f"elapsed_ms={entry.get('elapsed_ms')} error={entry.get('error_code')}"
        )
    lines.append("")
    return "\n".join(lines)
