from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from app.market.providers.polarium.readiness import HISTORY_EVENTS, REALTIME_EVENTS

BootstrapFailureCategory = Literal[
    "REQUEST_NOT_SENT",
    "NO_RESPONSE",
    "WRONG_ACTIVE_ID",
    "RAW_SIZE_NOT_RESOLVED",
    "UNSUPPORTED_PAYLOAD",
    "NO_CANDLES_FOUND",
    "TIMESTAMP_REJECTED",
    "STORE_KEY_MISMATCH",
    "HISTORY_NOT_INCREMENTED",
    "READINESS_NOT_UPDATED",
    "REALTIME_ONLY",
    "UNKNOWN",
]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "bootstrap_report.json"
REPORT_TXT = REPORT_DIR / "bootstrap_report.txt"


@dataclass
class BootstrapDiagnosticRecord:
    request_id: str | None
    active_id: int | None
    symbol: str | None
    display_name: str | None
    market_type: str | None
    raw_size_requested: int | None
    raw_size_resolved: int | None
    response_active_id: int | None = None
    request_sent: bool = False
    response_received: bool = False
    response_type: str | None = None
    payload_shape: str | None = None
    candles_found: int = 0
    candles_accepted: int = 0
    candles_rejected: int = 0
    rejection_reason: str | None = None
    history_count_before: int | None = None
    history_count_after: int | None = None
    readiness_before: str | None = None
    readiness_after: str | None = None
    timeout: bool = False
    expired_request: bool = False
    realtime_seen: bool = False
    store_key_match: bool | None = None
    failure_step: str = "UNKNOWN"
    category: BootstrapFailureCategory = "UNKNOWN"
    observed_at: int | None = None
    notes: list[str] = field(default_factory=list)

    def sanitized(self) -> dict[str, Any]:
        data = asdict(self)
        data["notes"] = list(self.notes)
        return data


class HistoricalBootstrapDiagnostic:
    """Writes sanitized, automatic diagnostics for historical bootstrap flows."""

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
        self._records: dict[str, BootstrapDiagnosticRecord] = {}

    @property
    def records(self) -> tuple[BootstrapDiagnosticRecord, ...]:
        return tuple(self._records.values())

    def observe_request(
        self,
        *,
        active_id: int | None,
        raw_size: int | None,
        request_id: str | None,
        request_sent: bool,
        session_context: dict[str, Any] | None,
        now_ms: int,
    ) -> None:
        key = _record_key(request_id, active_id, raw_size)
        record = self._records.get(key) or _new_record(
            request_id=request_id,
            active_id=active_id,
            raw_size=raw_size,
            session_context=session_context,
            now_ms=now_ms,
        )
        record.request_sent = record.request_sent or request_sent
        record.raw_size_requested = raw_size
        record.raw_size_resolved = raw_size
        record.observed_at = now_ms
        record.failure_step = "PENDING_RESPONSE"
        record.category = "NO_RESPONSE" if request_sent else "REQUEST_NOT_SENT"
        self._records[key] = record
        self._write_if_enabled()

    def observe_response(
        self,
        *,
        message: dict[str, Any],
        event: Any,
        result: Any,
        request_id: str | None,
        requested_active_id: int | None,
        requested_raw_size: int | None,
        session_context_before: dict[str, Any] | None,
        session_context_after: dict[str, Any] | None,
        history_count_before: int,
        history_count_after: int,
        now_ms: int,
    ) -> None:
        active_id = getattr(event, "active_id", None)
        raw_size = requested_raw_size or _first_event_raw_size(event)
        key = _matching_key(
            self._records,
            request_id=request_id,
            active_id=requested_active_id or active_id,
            raw_size=raw_size,
        )
        record = self._records.get(key) or _new_record(
            request_id=request_id,
            active_id=requested_active_id or active_id,
            raw_size=raw_size,
            session_context=session_context_before,
            now_ms=now_ms,
        )
        record.request_id = record.request_id or request_id
        record.response_active_id = active_id
        record.active_id = record.active_id or requested_active_id or active_id
        record.raw_size_resolved = raw_size
        record.response_received = True
        record.response_type = getattr(event, "event_name", None) or _event_name(message)
        record.payload_shape = _payload_shape(message)
        record.candles_found = _history_candle_count(message, raw_size)
        record.candles_accepted = sum(1 for candle in getattr(event, "candles", ()) if raw_size is None or candle.raw_size == raw_size)
        record.candles_rejected = max(record.candles_found - record.candles_accepted, 0)
        record.history_count_before = history_count_before
        record.history_count_after = history_count_after
        record.readiness_before = _history_state(session_context_before)
        record.readiness_after = _history_state(session_context_after)
        record.store_key_match = _store_key_matches(result, active_id=active_id, raw_size=raw_size)
        record.observed_at = now_ms
        _apply_context(record, session_context_after)
        _classify(record)
        self._records[key] = record
        self._write_if_enabled()

    def observe_parse_error(
        self,
        *,
        message: dict[str, Any],
        error: str,
        request_id: str | None,
        requested_active_id: int | None,
        requested_raw_size: int | None,
        session_context: dict[str, Any] | None,
        history_count_before: int,
        now_ms: int,
    ) -> None:
        key = _matching_key(self._records, request_id=request_id, active_id=requested_active_id, raw_size=requested_raw_size)
        record = self._records.get(key) or _new_record(
            request_id=request_id,
            active_id=requested_active_id,
            raw_size=requested_raw_size,
            session_context=session_context,
            now_ms=now_ms,
        )
        record.response_received = True
        record.response_type = _event_name(message)
        record.payload_shape = _payload_shape(message)
        record.candles_found = _history_candle_count(message, requested_raw_size)
        record.candles_accepted = 0
        record.candles_rejected = record.candles_found
        record.rejection_reason = _sanitize_reason(error)
        record.history_count_before = history_count_before
        record.history_count_after = history_count_before
        record.readiness_before = _history_state(session_context)
        record.readiness_after = _history_state(session_context)
        record.store_key_match = None
        record.observed_at = now_ms
        _classify(record)
        self._records[key] = record
        self._write_if_enabled()

    def observe_realtime(
        self,
        *,
        active_id: int | None,
        raw_size: int | None,
        session_context: dict[str, Any] | None,
        now_ms: int,
    ) -> None:
        key = _record_key(None, active_id, raw_size)
        if key in self._records:
            record = self._records[key]
            record.realtime_seen = True
            self._write_if_enabled()
            return
        record = _new_record(request_id=None, active_id=active_id, raw_size=raw_size, session_context=session_context, now_ms=now_ms)
        record.realtime_seen = True
        record.failure_step = "REALTIME_WITHOUT_HISTORY"
        record.category = "REALTIME_ONLY"
        self._records[key] = record
        self._write_if_enabled()

    def observe_timeout(
        self,
        *,
        request_id: str | None,
        active_id: int | None,
        raw_size: int | None,
        session_context: dict[str, Any] | None,
        expired: bool,
        now_ms: int,
    ) -> None:
        key = _matching_key(self._records, request_id=request_id, active_id=active_id, raw_size=raw_size)
        record = self._records.get(key) or _new_record(
            request_id=request_id,
            active_id=active_id,
            raw_size=raw_size,
            session_context=session_context,
            now_ms=now_ms,
        )
        record.timeout = True
        record.expired_request = expired
        record.failure_step = "WAITING_FOR_RESPONSE"
        record.category = "NO_RESPONSE"
        record.observed_at = now_ms
        self._records[key] = record
        self._write_if_enabled()

    def write_reports(self) -> None:
        self._report_json.parent.mkdir(parents=True, exist_ok=True)
        payload = self.sanitized()
        self._report_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._report_txt.write_text(_render_text(payload), encoding="utf-8")

    def sanitized(self) -> dict[str, Any]:
        records = [record.sanitized() for record in self.records]
        categories = Counter(record["category"] for record in records)
        return {
            "summary": {
                "total_bootstraps": len(records),
                "categories": dict(sorted(categories.items())),
            },
            "records": records,
        }

    def _write_if_enabled(self) -> None:
        if self._auto_write:
            self.write_reports()


def _new_record(
    *,
    request_id: str | None,
    active_id: int | None,
    raw_size: int | None,
    session_context: dict[str, Any] | None,
    now_ms: int,
) -> BootstrapDiagnosticRecord:
    record = BootstrapDiagnosticRecord(
        request_id=request_id,
        active_id=active_id,
        symbol=_string_or_none((session_context or {}).get("symbol")),
        display_name=_string_or_none((session_context or {}).get("display_name")),
        market_type=_string_or_none((session_context or {}).get("market_type")),
        raw_size_requested=raw_size,
        raw_size_resolved=raw_size,
        observed_at=now_ms,
    )
    _apply_context(record, session_context)
    return record


def _apply_context(record: BootstrapDiagnosticRecord, session_context: dict[str, Any] | None) -> None:
    if not session_context:
        return
    record.active_id = record.active_id or _as_int(session_context.get("active_id")) or _as_int(session_context.get("visible_active_id"))
    record.symbol = record.symbol or _string_or_none(session_context.get("symbol")) or _string_or_none(session_context.get("visible_symbol"))
    record.display_name = record.display_name or _string_or_none(session_context.get("display_name")) or _string_or_none(session_context.get("visible_display_name"))
    record.market_type = record.market_type or _string_or_none(session_context.get("market_type")) or _string_or_none(session_context.get("visible_market_type"))
    record.raw_size_resolved = record.raw_size_resolved or _as_int(session_context.get("raw_size")) or _as_int(session_context.get("visible_raw_size"))


def _classify(record: BootstrapDiagnosticRecord) -> None:
    if not record.request_sent and not record.response_received:
        record.category = "REQUEST_NOT_SENT"
        record.failure_step = "REQUEST"
        return
    if not record.response_received:
        record.category = "NO_RESPONSE"
        record.failure_step = "RESPONSE"
    elif record.active_id is not None and record.response_active_id is not None and record.active_id != record.response_active_id:
        record.category = "WRONG_ACTIVE_ID"
        record.failure_step = "CORRELATION"
    elif record.active_id is not None and record.request_id and record.raw_size_requested is not None and record.raw_size_resolved is None:
        record.category = "RAW_SIZE_NOT_RESOLVED"
        record.failure_step = "RAW_SIZE_RESOLUTION"
    elif record.rejection_reason and "DROP_INVALID_HISTORICAL_TIMESTAMP" in record.rejection_reason:
        record.category = "TIMESTAMP_REJECTED"
        record.failure_step = "TEMPORAL_VALIDATION"
    elif record.rejection_reason and "UNSUPPORTED" in record.rejection_reason:
        record.category = "UNSUPPORTED_PAYLOAD"
        record.failure_step = "PARSER"
    elif record.candles_found == 0:
        record.category = "NO_CANDLES_FOUND"
        record.failure_step = "PAYLOAD_CANDLES"
    elif record.store_key_match is False:
        record.category = "STORE_KEY_MISMATCH"
        record.failure_step = "CANDLE_STORE"
    elif record.candles_accepted > 0 and record.history_count_after == record.history_count_before:
        record.category = "HISTORY_NOT_INCREMENTED"
        record.failure_step = "HISTORY_COUNT"
    elif (
        record.history_count_after is not None
        and record.history_count_before is not None
        and record.history_count_after > record.history_count_before
        and record.readiness_after == record.readiness_before
        and record.readiness_after == "BOOTSTRAPPING"
    ):
        record.category = "READINESS_NOT_UPDATED"
        record.failure_step = "READINESS"
    else:
        record.category = "UNKNOWN"
        record.failure_step = "NO_DIVERGENCE_CLASSIFIED"


def _record_key(request_id: str | None, active_id: int | None, raw_size: int | None) -> str:
    if request_id:
        return f"request:{request_id}"
    return f"context:{active_id}:{raw_size}"


def _matching_key(records: dict[str, BootstrapDiagnosticRecord], *, request_id: str | None, active_id: int | None, raw_size: int | None) -> str:
    if request_id and f"request:{request_id}" in records:
        return f"request:{request_id}"
    context_key = _record_key(None, active_id, raw_size)
    if context_key in records:
        return context_key
    if request_id:
        return f"request:{request_id}"
    return context_key


def _event_name(message: dict[str, Any]) -> str | None:
    name = message.get("name")
    if isinstance(name, str) and name != "sendMessage":
        return name
    msg = message.get("msg")
    if isinstance(msg, dict) and isinstance(msg.get("name"), str):
        return msg["name"]
    return name if isinstance(name, str) else None


def _history_state(session_context: dict[str, Any] | None) -> str | None:
    value = (session_context or {}).get("history_state")
    return value if isinstance(value, str) else None


def _payload_shape(message: dict[str, Any]) -> str:
    msg = message.get("msg")
    if isinstance(msg, dict):
        for container in ("body", "result", "data"):
            item = msg.get(container)
            if isinstance(item, dict):
                return f"msg.{container}.{_body_shape(item)}"
        return f"msg.{_body_shape(msg)}"
    return _body_shape(message)


def _body_shape(body: dict[str, Any]) -> str:
    if isinstance(body.get("candles"), list):
        return "candles[]"
    if isinstance(body.get("candles_by_size"), dict):
        return "candles_by_size{}"
    if isinstance(body.get("candles"), dict):
        return "candles{}"
    if any(body.get(str(size)) or body.get(size) for size in (60, 300, 900)):
        return "size_keys{}"
    return "unknown"


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
        return message
    for key in ("body", "result", "data"):
        value = msg.get(key)
        if isinstance(value, dict):
            return value
    if any(key in msg for key in ("active_id", "candles", "candles_by_size")):
        return msg
    return {}


def _first_event_raw_size(event: Any) -> int | None:
    candles = getattr(event, "candles", ())
    if candles:
        return getattr(candles[0], "raw_size", None)
    return None


def _store_key_matches(result: Any, *, active_id: int | None, raw_size: int | None) -> bool | None:
    store_results = getattr(result, "store_results", ())
    if not store_results:
        return None
    for item in store_results:
        key = getattr(item, "key", None)
        if key is None:
            continue
        if active_id is not None and getattr(key, "active_id", None) != active_id:
            return False
        if raw_size is not None and getattr(key, "raw_size", None) != raw_size:
            return False
    return True


def _sanitize_reason(reason: str) -> str:
    forbidden = ("token", "cookie", "authorization", "bearer", "ssid", "password", "secret")
    lowered = reason.lower()
    if any(term in lowered for term in forbidden):
        return "SANITIZED_ERROR"
    return reason[:160]


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _string_or_none(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = " ".join(value.strip().split())
    if not parsed:
        return None
    lowered = parsed.lower()
    if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password", "secret")):
        return None
    return parsed[:120]


def _render_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Historical Bootstrap Diagnostic", ""]
    summary = payload.get("summary", {})
    lines.append(f"total_bootstraps: {summary.get('total_bootstraps', 0)}")
    lines.append(f"categories: {summary.get('categories', {})}")
    lines.append("")
    for record in payload.get("records", []):
        label = record.get("symbol") or record.get("display_name") or f"active_id={record.get('active_id')}"
        lines.append(f"- {label} raw_size={record.get('raw_size_resolved') or record.get('raw_size_requested')}")
        lines.append(f"  category: {record.get('category')}")
        lines.append(f"  failure_step: {record.get('failure_step')}")
        lines.append(f"  request_sent: {record.get('request_sent')} response_received: {record.get('response_received')}")
        lines.append(f"  candles_found: {record.get('candles_found')} accepted: {record.get('candles_accepted')} rejected: {record.get('candles_rejected')}")
        lines.append(f"  history_count: {record.get('history_count_before')} -> {record.get('history_count_after')}")
        lines.append(f"  readiness: {record.get('readiness_before')} -> {record.get('readiness_after')}")
        if record.get("rejection_reason"):
            lines.append(f"  rejection_reason: {record.get('rejection_reason')}")
    lines.append("")
    return "\n".join(lines)
