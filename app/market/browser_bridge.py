from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.market.browser_bridge_payload_adapter import adapt_browser_bridge_payload
from app.market.pipeline import MarketPipeline
from app.market.pipeline.models import PipelineResult

POLARIUM_AUTHORIZED_BROWSER_SOURCE = "POLARIUM_AUTHORIZED_BROWSER"
POLARIUM_AUTHORIZED_BROWSER_LABEL = "POLARIUM AUTHORIZED BROWSER LIVE"

ALLOWED_BROWSER_BRIDGE_EVENTS = frozenset(
    {
        "first-candles",
        "candle-generated",
        "candles-generated",
        "timeSync",
    }
)

PIPELINE_EVENTS = frozenset({"first-candles", "candle-generated", "candles-generated"})

BLOCKED_EVENT_NAMES = frozenset(
    {
        "authenticate",
        "authenticated",
        "marginal-balance",
        "balances",
        "subscription-balance-changed",
        "portfolio",
        "portfolio.get-history-positions",
        "orders",
        "positions",
        "order",
        "position",
        "execution",
        "result",
    }
)

SENSITIVE_MARKERS = (
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "bearer",
    "cookie",
    "set-cookie",
    "ssid",
    "password",
    "credential",
    "headers",
    "har",
)

MAX_PAYLOAD_BYTES = 64_000
MAX_DEPTH = 8
MAX_ARRAY_ITEMS = 200
MAX_OBJECT_KEYS = 120
TRACE_MAX_DEPTH = 8
TRACE_MAX_LIST_ITEMS = 20


@dataclass(frozen=True)
class BrowserBridgeResult:
    accepted: bool
    event_name: str | None
    pipeline_success: bool | None
    processed: int
    stored: int
    updated: int
    ignored: int
    rejected: int
    error_code: str | None
    source: str = POLARIUM_AUTHORIZED_BROWSER_SOURCE
    data_classification: str = POLARIUM_AUTHORIZED_BROWSER_LABEL

    def sanitized(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "event_name": self.event_name,
            "pipeline_success": self.pipeline_success,
            "processed": self.processed,
            "stored": self.stored,
            "updated": self.updated,
            "ignored": self.ignored,
            "rejected": self.rejected,
            "error_code": self.error_code,
            "source": self.source,
            "data_classification": self.data_classification,
        }


@dataclass
class BrowserBridgeTrace:
    event_received: dict[str, Any] | None = None
    adapter_accepted: bool = False
    payload_converted: dict[str, Any] | None = None
    pipeline_input: dict[str, Any] | None = None
    pipeline_result: dict[str, Any] | None = None
    rejection_reason: str | None = None
    candle_store: dict[str, Any] | None = None
    chart_api_probe: dict[str, Any] | None = None
    payload_comparison: dict[str, Any] | None = None

    def sanitized(self) -> dict[str, Any]:
        return {
            "event_received": self.event_received,
            "adapter_accepted": self.adapter_accepted,
            "payload_converted": self.payload_converted,
            "pipeline_input": self.pipeline_input,
            "pipeline_result": self.pipeline_result,
            "rejection_reason": self.rejection_reason,
            "candle_store": self.candle_store,
            "chart_api_probe": self.chart_api_probe,
            "payload_comparison": self.payload_comparison,
        }


@dataclass
class BrowserBridgeStatus:
    connected: bool = False
    bridge_active: bool = False
    last_event_name: str | None = None
    last_event_at: datetime | None = None
    received_count: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    pipeline_success_count: int = 0
    last_error_code: str | None = None
    active_ids_seen: set[int] = field(default_factory=set)
    raw_sizes_seen: set[int] = field(default_factory=set)
    source: str = POLARIUM_AUTHORIZED_BROWSER_SOURCE
    data_classification: str = "DISCONNECTED"
    last_trace: BrowserBridgeTrace = field(default_factory=BrowserBridgeTrace)

    def sanitized(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "bridge_active": self.bridge_active,
            "last_event_name": self.last_event_name,
            "last_event_at": self.last_event_at.isoformat() if self.last_event_at else None,
            "received_count": self.received_count,
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "pipeline_success_count": self.pipeline_success_count,
            "last_error_code": self.last_error_code,
            "active_ids_seen": sorted(self.active_ids_seen),
            "raw_sizes_seen": sorted(self.raw_sizes_seen),
            "source": self.source,
            "data_classification": self.data_classification,
            "last_trace": self.last_trace.sanitized(),
        }


class AuthorizedBrowserBridgeRuntime:
    """Read-only authorized browser bridge that feeds sanitized market events."""

    def __init__(self, pipeline: MarketPipeline) -> None:
        self._pipeline = pipeline
        self._status = BrowserBridgeStatus()

    def status(self) -> BrowserBridgeStatus:
        return self._status

    def reset(self) -> None:
        self._status = BrowserBridgeStatus()

    @property
    def is_active(self) -> bool:
        return self._status.bridge_active

    def ingest(self, payload: dict[str, Any], *, payload_size: int) -> BrowserBridgeResult:
        self._status.received_count += 1
        self._status.last_trace = BrowserBridgeTrace(event_received=_trace_payload(payload))
        if payload_size > MAX_PAYLOAD_BYTES:
            return self._reject("PAYLOAD_TOO_LARGE", None)

        validation_error = _validate_shape(payload)
        if validation_error:
            return self._reject(validation_error, _event_name(payload))

        event_name = _event_name(payload)
        if event_name is None:
            return self._reject("EVENT_NAME_REQUIRED", None)
        if event_name in BLOCKED_EVENT_NAMES:
            return self._reject("EVENT_BLOCKED", event_name)
        if event_name not in ALLOWED_BROWSER_BRIDGE_EVENTS:
            return self._reject("EVENT_NOT_ALLOWED", event_name)
        if _contains_sensitive_marker(payload):
            return self._reject("SENSITIVE_FIELD_REJECTED", event_name)

        normalized = _normalize_for_pipeline(event_name, payload)
        self._status.last_trace.adapter_accepted = True
        self._status.last_trace.payload_converted = _trace_payload(normalized)
        self._status.last_trace.pipeline_input = _trace_payload(normalized)
        self._status.accepted_count += 1
        self._status.connected = True
        self._status.bridge_active = True
        self._status.last_event_name = event_name
        self._status.last_event_at = _utcnow()
        self._status.last_error_code = None
        self._status.data_classification = POLARIUM_AUTHORIZED_BROWSER_LABEL

        if event_name == "timeSync":
            return BrowserBridgeResult(
                accepted=True,
                event_name=event_name,
                pipeline_success=None,
                processed=0,
                stored=0,
                updated=0,
                ignored=0,
                rejected=0,
                error_code=None,
            )

        result = self._pipeline.process(normalized)
        self._record_pipeline_result(result)
        self._record_trace_result(payload, normalized, result)
        return BrowserBridgeResult(
            accepted=True,
            event_name=event_name,
            pipeline_success=result.success,
            processed=result.processed,
            stored=result.stored,
            updated=result.updated,
            ignored=result.ignored,
            rejected=result.rejected,
            error_code=None if result.success else "PIPELINE_REJECTED",
        )

    def _reject(self, error_code: str, event_name: str | None) -> BrowserBridgeResult:
        self._status.rejected_count += 1
        self._status.last_event_name = event_name
        self._status.last_event_at = _utcnow()
        self._status.last_error_code = error_code
        self._status.last_trace.rejection_reason = error_code
        return BrowserBridgeResult(
            accepted=False,
            event_name=event_name,
            pipeline_success=False,
            processed=0,
            stored=0,
            updated=0,
            ignored=0,
            rejected=1,
            error_code=error_code,
        )

    def _record_pipeline_result(self, result: PipelineResult) -> None:
        if result.success:
            self._status.pipeline_success_count += 1
        for candle in result.route_result.candles:
            if candle.active_id is not None:
                self._status.active_ids_seen.add(candle.active_id)
            self._status.raw_sizes_seen.add(candle.raw_size)

    def _record_trace_result(self, received: dict[str, Any], converted: dict[str, Any], result: PipelineResult) -> None:
        errors = [
            {
                "code": error.code,
                "message": error.message,
                "path": error.path,
            }
            for error in result.errors
        ]
        self._status.last_trace.pipeline_result = {
            "success": result.success,
            "processed": result.processed,
            "stored": result.stored,
            "updated": result.updated,
            "ignored": result.ignored,
            "unsupported": result.unsupported,
            "rejected": result.rejected,
            "route_status": result.route_result.status,
            "errors": errors,
        }
        if not result.success:
            self._status.last_trace.rejection_reason = errors[0]["code"] if errors else "PIPELINE_REJECTED"

        saved = []
        chart_probe = None
        for candle in result.route_result.candles:
            if candle.active_id is None:
                continue
            series = self._pipeline.candle_store.series(candle.active_id, candle.raw_size)
            saved.append(
                {
                    "active_id": candle.active_id,
                    "raw_size": candle.raw_size,
                    "series_count_after": len(series),
                    "start_timestamp": candle.start_timestamp,
                    "end_timestamp": candle.end_timestamp,
                    "open": candle.open,
                    "close": candle.close,
                    "low_candidate": candle.low_candidate,
                    "high_candidate": candle.high_candidate,
                    "volume": candle.volume,
                }
            )
            chart_probe = {
                "endpoint": "/api/v1/market/chart",
                "params": {"active_id": candle.active_id, "raw_size": candle.raw_size},
                "count": len(series),
                "latest": _candle_to_chart_probe(series[-1]) if series else None,
            }

        self._status.last_trace.candle_store = {
            "received_candles": len(result.route_result.candles),
            "saved_candles": saved,
        }
        self._status.last_trace.chart_api_probe = chart_probe
        self._status.last_trace.payload_comparison = {
            "received": _trace_payload(received),
            "sent_to_pipeline": _trace_payload(converted),
            "saved": saved,
        }


def _normalize_for_pipeline(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    return adapt_browser_bridge_payload(event_name, payload)


def _event_name(payload: dict[str, Any]) -> str | None:
    direct = payload.get("event_name") or payload.get("name") or payload.get("event") or payload.get("type")
    if isinstance(direct, str):
        return direct
    nested = payload.get("payload")
    if isinstance(nested, dict):
        return _event_name(nested)
    msg = payload.get("msg")
    if isinstance(msg, dict) and isinstance(msg.get("name"), str):
        return msg["name"]
    return None


def _validate_shape(value: Any, *, depth: int = 0) -> str | None:
    if depth > MAX_DEPTH:
        return "PAYLOAD_TOO_DEEP"
    if isinstance(value, dict):
        if len(value) > MAX_OBJECT_KEYS:
            return "PAYLOAD_TOO_WIDE"
        for child in value.values():
            error = _validate_shape(child, depth=depth + 1)
            if error:
                return error
    elif isinstance(value, list):
        if depth == 0:
            return "ROOT_ARRAY_REJECTED"
        if len(value) > MAX_ARRAY_ITEMS:
            return "PAYLOAD_ARRAY_TOO_LONG"
        for child in value:
            error = _validate_shape(child, depth=depth + 1)
            if error:
                return error
    return None


def _contains_sensitive_marker(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in SENSITIVE_MARKERS):
                return True
            if _contains_sensitive_marker(child):
                return True
    elif isinstance(value, list):
        return any(_contains_sensitive_marker(child) for child in value)
    elif isinstance(value, str):
        lowered = value.lower()
        if "bearer " in lowered:
            return True
    return False


def _trace_payload(value: Any, *, depth: int = 0) -> Any:
    if depth > TRACE_MAX_DEPTH:
        return "<max-depth>"
    if isinstance(value, dict):
        traced: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in SENSITIVE_MARKERS):
                traced[str(key)] = "<redacted>"
            else:
                traced[str(key)] = _trace_payload(child, depth=depth + 1)
        return traced
    if isinstance(value, list):
        return [_trace_payload(child, depth=depth + 1) for child in value[:TRACE_MAX_LIST_ITEMS]]
    if isinstance(value, str) and "bearer " in value.lower():
        return "<redacted>"
    return value


def _candle_to_chart_probe(candle: Any) -> dict[str, Any]:
    return {
        "time": candle.start_timestamp,
        "open": candle.open,
        "high": candle.high_candidate,
        "low": candle.low_candidate,
        "close": candle.close,
    }


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
