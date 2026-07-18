from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

EnvelopeOrigin = Literal["PAGE_NATIVE", "FRIDAY_PROGRAMMATIC"]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "get_candles_envelope_report.json"
REPORT_TXT = REPORT_DIR / "get_candles_envelope_report.txt"

SENSITIVE_KEYS = {
    "authorization",
    "bearer",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "header",
    "headers",
    "password",
    "refresh_token",
    "secret",
    "ssid",
    "token",
}

SAFE_VALUE_KEYS = {
    "active_id",
    "activeId",
    "count",
    "end",
    "endTime",
    "end_time",
    "from",
    "index",
    "limit",
    "offset",
    "rawSize",
    "raw_size",
    "size",
    "start",
    "startTime",
    "start_time",
    "timestamp",
    "to",
}


@dataclass(frozen=True)
class GetCandlesEnvelopeRecord:
    order: int
    origin: EnvelopeOrigin
    timestamp: int
    request_id: str | None
    name: str | None
    inner_name: str | None
    payload_path: str | None
    paths: dict[str, str]
    shape: dict[str, Any]
    safe_values: dict[str, Any]

    def sanitized(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BootstrapOwnerRecord:
    order: int
    timestamp: int
    owner: str
    active_id: int | None
    raw_size: int | None
    request_id: str | None

    def sanitized(self) -> dict[str, Any]:
        return asdict(self)


class GetCandlesEnvelopeDiagnostic:
    """Captures structural get-candles envelopes without storing raw payloads."""

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
        self._records: list[GetCandlesEnvelopeRecord] = []
        self._bootstrap_owners: list[BootstrapOwnerRecord] = []
        self._next_order = 1
        self._next_owner_order = 1

    @property
    def records(self) -> tuple[GetCandlesEnvelopeRecord, ...]:
        return tuple(self._records)

    @property
    def bootstrap_owners(self) -> tuple[BootstrapOwnerRecord, ...]:
        return tuple(self._bootstrap_owners)

    def clear(self) -> None:
        self._records.clear()
        self._bootstrap_owners.clear()
        self._next_order = 1
        self._next_owner_order = 1
        self._write_if_enabled()

    def observe_outbound(self, message: dict[str, Any], *, origin: EnvelopeOrigin, now_ms: int) -> None:
        if _event_name(message) != "sendMessage" or _inner_name(message) != "get-candles":
            return
        sanitized = _sanitize(message)
        paths = _flatten_types(sanitized)
        shape = _shape(sanitized)
        safe_values = _safe_values(sanitized)
        record = GetCandlesEnvelopeRecord(
            order=self._next_order,
            origin=origin,
            timestamp=now_ms,
            request_id=_request_id(message),
            name=_event_name(message),
            inner_name=_inner_name(message),
            payload_path=_payload_path(message),
            paths=paths,
            shape=shape if isinstance(shape, dict) else {},
            safe_values=safe_values,
        )
        self._next_order += 1
        self._records.append(record)
        self._write_if_enabled()

    def observe_bootstrap_owner(
        self,
        *,
        owner: str,
        active_id: int | None,
        raw_size: int | None,
        request_id: str | None,
        now_ms: int,
    ) -> None:
        self._bootstrap_owners.append(
            BootstrapOwnerRecord(
                order=self._next_owner_order,
                timestamp=now_ms,
                owner=owner,
                active_id=active_id,
                raw_size=raw_size,
                request_id=request_id,
            )
        )
        self._next_owner_order += 1
        self._write_if_enabled()

    def write_reports(self) -> None:
        self._report_json.parent.mkdir(parents=True, exist_ok=True)
        payload = self.sanitized()
        self._report_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._report_txt.write_text(_render_text(payload), encoding="utf-8")

    def sanitized(self) -> dict[str, Any]:
        native = [record.sanitized() for record in self._records if record.origin == "PAGE_NATIVE"]
        programmatic = [record.sanitized() for record in self._records if record.origin == "FRIDAY_PROGRAMMATIC"]
        native_ref = native[-1] if native else None
        programmatic_ref = programmatic[-1] if programmatic else None
        differences = _structural_differences(native_ref, programmatic_ref)
        owners = [record.sanitized() for record in self._bootstrap_owners]
        owner_duplicates = _duplicate_bootstrap_owners(owners)
        categories = Counter(record.origin for record in self._records)
        return {
            "summary": {
                "total_get_candles": len(self._records),
                "by_origin": dict(sorted(categories.items())),
                "native_get_candles_count": len(native),
                "programmatic_get_candles_count": len(programmatic),
                "duplicate_bootstrap_owner_count": len(owner_duplicates),
            },
            "native_envelopes": native,
            "programmatic_envelopes": programmatic,
            "structural_differences": differences,
            "missing_fields": differences.get("missing_in_programmatic", []),
            "duplicate_bootstrap_owners": owner_duplicates,
            "bootstrap_owners": owners,
        }

    def _write_if_enabled(self) -> None:
        if self._auto_write:
            self.write_reports()


def _structural_differences(native: dict[str, Any] | None, programmatic: dict[str, Any] | None) -> dict[str, Any]:
    if native is None and programmatic is None:
        return {
            "status": "NO_GET_CANDLES_OBSERVED",
            "missing_in_programmatic": [],
            "missing_in_native": [],
            "different_types": [],
            "different_payload_path": False,
            "different_message_name": False,
        }
    if native is None:
        return {
            "status": "NATIVE_NOT_OBSERVED",
            "missing_in_programmatic": [],
            "missing_in_native": sorted((programmatic or {}).get("paths", {}).keys()),
            "different_types": [],
            "different_payload_path": False,
            "different_message_name": False,
        }
    if programmatic is None:
        return {
            "status": "PROGRAMMATIC_NOT_OBSERVED",
            "missing_in_programmatic": sorted(native.get("paths", {}).keys()),
            "missing_in_native": [],
            "different_types": [],
            "different_payload_path": False,
            "different_message_name": False,
        }
    native_paths = native.get("paths", {})
    programmatic_paths = programmatic.get("paths", {})
    if not isinstance(native_paths, dict):
        native_paths = {}
    if not isinstance(programmatic_paths, dict):
        programmatic_paths = {}
    native_keys = set(native_paths.keys())
    programmatic_keys = set(programmatic_paths.keys())
    different_types = []
    for path in sorted(native_keys & programmatic_keys):
        if native_paths[path] != programmatic_paths[path]:
            different_types.append({"path": path, "native": native_paths[path], "programmatic": programmatic_paths[path]})
    return {
        "status": "COMPARED",
        "missing_in_programmatic": sorted(native_keys - programmatic_keys),
        "missing_in_native": sorted(programmatic_keys - native_keys),
        "different_types": different_types,
        "different_payload_path": native.get("payload_path") != programmatic.get("payload_path"),
        "different_message_name": native.get("name") != programmatic.get("name") or native.get("inner_name") != programmatic.get("inner_name"),
        "safe_value_differences": _safe_value_differences(native.get("safe_values", {}), programmatic.get("safe_values", {})),
    }


def _safe_value_differences(native_values: Any, programmatic_values: Any) -> list[dict[str, Any]]:
    if not isinstance(native_values, dict) or not isinstance(programmatic_values, dict):
        return []
    differences = []
    for key in sorted(set(native_values) & set(programmatic_values)):
        if native_values[key] != programmatic_values[key]:
            differences.append({"key": key, "native": native_values[key], "programmatic": programmatic_values[key]})
    return differences


def _duplicate_bootstrap_owners(owners: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, Any], set[str]] = {}
    for owner in owners:
        key = (owner.get("active_id"), owner.get("raw_size"))
        if key == (None, None):
            continue
        grouped.setdefault(key, set()).add(str(owner.get("owner")))
    duplicates = []
    for (active_id, raw_size), names in sorted(grouped.items()):
        if len(names) > 1:
            duplicates.append({"active_id": active_id, "raw_size": raw_size, "owners": sorted(names)})
    return duplicates


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if _is_sensitive_key(key):
                continue
            sanitized[key] = _sanitize(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(type(value).__name__)


def _shape(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _shape(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_shape(value[0])] if value else []
    return _type_name(value)


def _flatten_types(value: Any, *, prefix: str = "") -> dict[str, str]:
    if isinstance(value, dict):
        flattened = {prefix: "dict"} if prefix else {}
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            flattened.update(_flatten_types(item, prefix=path))
        return flattened
    if isinstance(value, list):
        flattened = {prefix: "list"} if prefix else {}
        if value:
            flattened.update(_flatten_types(value[0], prefix=f"{prefix}[]"))
        return flattened
    return {prefix: _type_name(value)} if prefix else {}


def _safe_values(value: Any, *, prefix: str = "") -> dict[str, Any]:
    values: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in SAFE_VALUE_KEYS and _safe_scalar(item):
                values[path] = item
            values.update(_safe_values(item, prefix=path))
    elif isinstance(value, list):
        for index, item in enumerate(value[:3]):
            values.update(_safe_values(item, prefix=f"{prefix}[{index}]"))
    return values


def _safe_scalar(value: Any) -> bool:
    return isinstance(value, (int, float, bool, str)) or value is None


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if value is None:
        return "null"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return type(value).__name__


def _payload_path(message: dict[str, Any]) -> str | None:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return None
    for path in ("body", "data", "payload", "params"):
        if path in msg:
            return f"msg.{path}"
    return "msg"


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


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(sensitive in lowered for sensitive in SENSITIVE_KEYS)


def _render_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Exact Get-Candles Envelope", ""]
    summary = payload.get("summary", {})
    lines.append(f"total_get_candles: {summary.get('total_get_candles', 0)}")
    lines.append(f"by_origin: {summary.get('by_origin', {})}")
    lines.append("")
    lines.append("NATIVE ENVELOPE")
    _append_envelopes(lines, payload.get("native_envelopes", []))
    lines.append("")
    lines.append("PROGRAMMATIC ENVELOPE")
    _append_envelopes(lines, payload.get("programmatic_envelopes", []))
    lines.append("")
    lines.append("STRUCTURAL DIFFERENCES")
    differences = payload.get("structural_differences", {})
    lines.append(json.dumps(differences, indent=2, sort_keys=True))
    lines.append("")
    lines.append("MISSING FIELDS")
    missing = payload.get("missing_fields", [])
    if not missing:
        lines.append("- none")
    else:
        for field in missing:
            lines.append(f"- {field}")
    lines.append("")
    lines.append("DUPLICATE BOOTSTRAP OWNERS")
    duplicates = payload.get("duplicate_bootstrap_owners", [])
    if not duplicates:
        lines.append("- none")
    else:
        for duplicate in duplicates:
            lines.append(
                f"- active_id={duplicate.get('active_id')} raw_size={duplicate.get('raw_size')} "
                f"owners={duplicate.get('owners')}"
            )
    lines.append("")
    return "\n".join(lines)


def _append_envelopes(lines: list[str], envelopes: list[dict[str, Any]]) -> None:
    if not envelopes:
        lines.append("- none")
        return
    for envelope in envelopes:
        lines.append(
            f"{envelope.get('order')}. request_id={envelope.get('request_id')} "
            f"name={envelope.get('name')} inner={envelope.get('inner_name')} "
            f"payload_path={envelope.get('payload_path')}"
        )
        lines.append(f"   safe_values={envelope.get('safe_values', {})}")
