from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from app.market.providers.polarium.readiness import HISTORY_EVENTS
from app.market.store.types import CandleStoreWriteResult

BootstrapPayloadTraceCategory = Literal[
    "PAYLOAD_EMPTY",
    "PAYLOAD_SINGLE_CANDLE",
    "PAYLOAD_MULTI_CANDLE",
    "PARSER_DROPPED",
    "VALIDATION_DROPPED",
    "STORE_DROPPED",
    "DUPLICATE_FILTER",
    "SUCCESS",
    "UNKNOWN",
]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "bootstrap_payload_report.json"
REPORT_TXT = REPORT_DIR / "bootstrap_payload_report.txt"


@dataclass
class BootstrapPayloadTraceRecord:
    request_id: str | None
    active_id: int | None
    symbol: str | None
    raw_size: int | None
    response_message_type: str | None
    payload_format_detected: str
    candles_in_payload: int
    candles_after_parser: int
    candles_after_validation: int
    candles_written: int
    candles_ignored: int
    duplicate_count: int
    first_timestamp: int | None
    last_timestamp: int | None
    bucket_before: int
    bucket_after: int
    history_before: int
    history_after: int
    readiness_before: str | None
    readiness_after: str | None
    category: BootstrapPayloadTraceCategory
    observed_at: int | None = None
    parser_error: str | None = None
    notes: list[str] = field(default_factory=list)

    def sanitized(self) -> dict[str, Any]:
        return asdict(self)


class BootstrapPayloadTraceDiagnostic:
    """Sanitized proof trace for first-candles/candles bootstrap payloads."""

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
        self._records: list[BootstrapPayloadTraceRecord] = []

    @property
    def records(self) -> tuple[BootstrapPayloadTraceRecord, ...]:
        return tuple(self._records)

    def observe_success(
        self,
        *,
        message: dict[str, Any],
        event: Any,
        store_results: tuple[CandleStoreWriteResult, ...],
        request_id: str | None,
        requested_active_id: int | None,
        requested_raw_size: int | None,
        bucket_before: int,
        bucket_after: int,
        history_before: int,
        history_after: int,
        readiness_before: str | None,
        readiness_after: str | None,
        now_ms: int,
    ) -> None:
        if getattr(event, "event_name", None) not in HISTORY_EVENTS:
            return
        raw_size = requested_raw_size or _first_event_raw_size(event)
        event_candles = tuple(
            candle
            for candle in getattr(event, "candles", ())
            if raw_size is None or getattr(candle, "raw_size", None) == raw_size
        )
        candles_in_payload = _history_candle_count(message, raw_size)
        candles_after_parser = len(event_candles)
        candles_after_validation = candles_after_parser
        candles_written = _count_status(store_results, {"added", "updated"})
        candles_ignored = _count_status(store_results, {"ignored"})
        record = BootstrapPayloadTraceRecord(
            request_id=request_id,
            active_id=getattr(event, "active_id", None) or requested_active_id,
            symbol=getattr(event, "symbol", None),
            raw_size=raw_size,
            response_message_type=getattr(event, "event_name", None) or _event_name(message),
            payload_format_detected=_payload_format(message),
            candles_in_payload=candles_in_payload,
            candles_after_parser=candles_after_parser,
            candles_after_validation=candles_after_validation,
            candles_written=candles_written,
            candles_ignored=candles_ignored,
            duplicate_count=candles_ignored,
            first_timestamp=_first_timestamp(event_candles) or _payload_first_timestamp(message, raw_size),
            last_timestamp=_last_timestamp(event_candles) or _payload_last_timestamp(message, raw_size),
            bucket_before=bucket_before,
            bucket_after=bucket_after,
            history_before=history_before,
            history_after=history_after,
            readiness_before=readiness_before,
            readiness_after=readiness_after,
            category="UNKNOWN",
            observed_at=now_ms,
        )
        record.category = _classify_success(record, store_results)
        self._records.append(record)
        self._write_if_enabled()

    def observe_parse_error(
        self,
        *,
        message: dict[str, Any],
        error: str,
        request_id: str | None,
        requested_active_id: int | None,
        requested_raw_size: int | None,
        bucket_before: int,
        history_before: int,
        readiness_before: str | None,
        now_ms: int,
    ) -> None:
        if _event_name(message) not in HISTORY_EVENTS:
            return
        candles_in_payload = _history_candle_count(message, requested_raw_size)
        record = BootstrapPayloadTraceRecord(
            request_id=request_id,
            active_id=requested_active_id or _find_active_id(message),
            symbol=_find_symbol(message),
            raw_size=requested_raw_size or _find_raw_size(message),
            response_message_type=_event_name(message),
            payload_format_detected=_payload_format(message),
            candles_in_payload=candles_in_payload,
            candles_after_parser=0,
            candles_after_validation=0,
            candles_written=0,
            candles_ignored=0,
            duplicate_count=0,
            first_timestamp=_payload_first_timestamp(message, requested_raw_size),
            last_timestamp=_payload_last_timestamp(message, requested_raw_size),
            bucket_before=bucket_before,
            bucket_after=bucket_before,
            history_before=history_before,
            history_after=history_before,
            readiness_before=readiness_before,
            readiness_after=readiness_before,
            category=_classify_parse_error(candles_in_payload, error),
            observed_at=now_ms,
            parser_error=_sanitize_error(error),
        )
        self._records.append(record)
        self._write_if_enabled()

    def write_reports(self) -> None:
        self._report_json.parent.mkdir(parents=True, exist_ok=True)
        payload = self.sanitized()
        self._report_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._report_txt.write_text(_render_text(payload), encoding="utf-8")

    def sanitized(self) -> dict[str, Any]:
        records = [record.sanitized() for record in self._records]
        categories = Counter(record["category"] for record in records)
        return {
            "summary": {
                "total_records": len(records),
                "categories": dict(sorted(categories.items())),
            },
            "records": records,
        }

    def _write_if_enabled(self) -> None:
        if self._auto_write:
            self.write_reports()


def _classify_success(
    record: BootstrapPayloadTraceRecord,
    store_results: tuple[CandleStoreWriteResult, ...],
) -> BootstrapPayloadTraceCategory:
    if record.candles_in_payload == 0:
        return "PAYLOAD_EMPTY"
    if record.candles_after_parser < record.candles_in_payload:
        return "PARSER_DROPPED"
    if record.candles_after_validation < record.candles_after_parser:
        return "VALIDATION_DROPPED"
    if any(result.status == "rejected" for result in store_results):
        return "STORE_DROPPED"
    if record.duplicate_count > 0 and record.candles_written == 0:
        return "DUPLICATE_FILTER"
    if record.candles_written + record.candles_ignored < record.candles_after_validation:
        return "STORE_DROPPED"
    if record.candles_in_payload == 1 and record.candles_after_parser == 1 and record.candles_written <= 1:
        return "PAYLOAD_SINGLE_CANDLE"
    if record.candles_in_payload > 1 and record.candles_written > 0:
        return "SUCCESS"
    if record.candles_in_payload > 1:
        return "PAYLOAD_MULTI_CANDLE"
    return "UNKNOWN"


def _classify_parse_error(candles_in_payload: int, error: str) -> BootstrapPayloadTraceCategory:
    if candles_in_payload == 0:
        return "PAYLOAD_EMPTY"
    if "DROP_INVALID_HISTORICAL_TIMESTAMP" in error:
        return "VALIDATION_DROPPED"
    return "PARSER_DROPPED"


def _count_status(results: tuple[CandleStoreWriteResult, ...], statuses: set[str]) -> int:
    return sum(1 for result in results if result.status in statuses)


def _first_event_raw_size(event: Any) -> int | None:
    candles = getattr(event, "candles", ())
    return candles[0].raw_size if candles else None


def _first_timestamp(candles: tuple[Any, ...]) -> int | None:
    values = [getattr(candle, "start_timestamp", None) for candle in candles]
    parsed = [value for value in values if isinstance(value, int)]
    return min(parsed) if parsed else None


def _last_timestamp(candles: tuple[Any, ...]) -> int | None:
    values = [getattr(candle, "start_timestamp", None) for candle in candles]
    parsed = [value for value in values if isinstance(value, int)]
    return max(parsed) if parsed else None


def _event_name(message: dict[str, Any]) -> str | None:
    name = message.get("name")
    if isinstance(name, str) and name != "sendMessage":
        return name
    msg = message.get("msg")
    if isinstance(msg, dict) and isinstance(msg.get("name"), str):
        return msg["name"]
    return name if isinstance(name, str) else None


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


def _payload_format(message: dict[str, Any]) -> str:
    body = _history_body(message)
    if isinstance(body.get("candles"), list):
        return "list:candles"
    if isinstance(body.get("candles_by_size"), dict):
        return "dict:candles_by_size"
    if isinstance(body.get("candles"), dict):
        return "dict:candles"
    if any(body.get(str(size)) or body.get(size) for size in (60, 300, 900)):
        return "dict:size_keys"
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
            value = candles_by_size.get(str(raw_size)) or candles_by_size.get(raw_size)
            if isinstance(value, list):
                return sum(1 for item in value if isinstance(item, dict))
            return 1 if isinstance(value, dict) else 0
        total = 0
        for value in candles_by_size.values():
            if isinstance(value, list):
                total += sum(1 for item in value if isinstance(item, dict))
            elif isinstance(value, dict):
                total += 1
        return total
    return 0


def _payload_timestamps(message: dict[str, Any], raw_size: int | None) -> list[int]:
    body = _history_body(message)
    candles: list[Any] = []
    raw_list = body.get("candles")
    if isinstance(raw_list, list):
        candles = raw_list
    else:
        candles_by_size = body.get("candles_by_size") or body.get("candles")
        if not isinstance(candles_by_size, dict) and any((body.get(str(size)) or body.get(size)) for size in (60, 300, 900)):
            candles_by_size = body
        if isinstance(candles_by_size, dict):
            if raw_size is not None:
                value = candles_by_size.get(str(raw_size)) or candles_by_size.get(raw_size)
                candles = value if isinstance(value, list) else [value]
            else:
                candles = list(candles_by_size.values())
    timestamps = []
    for candle in candles:
        if not isinstance(candle, dict):
            continue
        if raw_size is not None and _as_int(candle.get("size")) not in {None, raw_size}:
            continue
        parsed = _as_int(candle.get("from"))
        if parsed is not None:
            timestamps.append(parsed)
    return timestamps


def _payload_first_timestamp(message: dict[str, Any], raw_size: int | None) -> int | None:
    timestamps = _payload_timestamps(message, raw_size)
    return min(timestamps) if timestamps else None


def _payload_last_timestamp(message: dict[str, Any], raw_size: int | None) -> int | None:
    timestamps = _payload_timestamps(message, raw_size)
    return max(timestamps) if timestamps else None


def _find_active_id(value: Any) -> int | None:
    return _find_first_int(value, {"active_id", "activeId"})


def _find_raw_size(value: Any) -> int | None:
    return _find_first_int(value, {"size", "raw_size", "rawSize"})


def _find_symbol(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("symbol", "ticker", "display_name", "displayName"):
            parsed = _as_symbol(value.get(key))
            if parsed is not None:
                return parsed
        for item in value.values():
            parsed = _find_symbol(item)
            if parsed is not None:
                return parsed
    if isinstance(value, list):
        for item in value:
            parsed = _find_symbol(item)
            if parsed is not None:
                return parsed
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


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _as_symbol(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = " ".join(value.strip().split())
    if not parsed or len(parsed) > 80:
        return None
    lowered = parsed.lower()
    if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password")):
        return None
    return parsed


def _sanitize_error(error: str) -> str:
    lowered = error.lower()
    if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password", "secret")):
        return "SANITIZED_ERROR"
    return error[:160]


def _render_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Bootstrap Payload Trace", ""]
    summary = payload.get("summary", {})
    lines.append(f"total_records: {summary.get('total_records', 0)}")
    lines.append(f"categories: {summary.get('categories', {})}")
    lines.append("")
    for record in payload.get("records", []):
        label = record.get("symbol") or f"active_id={record.get('active_id')}"
        lines.append(f"- {label} raw_size={record.get('raw_size')} request_id={record.get('request_id')}")
        lines.append(f"  category: {record.get('category')}")
        lines.append(f"  response_message_type: {record.get('response_message_type')}")
        lines.append(f"  payload_format_detected: {record.get('payload_format_detected')}")
        lines.append(
            "  counts: "
            f"payload={record.get('candles_in_payload')} parser={record.get('candles_after_parser')} "
            f"validation={record.get('candles_after_validation')} written={record.get('candles_written')} "
            f"ignored={record.get('candles_ignored')} duplicates={record.get('duplicate_count')}"
        )
        lines.append(f"  timestamps: {record.get('first_timestamp')} -> {record.get('last_timestamp')}")
        lines.append(f"  bucket: {record.get('bucket_before')} -> {record.get('bucket_after')}")
        lines.append(f"  history_count: {record.get('history_before')} -> {record.get('history_after')}")
        lines.append(f"  readiness: {record.get('readiness_before')} -> {record.get('readiness_after')}")
        if record.get("parser_error"):
            lines.append(f"  parser_error: {record.get('parser_error')}")
    lines.append("")
    return "\n".join(lines)
