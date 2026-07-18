from __future__ import annotations

import inspect
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

SessionContextAuditOrigin = Literal[
    "PAGE_NATIVE",
    "MARKET_WS",
    "BOOTSTRAP",
    "FOLLOW_POLARIUM",
    "SESSION_RESTORE",
    "DEFAULT_CONTEXT",
    "HISTORICAL_BOOTSTRAP",
    "MANUAL_SELECTION",
    "UNKNOWN",
]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "session_context_audit.json"
REPORT_TXT = REPORT_DIR / "session_context_audit.txt"
MAX_RECORDS = 500


@dataclass
class SessionContextAuditRecord:
    timestamp: int
    kind: str
    file: str
    line: int
    caller: str
    origin: SessionContextAuditOrigin
    reason: str
    old_active_id: int | None = None
    new_active_id: int | None = None
    old_symbol: str | None = None
    new_symbol: str | None = None
    old_raw_size: int | None = None
    new_raw_size: int | None = None
    bucket_exists: bool | None = None
    buckets: tuple[str, ...] = ()
    received_symbol: str | None = None
    received_active_id: int | None = None
    frame: str | None = None
    request_id: str | None = None
    websocket: str | None = None
    target_id: str | None = None

    def sanitized(self) -> dict[str, Any]:
        data = asdict(self)
        data["buckets"] = list(self.buckets)
        return data


class SessionContextAudit:
    """Records sanitized Session Context ownership and CDP context clues."""

    def __init__(
        self,
        *,
        report_json: Path | str = REPORT_JSON,
        report_txt: Path | str = REPORT_TXT,
        auto_write: bool = True,
        max_records: int = MAX_RECORDS,
    ) -> None:
        self._report_json = Path(report_json)
        self._report_txt = Path(report_txt)
        self._auto_write = auto_write
        self._max_records = max_records
        self._records: list[SessionContextAuditRecord] = []

    @property
    def records(self) -> tuple[SessionContextAuditRecord, ...]:
        return tuple(self._records)

    def observe_update(
        self,
        *,
        old_context: dict[str, Any] | None,
        new_context: dict[str, Any] | None,
        origin: SessionContextAuditOrigin,
        reason: str,
        now_ms: int,
        buckets: tuple[str, ...],
        bucket_exists: bool | None,
    ) -> None:
        caller = _caller()
        record = SessionContextAuditRecord(
            timestamp=now_ms,
            kind="SESSION_CONTEXT_UPDATE",
            file=caller["file"],
            line=caller["line"],
            caller=caller["caller"],
            origin=origin,
            reason=_safe_string(reason) or "UNKNOWN",
            old_active_id=_active_id(old_context),
            new_active_id=_active_id(new_context),
            old_symbol=_symbol(old_context),
            new_symbol=_symbol(new_context),
            old_raw_size=_raw_size(old_context),
            new_raw_size=_raw_size(new_context),
            bucket_exists=bucket_exists,
            buckets=buckets,
        )
        self._append(record)

    def observe_cdp_context_event(
        self,
        *,
        message: dict[str, Any],
        origin: SessionContextAuditOrigin,
        frame: str | None,
        request_id: str | None,
        websocket: str | None,
        target_id: str | None,
        now_ms: int,
        buckets: tuple[str, ...],
    ) -> None:
        if not _contains_context_marker(message):
            return
        caller = _caller()
        record = SessionContextAuditRecord(
            timestamp=now_ms,
            kind="CDP_CONTEXT_EVENT",
            file=caller["file"],
            line=caller["line"],
            caller=caller["caller"],
            origin=origin,
            reason=_event_name(message) or "CONTEXT_MARKER_OBSERVED",
            received_active_id=_find_first_int(message, {"active_id", "activeId"}),
            received_symbol=_find_context_symbol(message),
            frame=_safe_string(frame),
            request_id=_safe_string(request_id),
            websocket=_safe_string(websocket),
            target_id=_safe_string(target_id),
            buckets=buckets,
        )
        self._append(record)

    def sanitized(self) -> dict[str, Any]:
        records = [record.sanitized() for record in self._records]
        return {
            "records_count": len(records),
            "origins": dict(Counter(record["origin"] for record in records)),
            "latest_active_id": records[-1].get("new_active_id") if records else None,
            "latest_symbol": records[-1].get("new_symbol") if records else None,
            "latest_raw_size": records[-1].get("new_raw_size") if records else None,
            "records": records,
        }

    def write_reports(self) -> None:
        self._report_json.parent.mkdir(parents=True, exist_ok=True)
        payload = self.sanitized()
        self._report_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self._report_txt.write_text(_format_timeline(payload), encoding="utf-8")

    def _append(self, record: SessionContextAuditRecord) -> None:
        self._records.append(record)
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records :]
        if self._auto_write:
            self.write_reports()


def _format_timeline(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Polarium Session Context Audit", ""]
    for record in payload.get("records", []):
        lines.append(f"{record.get('timestamp')} {record.get('origin')} {record.get('reason')}")
        if record.get("kind") == "SESSION_CONTEXT_UPDATE":
            lines.append(
                f"  SessionContext: {record.get('old_symbol')} {record.get('old_active_id')} raw={record.get('old_raw_size')}"
                f" -> {record.get('new_symbol')} {record.get('new_active_id')} raw={record.get('new_raw_size')}"
            )
            lines.append(f"  CandleStore bucket exists: {'SIM' if record.get('bucket_exists') else 'NÃO'}")
        else:
            lines.append(
                f"  CDP: symbol={record.get('received_symbol')} active_id={record.get('received_active_id')}"
                f" frame={record.get('frame')} requestId={record.get('request_id')} websocket={record.get('websocket')}"
            )
        lines.append(f"  buckets: {', '.join(record.get('buckets') or []) or 'nenhum'}")
        lines.append("------------------")
    return "\n".join(lines)


def _caller() -> dict[str, Any]:
    frame = inspect.stack()[2]
    return {
        "file": _safe_string(frame.filename) or "UNKNOWN",
        "line": int(frame.lineno),
        "caller": _safe_string(frame.function) or "UNKNOWN",
    }


def _active_id(context: dict[str, Any] | None) -> int | None:
    return _as_int((context or {}).get("active_id")) or _as_int((context or {}).get("visible_active_id"))


def _raw_size(context: dict[str, Any] | None) -> int | None:
    return _as_int((context or {}).get("raw_size")) or _as_int((context or {}).get("visible_raw_size"))


def _symbol(context: dict[str, Any] | None) -> str | None:
    return _safe_string((context or {}).get("symbol")) or _safe_string((context or {}).get("visible_symbol")) or _safe_string((context or {}).get("display_name"))


def _event_name(message: dict[str, Any]) -> str | None:
    value = message.get("name")
    if isinstance(value, str) and value != "sendMessage":
        return _safe_string(value)
    msg = message.get("msg")
    if isinstance(msg, dict):
        inner = msg.get("name")
        if isinstance(inner, str):
            return _safe_string(inner)
    return _safe_string(value)


def _contains_context_marker(value: Any) -> bool:
    markers = {"changeSymbol", "setAsset", "asset", "active_id", "activeId", "symbol", "instrument"}
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) in markers:
                return True
            if _contains_context_marker(item):
                return True
    elif isinstance(value, list):
        return any(_contains_context_marker(item) for item in value)
    return False


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


def _find_first_string(value: Any, keys: set[str]) -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys:
                parsed = _safe_string(item)
                if parsed is not None:
                    return parsed
            parsed = _find_first_string(item, keys)
            if parsed is not None:
                return parsed
    if isinstance(value, list):
        for item in value:
            parsed = _find_first_string(item, keys)
            if parsed is not None:
                return parsed
    return None


def _find_context_symbol(value: Any) -> str | None:
    for keys in (
        {"symbol", "ticker"},
        {"instrument", "asset"},
        {"display_name", "displayName", "title"},
    ):
        found = _find_first_string(value, keys)
        if found is not None:
            return found
    return None


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _safe_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.strip().split())
    if not normalized:
        return None
    lowered = normalized.lower()
    if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password")):
        return None
    return normalized[:180]
