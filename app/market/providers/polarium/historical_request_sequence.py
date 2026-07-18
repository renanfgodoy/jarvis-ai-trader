from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

HistoricalRequestOrigin = Literal["PAGE_NATIVE", "FRIDAY_PROGRAMMATIC"]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "historical_request_sequence.json"
REPORT_TXT = REPORT_DIR / "historical_request_sequence.txt"


@dataclass(frozen=True)
class HistoricalRequestSequenceEntry:
    order: int
    origin: HistoricalRequestOrigin
    timestamp: int
    request_id: str | None
    name: str | None
    inner_name: str | None
    active_id: int | None
    raw_size: int | None
    count: int | None
    from_timestamp: int | None
    to_timestamp: int | None
    offset: int | None

    def sanitized(self) -> dict[str, Any]:
        return asdict(self)


class HistoricalRequestSequenceDiagnostic:
    """Captures sanitized outbound market/history request sequences."""

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
        self._entries: list[HistoricalRequestSequenceEntry] = []
        self._next_order = 1

    @property
    def entries(self) -> tuple[HistoricalRequestSequenceEntry, ...]:
        return tuple(self._entries)

    def clear(self) -> None:
        self._entries.clear()
        self._next_order = 1
        self._write_if_enabled()

    def observe_outbound(self, message: dict[str, Any], *, origin: HistoricalRequestOrigin, now_ms: int) -> None:
        if not _is_market_history_outbound(message):
            return
        entry = HistoricalRequestSequenceEntry(
            order=self._next_order,
            origin=origin,
            timestamp=now_ms,
            request_id=_request_id(message),
            name=_event_name(message),
            inner_name=_inner_name(message),
            active_id=_find_first_int(message, {"active_id", "activeId"}),
            raw_size=_find_first_int(message, {"size", "raw_size", "rawSize"}),
            count=_find_first_int(message, {"count", "limit"}),
            from_timestamp=_find_first_int(message, {"from", "start", "startTime", "start_time"}),
            to_timestamp=_find_first_int(message, {"to", "end", "endTime", "end_time"}),
            offset=_find_first_int(message, {"offset"}),
        )
        self._next_order += 1
        self._entries.append(entry)
        self._write_if_enabled()

    def write_reports(self) -> None:
        self._report_json.parent.mkdir(parents=True, exist_ok=True)
        payload = self.sanitized()
        self._report_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._report_txt.write_text(_render_text(payload), encoding="utf-8")

    def sanitized(self) -> dict[str, Any]:
        manual = [entry.sanitized() for entry in self._entries if entry.origin == "PAGE_NATIVE"]
        programmatic = [entry.sanitized() for entry in self._entries if entry.origin == "FRIDAY_PROGRAMMATIC"]
        missing = _missing_entries(manual, programmatic)
        categories = Counter(entry.origin for entry in self._entries)
        return {
            "summary": {
                "total_entries": len(self._entries),
                "by_origin": dict(sorted(categories.items())),
                "manual_count": len(manual),
                "programmatic_count": len(programmatic),
                "missing_in_programmatic_count": len(missing),
            },
            "manual_flow": manual,
            "programmatic_flow": programmatic,
            "missing_in_programmatic_flow": missing,
        }

    def _write_if_enabled(self) -> None:
        if self._auto_write:
            self.write_reports()


def _missing_entries(manual: list[dict[str, Any]], programmatic: list[dict[str, Any]]) -> list[dict[str, Any]]:
    programmatic_signatures = [_signature(entry) for entry in programmatic]
    missing = []
    for entry in manual:
        signature = _signature(entry)
        if signature not in programmatic_signatures:
            missing.append(
                {
                    "manual_order": entry["order"],
                    "name": entry["name"],
                    "inner_name": entry["inner_name"],
                    "active_id": entry["active_id"],
                    "raw_size": entry["raw_size"],
                    "count": entry["count"],
                    "from": entry["from_timestamp"],
                    "to": entry["to_timestamp"],
                    "offset": entry["offset"],
                }
            )
    return missing


def _signature(entry: dict[str, Any]) -> tuple[Any, ...]:
    return (
        entry.get("name"),
        entry.get("inner_name"),
        entry.get("active_id"),
        entry.get("raw_size"),
        entry.get("count"),
        entry.get("from_timestamp"),
        entry.get("to_timestamp"),
        entry.get("offset"),
    )


def _is_market_history_outbound(message: dict[str, Any]) -> bool:
    name = _event_name(message)
    inner = _inner_name(message)
    if name == "subscribeMessage" and inner in {"candle-generated", "candles-generated"}:
        return True
    if name != "sendMessage":
        return False
    if inner == "get-first-candles":
        return True
    return _find_first_int(message, {"active_id", "activeId"}) is not None and any(
        _find_first_int(message, keys) is not None
        for keys in (
            {"size", "raw_size", "rawSize"},
            {"count", "limit"},
            {"from", "start", "startTime", "start_time"},
            {"to", "end", "endTime", "end_time"},
            {"offset"},
        )
    )


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
    if isinstance(value, str) and value:
        return value
    msg = message.get("msg")
    if isinstance(msg, dict):
        nested = msg.get("request_id") or msg.get("requestId")
        if isinstance(nested, str) and nested:
            return nested
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


def _render_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Historical Request Sequence", ""]
    summary = payload.get("summary", {})
    lines.append(f"total_entries: {summary.get('total_entries', 0)}")
    lines.append(f"by_origin: {summary.get('by_origin', {})}")
    lines.append("")
    lines.append("MANUAL FLOW")
    _append_entries(lines, payload.get("manual_flow", []))
    lines.append("")
    lines.append("PROGRAMMATIC FLOW")
    _append_entries(lines, payload.get("programmatic_flow", []))
    lines.append("")
    lines.append("MISSING IN PROGRAMMATIC FLOW")
    for entry in payload.get("missing_in_programmatic_flow", []):
        lines.append(
            f"- manual_order={entry.get('manual_order')} name={entry.get('name')} inner={entry.get('inner_name')} "
            f"active_id={entry.get('active_id')} raw_size={entry.get('raw_size')} count={entry.get('count')} "
            f"from={entry.get('from')} to={entry.get('to')} offset={entry.get('offset')}"
        )
    lines.append("")
    return "\n".join(lines)


def _append_entries(lines: list[str], entries: list[dict[str, Any]]) -> None:
    if not entries:
        lines.append("- none")
        return
    for entry in entries:
        lines.append(
            f"{entry.get('order')}. name={entry.get('name')} inner={entry.get('inner_name')} "
            f"request_id={entry.get('request_id')} active_id={entry.get('active_id')} raw_size={entry.get('raw_size')} "
            f"count={entry.get('count')} from={entry.get('from_timestamp')} to={entry.get('to_timestamp')} "
            f"offset={entry.get('offset')}"
        )
