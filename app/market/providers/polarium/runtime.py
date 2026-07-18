from __future__ import annotations

import time
from dataclasses import dataclass, replace
from typing import Any, Literal

from app.market.providers.polarium.asset_switch_diagnostic import AssetSwitchDiagnostic
from app.market.providers.polarium.bootstrap_diagnostic import HistoricalBootstrapDiagnostic
from app.market.providers.polarium.bootstrap_payload_trace import BootstrapPayloadTraceDiagnostic
from app.market.providers.polarium.history_count_diagnostic import HistoryCountDiagnostic
from app.market.providers.polarium.instrument_metadata import PolariumInstrumentMetadataMap
from app.market.providers.polarium.market_feed import PolariumMarketFeed
from app.market.providers.polarium.market_router import PolariumMarketRouter
from app.market.providers.polarium.market_socket import PolariumMarketSocketDiscovery
from app.market.providers.polarium.market_store_adapter import PolariumCandleStoreAdapter
from app.market.providers.polarium.market_subscription import PolariumMarketSubscriptionFactory
from app.market.providers.polarium.models import PolariumMarketFeedResult, PolariumRuntimeStatus
from app.market.providers.polarium.parser import PolariumMarketEventParseError, PolariumMarketFeedParser
from app.market.providers.polarium.readiness import HISTORY_EVENTS, REALTIME_EVENTS, PolariumReadinessConfig, PolariumReadinessTracker
from app.market.providers.polarium.runtime_guard import PolariumRuntimeGuard, PolariumRuntimeGuardViolation
from app.market.providers.polarium.session_context_audit import SessionContextAudit, SessionContextAuditOrigin
from app.market.providers.polarium.session_context import PolariumSessionContext, build_polarium_session_context
from app.market.store import CandleStore
from app.market.store.types import CandleSeriesKey

PolariumMessageOrigin = Literal["PAGE_NATIVE", "SERVER_INBOUND", "FRIDAY_PROBE"]


@dataclass
class _BootstrapRequest:
    active_id: int
    raw_size: int | None
    request_id: str | None
    requested_at: int
    attempts: int = 1
    completed_at: int | None = None


@dataclass
class _BootstrapDiagnostics:
    state: str = "NO_HISTORY"
    request_sent: bool = False
    request_id_present: bool = False
    response_received: bool = False
    response_type: str | None = None
    received_count: int = 0
    valid_count: int = 0
    inserted_count: int = 0
    duplicate_count: int = 0
    history_count: int = 0
    last_error: str | None = None
    bootstrap_requested_at: int | None = None
    bootstrap_request_id: str | None = None
    bootstrap_attempts: int = 0
    bootstrap_completed_at: int | None = None
    pending_bootstrap_requests: int = 0
    matched_bootstrap_responses: int = 0
    unmatched_bootstrap_responses: int = 0
    expired_bootstrap_requests: int = 0

    def sanitized(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "request_sent": self.request_sent,
            "request_id_present": self.request_id_present,
            "response_received": self.response_received,
            "response_type": self.response_type,
            "received_count": self.received_count,
            "valid_count": self.valid_count,
            "inserted_count": self.inserted_count,
            "duplicate_count": self.duplicate_count,
            "history_count": self.history_count,
            "last_error": self.last_error,
            "bootstrap_requested_at": self.bootstrap_requested_at,
            "bootstrap_request_id": self.bootstrap_request_id,
            "bootstrap_attempts": self.bootstrap_attempts,
            "bootstrap_completed_at": self.bootstrap_completed_at,
            "pending_bootstrap_requests": self.pending_bootstrap_requests,
            "matched_bootstrap_responses": self.matched_bootstrap_responses,
            "unmatched_bootstrap_responses": self.unmatched_bootstrap_responses,
            "expired_bootstrap_requests": self.expired_bootstrap_requests,
        }


class PolariumMarketFeedRuntime:
    """Official read-only Polarium market feed runtime.

    The runtime consumes already-authorized market WebSocket messages and writes
    only normalized market candles to the shared CandleStore.
    """

    def __init__(
        self,
        candle_store: CandleStore,
        *,
        guard: PolariumRuntimeGuard | None = None,
        parser: PolariumMarketFeedParser | None = None,
        socket_discovery: PolariumMarketSocketDiscovery | None = None,
        subscription_factory: PolariumMarketSubscriptionFactory | None = None,
        instrument_metadata: PolariumInstrumentMetadataMap | None = None,
        readiness_config: PolariumReadinessConfig | None = None,
        bootstrap_diagnostic: HistoricalBootstrapDiagnostic | None = None,
        bootstrap_payload_trace: BootstrapPayloadTraceDiagnostic | None = None,
        history_count_diagnostic: HistoryCountDiagnostic | None = None,
        asset_switch_diagnostic: AssetSwitchDiagnostic | None = None,
        session_context_audit: SessionContextAudit | None = None,
    ) -> None:
        self._guard = guard or PolariumRuntimeGuard()
        self._parser = parser or PolariumMarketFeedParser()
        self._socket_discovery = socket_discovery or PolariumMarketSocketDiscovery()
        self._subscription_factory = subscription_factory or PolariumMarketSubscriptionFactory()
        self._instrument_metadata = instrument_metadata or PolariumInstrumentMetadataMap()
        self._readiness = PolariumReadinessTracker(readiness_config)
        self._candle_store = candle_store
        self._feed = PolariumMarketFeed(PolariumMarketRouter(PolariumCandleStoreAdapter(candle_store)))
        self._subscriptions: set[int] = set()
        self._received = 0
        self._processed = 0
        self._dropped = 0
        self._forbidden = 0
        self._latest_active_id: int | None = None
        self._latest_symbol: str | None = None
        self._latest_raw_sizes: tuple[int, ...] = ()
        self._background_contexts: dict[int, set[int]] = {}
        self._visible_active_id: int | None = None
        self._visible_symbol: str | None = None
        self._visible_raw_size: int | None = None
        self._visible_latest_price: float | None = None
        self._visible_latest_update: int | None = None
        self._visible_status = "OFFLINE"
        self._latest_raw_size: int | None = None
        self._latest_price: float | None = None
        self._latest_update: int | None = None
        self._history_timestamps: dict[tuple[int, int], set[int]] = {}
        self._bootstrap_pending: dict[str, _BootstrapRequest] = {}
        self._bootstrap_latest: _BootstrapRequest | None = None
        self._bootstrap_diagnostics = _BootstrapDiagnostics()
        self._bootstrap_diagnostic = bootstrap_diagnostic or HistoricalBootstrapDiagnostic()
        self._bootstrap_payload_trace = bootstrap_payload_trace or BootstrapPayloadTraceDiagnostic()
        self._history_count_diagnostic = history_count_diagnostic or HistoryCountDiagnostic()
        self._asset_switch_diagnostic = asset_switch_diagnostic or AssetSwitchDiagnostic()
        self._session_context_audit = session_context_audit or SessionContextAudit()
        self._session_context = PolariumSessionContext.disconnected()

    @property
    def feed(self) -> PolariumMarketFeed:
        return self._feed

    @property
    def socket_discovery(self) -> PolariumMarketSocketDiscovery:
        return self._socket_discovery

    def subscribe_payload(self, active_id: int) -> dict:
        payload = self._subscription_factory.subscribe_candles_generated(active_id)
        self._guard.validate_outbound(payload)
        self._subscriptions.add(active_id)
        return payload

    def unsubscribe_payload(self, active_id: int) -> dict:
        payload = self._subscription_factory.unsubscribe_candles_generated(active_id)
        self._guard.validate_outbound(payload)
        self._subscriptions.discard(active_id)
        return payload

    def bootstrap_payload(self, active_id: int, raw_size: int) -> dict:
        payload = {
            "name": "sendMessage",
            "request_id": f"friday_bootstrap_get_first_candles_{active_id}_{raw_size}_{int(time.time() * 1000)}",
            "msg": {
                "name": "get-first-candles",
                "body": {"active_id": active_id, "size": raw_size},
            },
        }
        self._guard.validate_outbound(payload)
        self._readiness.start_bootstrap(active_id, raw_size, now_ms=_epoch_ms())
        self._record_bootstrap_request(active_id=active_id, raw_size=raw_size, request_id=_request_id(payload), now_ms=_epoch_ms(), request_sent=False)
        self._update_session_context(self._build_session_context(), origin="HISTORICAL_BOOTSTRAP", reason="BOOTSTRAP_PAYLOAD_CREATED", now_ms=_epoch_ms())
        return payload

    def record_bootstrap_payload(self, payload: dict[str, Any], *, request_sent: bool, now_ms: int | None = None) -> None:
        visible = _visible_context_from_page_native(payload)
        if visible is None:
            return
        active_id, raw_size = visible
        if raw_size is None:
            return
        self._readiness.start_bootstrap(active_id, raw_size, now_ms=now_ms or _epoch_ms())
        self._record_bootstrap_request(active_id=active_id, raw_size=raw_size, request_id=_request_id(payload), now_ms=now_ms or _epoch_ms(), request_sent=request_sent)
        self._update_session_context(self._build_session_context(), origin="PAGE_NATIVE", reason="BOOTSTRAP_PAYLOAD_OBSERVED", now_ms=now_ms or _epoch_ms())

    def process_message(
        self,
        message: dict[str, Any],
        *,
        now_ms: int | None = None,
        origin: PolariumMessageOrigin = "SERVER_INBOUND",
    ) -> PolariumMarketFeedResult:
        observed_now = now_ms or _epoch_ms()
        self._received += 1
        if origin == "PAGE_NATIVE":
            self._observe_visible_context(message, now_ms=observed_now)
        decision = self._guard.classify_inbound(message)
        if decision == "forbidden":
            self._forbidden += 1
            return PolariumMarketFeedResult(status="dropped", event_name=_event_name(message), active_id=None, dropped_reason="FORBIDDEN_INBOUND")
        self._instrument_metadata.observe(message)
        if decision == "drop":
            self._dropped += 1
            return PolariumMarketFeedResult(status="dropped", event_name=_event_name(message), active_id=None, dropped_reason="UNSUPPORTED_INBOUND")
        parse_defaults = self._bootstrap_defaults_for(message)
        context_before = self._session_context.sanitized()
        history_before = self._history_count_for(
            active_id=parse_defaults.active_id if parse_defaults else _find_active_id(message) or self._visible_active_id,
            raw_size=parse_defaults.raw_size if parse_defaults else _find_raw_size(message) or self._visible_raw_size,
        )
        bucket_before_by_context: dict[tuple[int, int], int] = {}
        history_before_by_context: dict[tuple[int, int], int] = {}
        readiness_before_by_context: dict[tuple[int, int], dict[str, Any]] = {}
        try:
            event = self._parser.parse(
                message,
                default_active_id=parse_defaults.active_id if parse_defaults else None,
                default_raw_size=parse_defaults.raw_size if parse_defaults else None,
            )
        except PolariumMarketEventParseError as exc:
            self._dropped += 1
            self._record_bootstrap_parse_error(message, str(exc))
            requested_active_id = parse_defaults.active_id if parse_defaults else _find_active_id(message) or self._visible_active_id
            requested_raw_size = parse_defaults.raw_size if parse_defaults else _find_raw_size(message) or self._visible_raw_size
            self._bootstrap_payload_trace.observe_parse_error(
                message=message,
                error=str(exc),
                request_id=_request_id(message),
                requested_active_id=requested_active_id,
                requested_raw_size=requested_raw_size,
                bucket_before=self._bucket_size(active_id=requested_active_id, raw_size=requested_raw_size),
                history_before=history_before,
                readiness_before=_readiness_state(context_before),
                now_ms=observed_now,
            )
            self._bootstrap_diagnostic.observe_parse_error(
                message=message,
                error=str(exc),
                request_id=_request_id(message),
                requested_active_id=requested_active_id,
                requested_raw_size=requested_raw_size,
                session_context=context_before,
                history_count_before=history_before,
                now_ms=observed_now,
            )
            return PolariumMarketFeedResult(status="invalid", event_name=_event_name(message), active_id=None, dropped_reason=str(exc))
        event = self._enrich_symbol(event)
        if event.event_name in HISTORY_EVENTS:
            bucket_before_by_context = self._bucket_sizes_for_event(event)
            history_before_by_context = self._history_counts_for_event(event)
            readiness_before_by_context = self._readiness_snapshots_for_event(event, now_ms=observed_now)
        result = self._feed.consume(event, now_ms=observed_now)
        self._processed += result.processed
        if result.status == "processed" and result.processed > 0:
            self._latest_active_id = event.active_id
            self._latest_symbol = event.symbol
            self._latest_raw_sizes = tuple(sorted({candle.raw_size for candle in event.candles}))
            self._latest_raw_size = self._latest_raw_sizes[0] if self._latest_raw_sizes else None
            self._latest_price = event.value if event.value is not None else event.candles[-1].close
            self._latest_update = observed_now
            self._record_background_context(event.active_id, self._latest_raw_sizes)
            self._record_readiness(event, now_ms=self._latest_update)
            self._record_bootstrap_response(message=message, event=event, result=result, now_ms=self._latest_update)
            if self._visible_active_id == event.active_id and (self._visible_raw_size is None or self._visible_raw_size in self._latest_raw_sizes):
                if self._visible_symbol is None:
                    self._visible_symbol = event.symbol
                visible_candle = _visible_candle(event.candles, self._visible_raw_size)
                if visible_candle is not None:
                    self._visible_latest_price = visible_candle.close
                    self._visible_latest_update = self._latest_update
                self._visible_status = "READY"
            self._update_session_context(self._build_session_context(), origin="MARKET_WS", reason=f"{event.event_name}_PROCESSED", now_ms=self._latest_update)
            if event.event_name in HISTORY_EVENTS:
                raw_size = parse_defaults.raw_size if parse_defaults else self._visible_raw_size
                self._bootstrap_payload_trace.observe_success(
                    message=message,
                    event=event,
                    store_results=result.store_results,
                    request_id=_request_id(message),
                    requested_active_id=parse_defaults.active_id if parse_defaults else _find_active_id(message) or self._visible_active_id,
                    requested_raw_size=raw_size,
                    bucket_before=bucket_before_by_context.get((event.active_id, raw_size), 0),
                    bucket_after=self._bucket_size(active_id=event.active_id, raw_size=raw_size),
                    history_before=history_before_by_context.get((event.active_id, raw_size), 0),
                    history_after=self._history_count_for(active_id=event.active_id, raw_size=raw_size),
                    readiness_before=_readiness_state(readiness_before_by_context.get((event.active_id, raw_size))),
                    readiness_after=self._readiness.snapshot(event.active_id, raw_size, now_ms=self._latest_update).state if raw_size is not None else None,
                    now_ms=self._latest_update,
                )
                self._asset_switch_diagnostic.observe_bootstrap_finished(
                    active_id=event.active_id,
                    raw_size=raw_size,
                    symbol=event.symbol,
                    visible_active_id=self._visible_active_id,
                    visible_raw_size=self._visible_raw_size,
                    bucket_size_before=bucket_before_by_context.get((event.active_id, raw_size), 0),
                    bucket_size_after=self._bucket_size(active_id=event.active_id, raw_size=raw_size),
                    history_count=self._history_count_for(active_id=event.active_id, raw_size=raw_size),
                    readiness_state=self._readiness.snapshot(event.active_id, raw_size, now_ms=self._latest_update).state if raw_size is not None else None,
                    now_ms=self._latest_update,
                )
                self._history_count_diagnostic.observe_history_event(
                    event=event,
                    store_results=result.store_results,
                    bucket_before=bucket_before_by_context,
                    bucket_after=self._bucket_sizes_for_event(event),
                    history_before=history_before_by_context,
                    history_after=self._history_counts_for_event(event),
                    readiness_before=readiness_before_by_context,
                    readiness_after=self._readiness_snapshots_for_event(event, now_ms=self._latest_update),
                    now_ms=self._latest_update,
                )
                self._bootstrap_diagnostic.observe_response(
                    message=message,
                    event=event,
                    result=result,
                    request_id=_request_id(message),
                    requested_active_id=parse_defaults.active_id if parse_defaults else _find_active_id(message) or self._visible_active_id,
                    requested_raw_size=raw_size,
                    session_context_before=context_before,
                    session_context_after=self._session_context.sanitized(),
                    history_count_before=history_before,
                    history_count_after=self._history_count_for(active_id=event.active_id, raw_size=raw_size),
                    now_ms=self._latest_update,
                )
            elif event.event_name in REALTIME_EVENTS:
                for candle in event.candles:
                    self._bootstrap_diagnostic.observe_realtime(
                        active_id=event.active_id,
                        raw_size=candle.raw_size,
                        session_context=self._session_context.sanitized(),
                        now_ms=self._latest_update,
                    )
        return result

    def _enrich_symbol(self, event) -> Any:
        symbol = event.symbol or self._instrument_metadata.symbol_for(event.active_id)
        if symbol == event.symbol:
            return event
        return replace(event, symbol=symbol, candles=tuple(replace(candle, symbol=symbol) for candle in event.candles))

    def _observe_visible_context(self, message: dict[str, Any], *, now_ms: int | None = None) -> None:
        visible = _visible_context_from_page_native(message)
        if visible is None:
            return
        active_id, raw_size = visible
        if raw_size is None:
            return
        observed_now = now_ms or _epoch_ms()
        previous_context = self._session_context.sanitized()
        previous = (self._visible_active_id, self._visible_raw_size)
        current = (active_id, raw_size)
        previous_bucket_size = self._bucket_size(active_id=previous[0], raw_size=previous[1])
        if previous != current:
            self._visible_status = "SYNCING"
            self._visible_latest_price = None
            self._visible_latest_update = None
            self._readiness.start_bootstrap(active_id, raw_size, now_ms=observed_now)
        self._visible_active_id = active_id
        self._visible_raw_size = raw_size
        self._visible_symbol = self._instrument_metadata.symbol_for(active_id)
        self._update_session_context(self._build_session_context(), origin="PAGE_NATIVE", reason="VISIBLE_CONTEXT_OBSERVED", now_ms=observed_now)
        if previous != current:
            self._asset_switch_diagnostic.observe_selection(
                previous_context=previous_context,
                current_context=self._session_context.sanitized(),
                bucket_size_before=previous_bucket_size,
                bucket_size_after=self._bucket_size(active_id=active_id, raw_size=raw_size),
                now_ms=observed_now,
            )
        if _event_name(message) == "sendMessage" and _inner_name(message) == "get-first-candles":
            self._record_bootstrap_request(active_id=active_id, raw_size=raw_size, request_id=_request_id(message), now_ms=observed_now, request_sent=True)

    def _record_bootstrap_request(self, *, active_id: int, raw_size: int | None, request_id: str | None, now_ms: int, request_sent: bool) -> None:
        key = request_id or f"visible:{active_id}:{raw_size}"
        current = self._bootstrap_pending.get(key)
        if current is None:
            current = _BootstrapRequest(active_id=active_id, raw_size=raw_size, request_id=request_id, requested_at=now_ms)
            self._bootstrap_pending[key] = current
        else:
            current.attempts += 1
        self._bootstrap_latest = current
        self._bootstrap_diagnostics.state = "BOOTSTRAPPING"
        self._bootstrap_diagnostics.request_sent = self._bootstrap_diagnostics.request_sent or request_sent
        self._bootstrap_diagnostics.request_id_present = request_id is not None
        self._bootstrap_diagnostics.bootstrap_requested_at = current.requested_at
        self._bootstrap_diagnostics.bootstrap_request_id = request_id
        self._bootstrap_diagnostics.bootstrap_attempts = current.attempts
        self._bootstrap_diagnostics.pending_bootstrap_requests = len(self._bootstrap_pending)
        self._bootstrap_diagnostics.last_error = None
        self._bootstrap_diagnostic.observe_request(
            active_id=active_id,
            raw_size=raw_size,
            request_id=request_id,
            request_sent=request_sent,
            session_context=self._build_session_context().sanitized(),
            now_ms=now_ms,
        )
        self._asset_switch_diagnostic.observe_bootstrap_started(active_id=active_id, raw_size=raw_size, now_ms=now_ms)

    def _bootstrap_defaults_for(self, message: dict[str, Any]) -> _BootstrapRequest | None:
        if _event_name(message) not in HISTORY_EVENTS:
            return None
        request_id = _request_id(message)
        if request_id is not None and request_id in self._bootstrap_pending:
            return self._bootstrap_pending[request_id]
        active_id = _find_active_id(message)
        raw_size = _find_raw_size(message)
        if active_id is not None:
            compatible = [
                request
                for request in self._bootstrap_pending.values()
                if request.active_id == active_id and (raw_size is None or request.raw_size == raw_size)
            ]
            if raw_size is not None and compatible:
                return compatible[0]
            if raw_size is None and len(compatible) == 1:
                return compatible[0]
        if len(self._bootstrap_pending) == 1:
            return next(iter(self._bootstrap_pending.values()))
        if self._bootstrap_latest and self._bootstrap_latest.active_id == self._visible_active_id and self._bootstrap_latest.raw_size == self._visible_raw_size:
            return self._bootstrap_latest
        return None

    def _record_bootstrap_parse_error(self, message: dict[str, Any], error: str) -> None:
        if _event_name(message) not in HISTORY_EVENTS:
            return
        self._bootstrap_diagnostics.response_received = True
        self._bootstrap_diagnostics.response_type = _event_name(message)
        self._bootstrap_diagnostics.last_error = error
        self._bootstrap_diagnostics.unmatched_bootstrap_responses += 1

    def _record_bootstrap_response(self, *, message: dict[str, Any], event, result: PolariumMarketFeedResult, now_ms: int) -> None:
        if event.event_name not in HISTORY_EVENTS:
            return
        request = self._bootstrap_defaults_for(message)
        raw_size = request.raw_size if request else self._visible_raw_size
        received_count = _history_candle_count(message, raw_size)
        valid_count = sum(1 for candle in event.candles if raw_size is None or candle.raw_size == raw_size)
        inserted_count = sum(1 for item in result.store_results if item.status in {"added", "updated"})
        duplicate_count = sum(1 for item in result.store_results if item.status == "ignored")
        if request is not None:
            request.completed_at = now_ms
            key = request.request_id or f"visible:{request.active_id}:{request.raw_size}"
            self._bootstrap_pending.pop(key, None)
            self._bootstrap_diagnostics.matched_bootstrap_responses += 1
        else:
            self._bootstrap_diagnostics.unmatched_bootstrap_responses += 1
        if raw_size is not None:
            history_count = len(self._history_timestamps.get((event.active_id, raw_size), set()))
        else:
            history_count = sum(len(values) for (active_id, _), values in self._history_timestamps.items() if active_id == event.active_id)
        self._bootstrap_diagnostics.state = "READY" if history_count >= self._readiness.config.ready_candles else "LIMITED" if history_count > 0 else "NO_HISTORY"
        self._bootstrap_diagnostics.response_received = True
        self._bootstrap_diagnostics.response_type = event.event_name
        self._bootstrap_diagnostics.received_count = received_count
        self._bootstrap_diagnostics.valid_count = valid_count
        self._bootstrap_diagnostics.inserted_count = inserted_count
        self._bootstrap_diagnostics.duplicate_count = duplicate_count
        self._bootstrap_diagnostics.history_count = history_count
        self._bootstrap_diagnostics.bootstrap_completed_at = now_ms
        self._bootstrap_diagnostics.pending_bootstrap_requests = len(self._bootstrap_pending)
        self._bootstrap_diagnostics.last_error = None

    def _record_background_context(self, active_id: int, raw_sizes: tuple[int, ...]) -> None:
        if active_id not in self._background_contexts:
            self._background_contexts[active_id] = set()
        self._background_contexts[active_id].update(raw_sizes)

    def _record_readiness(self, event, *, now_ms: int) -> None:
        for candle in event.candles:
            key = (event.active_id, candle.raw_size)
            if event.event_name in HISTORY_EVENTS:
                timestamps = self._history_timestamps.setdefault(key, set())
                timestamps.add(candle.start_timestamp)
                self._readiness.record_history(event.active_id, candle.raw_size, len(timestamps), now_ms=now_ms)
            elif event.event_name in REALTIME_EVENTS:
                self._readiness.record_realtime(event.active_id, candle.raw_size, now_ms=now_ms)

    def _history_count_for(self, *, active_id: int | None, raw_size: int | None) -> int:
        if active_id is None:
            return 0
        if raw_size is not None:
            return len(self._history_timestamps.get((active_id, raw_size), set()))
        return sum(len(values) for (stored_active_id, _), values in self._history_timestamps.items() if stored_active_id == active_id)

    def _bucket_sizes_for_event(self, event) -> dict[tuple[int, int], int]:
        sizes: dict[tuple[int, int], int] = {}
        for candle in event.candles:
            key = (event.active_id, candle.raw_size)
            sizes[key] = self._bucket_size(active_id=event.active_id, raw_size=candle.raw_size)
        return sizes

    def _bucket_size(self, *, active_id: int | None, raw_size: int | None) -> int:
        if active_id is None or raw_size is None:
            return 0
        series_key = CandleSeriesKey(provider="POLARIUM", active_id=active_id, raw_size=raw_size)
        return len(self._candle_store.series_by_key(series_key))

    def _history_counts_for_event(self, event) -> dict[tuple[int, int], int]:
        return {(event.active_id, candle.raw_size): self._history_count_for(active_id=event.active_id, raw_size=candle.raw_size) for candle in event.candles}

    def _readiness_snapshots_for_event(self, event, *, now_ms: int) -> dict[tuple[int, int], dict[str, Any]]:
        snapshots: dict[tuple[int, int], dict[str, Any]] = {}
        for candle in event.candles:
            snapshots[(event.active_id, candle.raw_size)] = self._readiness.snapshot(event.active_id, candle.raw_size, now_ms=now_ms).sanitized()
        return snapshots

    def status(self) -> PolariumRuntimeStatus:
        market_socket = self._socket_discovery.market_socket
        if self._latest_active_id is None:
            self._update_session_context(self._build_session_context(), origin="DEFAULT_CONTEXT", reason="STATUS_REFRESH_WITHOUT_MARKET_EVENT", now_ms=_epoch_ms())
        return PolariumRuntimeStatus(
            read_only=True,
            connected=bool(market_socket and market_socket.active),
            authenticated=bool(market_socket and market_socket.authenticated),
            market_socket_ready=bool(market_socket and market_socket.ready),
            subscriptions=tuple(sorted(self._subscriptions)),
            received=self._received,
            processed=self._processed,
            dropped=self._dropped,
            forbidden=self._forbidden,
            reconnects=self._socket_discovery.reconnects,
            latest_active_id=self._latest_active_id,
            latest_symbol=self._latest_symbol,
            latest_raw_sizes=self._latest_raw_sizes,
            session_context=self._session_context.sanitized(),
            bootstrap=self._bootstrap_diagnostics.sanitized(),
        )

    def observe_cdp_context_event(
        self,
        message: dict[str, Any],
        *,
        origin: SessionContextAuditOrigin,
        frame: str | None,
        request_id: str | None,
        websocket: str | None,
        target_id: str | None,
        now_ms: int | None = None,
    ) -> None:
        self._session_context_audit.observe_cdp_context_event(
            message=message,
            origin=origin,
            frame=frame,
            request_id=request_id,
            websocket=websocket,
            target_id=target_id,
            now_ms=now_ms or _epoch_ms(),
            buckets=self._bucket_labels(),
        )

    def _build_session_context(self) -> PolariumSessionContext:
        market_socket = self._socket_discovery.market_socket
        websocket_state = "ONLINE" if market_socket and market_socket.active and market_socket.ready else "DISCONNECTED"
        readiness = self._readiness.snapshot(self._visible_active_id, self._visible_raw_size, now_ms=_readiness_now(self._visible_latest_update)).sanitized()
        return build_polarium_session_context(
            websocket_state=websocket_state,
            authenticated=bool(market_socket and market_socket.authenticated),
            active_id=self._visible_active_id,
            symbol=self._visible_symbol,
            raw_size=self._visible_raw_size,
            latest_price=self._visible_latest_price,
            last_update=self._visible_latest_update,
            feed_status=str(readiness["state"]) if self._visible_active_id is not None else "OFFLINE",
            latest_market_event_active_id=self._latest_active_id,
            latest_market_event_raw_sizes=self._latest_raw_sizes,
            available_raw_sizes=tuple(sorted(self._background_contexts.get(self._visible_active_id, set()))),
            background_market_contexts=tuple(
                {"active_id": active_id, "raw_sizes": sorted(raw_sizes)}
                for active_id, raw_sizes in sorted(self._background_contexts.items())
            ),
            history=readiness,
        )

    def _update_session_context(
        self,
        next_context: PolariumSessionContext,
        *,
        origin: SessionContextAuditOrigin,
        reason: str,
        now_ms: int,
    ) -> None:
        previous = self._session_context
        self._session_context = next_context
        active_id = next_context.active_id
        raw_size = next_context.raw_size
        self._session_context_audit.observe_update(
            old_context=previous.sanitized(),
            new_context=next_context.sanitized(),
            origin=origin,
            reason=reason,
            now_ms=now_ms,
            buckets=self._bucket_labels(),
            bucket_exists=self._bucket_size(active_id=active_id, raw_size=raw_size) > 0 if active_id is not None and raw_size is not None else False,
        )

    def _bucket_labels(self) -> tuple[str, ...]:
        return tuple(
            f"{key.provider}:{key.active_id}:{key.raw_size}"
            for key in self._candle_store.series_keys()
            if key.provider == "POLARIUM"
        )


def _event_name(message: dict[str, Any]) -> str | None:
    value = message.get("name")
    return value if isinstance(value, str) else None


def _request_id(message: dict[str, Any]) -> str | None:
    value = message.get("request_id") or message.get("requestId")
    if isinstance(value, str) and value:
        return value
    msg = message.get("msg")
    if isinstance(msg, dict):
        nested = msg.get("request_id") or msg.get("requestId")
        if isinstance(nested, str) and nested:
            return nested
    return None


def _epoch_ms() -> int:
    return int(time.time() * 1000)


def _visible_context_from_page_native(message: dict[str, Any]) -> tuple[int, int | None] | None:
    name = _event_name(message)
    inner = _inner_name(message)
    body = _body(message)
    routing_filters = _routing_filters(message)
    if name == "sendMessage" and inner == "get-first-candles":
        active_id = _as_int(body.get("active_id")) or _as_int(routing_filters.get("active_id"))
        raw_size = _as_int(body.get("size")) or _as_int(body.get("raw_size")) or _as_int(routing_filters.get("size"))
        return (active_id, raw_size) if active_id is not None else None
    if name == "subscribeMessage" and inner in {"candle-generated", "candles-generated"}:
        active_id = _as_int(routing_filters.get("active_id"))
        raw_size = _as_int(routing_filters.get("size"))
        return (active_id, raw_size) if active_id is not None else None
    return None


def _inner_name(message: dict[str, Any]) -> str | None:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return None
    value = msg.get("name")
    return value if isinstance(value, str) else None


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


def _find_active_id(value: Any) -> int | None:
    return _find_first_int(value, {"active_id", "activeId"})


def _find_raw_size(value: Any) -> int | None:
    return _find_first_int(value, {"size", "raw_size", "rawSize"})


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


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


def _history_candle_count(message: dict[str, Any], raw_size: int | None) -> int:
    body = _history_body(message)
    raw_list = body.get("candles")
    if isinstance(raw_list, list):
        return sum(1 for item in raw_list if isinstance(item, dict) and (raw_size is None or _as_int(item.get("size")) in {None, raw_size}))
    candles_by_size = body.get("candles_by_size") or body.get("candles")
    if not isinstance(candles_by_size, dict) and any((body.get(str(size)) or body.get(size)) for size in (60, 300, 900)):
        candles_by_size = body
    if isinstance(candles_by_size, dict):
        if raw_size is not None:
            return 1 if isinstance(candles_by_size.get(str(raw_size)) or candles_by_size.get(raw_size), dict) else 0
        return sum(1 for item in candles_by_size.values() if isinstance(item, dict))
    return 0


def _history_body(message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return message if isinstance(message, dict) else {}
    for key in ("body", "result", "data"):
        value = msg.get(key)
        if isinstance(value, dict):
            return value
    if any(key in msg for key in ("candles", "candles_by_size", "active_id")):
        return msg
    return {}


def _visible_candle(candles: tuple, raw_size: int | None) -> Any | None:
    if raw_size is None:
        return candles[-1] if candles else None
    for candle in reversed(candles):
        if candle.raw_size == raw_size:
            return candle
    return None


def _readiness_now(last_update: int | None) -> int:
    if last_update is not None and last_update < 1_000_000_000_000:
        return last_update
    return _epoch_ms()


def _readiness_state(snapshot: dict[str, Any] | None) -> str | None:
    value = (snapshot or {}).get("history_state") or (snapshot or {}).get("state")
    return value if isinstance(value, str) else None
