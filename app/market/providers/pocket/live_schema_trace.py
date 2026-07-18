from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.market.providers.pocket.cdp_models import PocketObservedFrame, PocketObservedSocket
from tools.pocket_discovery.har_loader import har_entries, load_har
from tools.pocket_discovery.models import ParsedSocketIOFrame
from tools.pocket_discovery.socketio_parser import parse_socketio_frame
from tools.pocket_parser.stream_parser import parse_update_stream

SENSITIVE_MARKERS = ("token", "cookie", "authorization", "bearer", "ssid", "password", "email", "user", "account", "balance")
PRIVATE_HARS = (
    Path(".jarvis_private/pocket_hars/pocketoption.com.har"),
    Path(".jarvis_private/pocket_hars/pocketoption.com(1).har"),
)


@dataclass
class PocketLiveSchemaTrace:
    max_samples_per_event: int = 20
    samples: dict[str, list[dict[str, Any]]] = field(default_factory=lambda: {"updateStream": [], "chafor": []})
    signatures: dict[str, set[str]] = field(default_factory=lambda: {"updateStream": set(), "chafor": set()})
    history_events_observed: int = 0
    first_stream_timestamp: float | None = None
    first_history_timestamp: float | None = None
    observer_started_at: float | None = None
    target_attached_at: float | None = None
    market_socket_confirmed_at: float | None = None

    def mark_observer_started(self) -> None:
        self.observer_started_at = self.observer_started_at or 0.0

    def mark_target_attached(self) -> None:
        self.target_attached_at = self.target_attached_at or 0.0

    def record_event(
        self,
        *,
        event_name: str | None,
        payload: object,
        parsed: ParsedSocketIOFrame,
        frame: PocketObservedFrame,
        socket: PocketObservedSocket,
    ) -> None:
        if event_name == "updateHistoryNewFast":
            self.history_events_observed += 1
            self.first_history_timestamp = self.first_history_timestamp or frame.timestamp
            return
        if event_name not in {"updateStream", "chafor"}:
            return
        if event_name == "updateStream":
            self.first_stream_timestamp = self.first_stream_timestamp or frame.timestamp
            if socket.classification == "MARKET_SOCKET":
                self.market_socket_confirmed_at = self.market_socket_confirmed_at or frame.timestamp
        sample = build_schema_sample(event_name, payload, parsed, frame, socket)
        signature = structural_signature(sample)
        if signature in self.signatures[event_name]:
            return
        if len(self.samples[event_name]) >= self.max_samples_per_event:
            return
        self.signatures[event_name].add(signature)
        self.samples[event_name].append(sample)

    def update_stream_report(self) -> dict[str, Any]:
        har_shapes = har_update_stream_shapes()
        live_shapes = self.samples.get("updateStream", [])
        classification = classify_compatibility(har_shapes, live_shapes)
        return {
            "event_name": "updateStream",
            "samples_count": len(live_shapes),
            "live_samples": live_shapes,
            "har_samples_count": len(har_shapes),
            "har_samples": har_shapes[:20],
            "compatibility": classification,
            "sanitization_audit": sanitization_audit(live_shapes),
            "parser_v11_expected_schema": "[asset, timestamp, price]",
            "parser_rejection_summary": rejection_summary(live_shapes),
            "cause_ticks_zero": cause_ticks_zero(live_shapes),
        }

    def chafor_report(self) -> dict[str, Any]:
        samples = self.samples.get("chafor", [])
        return {
            "event_name": "chafor",
            "samples_count": len(samples),
            "samples": samples,
            "classification": classify_chafor(samples),
            "routed_as_tick": False,
            "evidence": "chafor is cataloged separately and is not converted to PocketRealtimeTick.",
        }

    def history_absence_report(self, *, market_socket_found: bool) -> dict[str, Any]:
        if self.history_events_observed:
            category = "HISTORY_OBSERVED"
        elif market_socket_found:
            category = "HISTORY_EVENT_NOT_OBSERVED"
        else:
            category = "HISTORY_EVENT_UNKNOWN"
        return {
            "category": category,
            "history_events_observed": self.history_events_observed,
            "observer_started_at": self.observer_started_at,
            "target_attached_at": self.target_attached_at,
            "market_socket_confirmed_at": self.market_socket_confirmed_at,
            "first_stream_event_at": self.first_stream_timestamp,
            "first_history_event_at": self.first_history_timestamp,
            "notes": "No historical event is replayed or requested by Friday in this sprint.",
        }


def build_schema_sample(
    event_name: str,
    payload: object,
    parsed: ParsedSocketIOFrame,
    frame: PocketObservedFrame,
    socket: PocketObservedSocket,
) -> dict[str, Any]:
    shape = structural_shape(payload)
    ticks, rejections = parse_update_stream(payload, source_har="live-cdp", session_index=0, frame_index=0, sequence_start=0) if event_name == "updateStream" else ([], [])
    return {
        "timestamp_observed": frame.timestamp,
        "event_name": event_name,
        "direction": frame.direction,
        "socket_classification": socket.classification,
        "frame_prefix": parsed.raw_type,
        "engineio_type": parsed.raw_type[:1],
        "socketio_type": parsed.raw_type,
        "namespace": parsed.namespace,
        "namespace_present": parsed.namespace is not None,
        "ack_id_present": parsed.ack_id is not None,
        "args_count": len(parsed.args),
        "payload_root_type": type(payload).__name__,
        "payload_depth": max_depth(payload),
        "payload_length": len(payload) if isinstance(payload, (list, dict, tuple)) else None,
        "top_level_key_names": top_level_keys(payload),
        "nested_key_paths": shape["key_paths"],
        "value_types": shape["value_types"],
        "list_lengths": shape["list_lengths"],
        "string_patterns": shape["string_patterns"],
        "numeric_ranges": shape["numeric_ranges"],
        "candidate_asset_paths": shape["candidate_asset_paths"],
        "candidate_timestamp_paths": shape["candidate_timestamp_paths"],
        "candidate_price_paths": shape["candidate_price_paths"],
        "parser_result": "ACCEPTED" if ticks else "REJECTED",
        "rejection_code": rejections[0].code if rejections else None,
    }


def structural_shape(payload: object) -> dict[str, Any]:
    acc: dict[str, Any] = {
        "key_paths": [],
        "value_types": {},
        "list_lengths": {},
        "string_patterns": {},
        "numeric_ranges": {},
        "candidate_asset_paths": [],
        "candidate_timestamp_paths": [],
        "candidate_price_paths": [],
    }
    visit(payload, "$", acc)
    acc["key_paths"] = sorted(set(acc["key_paths"]))[:80]
    for key in ("candidate_asset_paths", "candidate_timestamp_paths", "candidate_price_paths"):
        acc[key] = sorted(set(acc[key]))[:40]
    return acc


def visit(value: object, path: str, acc: dict[str, Any]) -> None:
    acc["value_types"][path] = type(value).__name__
    if isinstance(value, dict):
        for key, item in value.items():
            safe = safe_key(str(key))
            child = f"{path}.{safe}"
            acc["key_paths"].append(child)
            visit(item, child, acc)
        return
    if isinstance(value, list):
        acc["list_lengths"][path] = len(value)
        for index, item in enumerate(value[:8]):
            visit(item, f"{path}[]", acc)
        return
    if isinstance(value, str):
        acc["string_patterns"][path] = classify_string(value)
        if looks_like_asset(value):
            acc["candidate_asset_paths"].append(path)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        acc["numeric_ranges"][path] = numeric_class(value)
        lowered = path.lower()
        if "time" in lowered or 1_000_000_000 <= float(value) <= 4_000_000_000:
            acc["candidate_timestamp_paths"].append(path)
        if any(marker in lowered for marker in ("price", "value", "rate", "close", "bid", "ask")) or 0 < float(value) < 1_000_000:
            acc["candidate_price_paths"].append(path)


def max_depth(value: object) -> int:
    if isinstance(value, dict) and value:
        return 1 + max(max_depth(item) for item in value.values())
    if isinstance(value, list) and value:
        return 1 + max(max_depth(item) for item in value)
    return 0


def numeric_class(value: int | float) -> str:
    number = float(value)
    if 1_000_000_000 <= number <= 4_000_000_000:
        return "epoch_seconds"
    if 0 < number < 1:
        return "positive_decimal_lt_1"
    if 1 <= number < 1_000:
        return "positive_number_lt_1000"
    if number >= 1_000:
        return "positive_number_gte_1000"
    return "non_positive_or_unknown"


def top_level_keys(payload: object) -> list[str]:
    if isinstance(payload, dict):
        return sorted(safe_key(str(key)) for key in payload.keys())[:40]
    return []


def safe_key(key: str) -> str:
    lowered = key.lower()
    if any(marker in lowered for marker in SENSITIVE_MARKERS):
        return "[REDACTED_KEY]"
    return key


def classify_string(value: str) -> str:
    lowered = value.lower()
    if any(marker in lowered for marker in SENSITIVE_MARKERS):
        return "[REDACTED]"
    if looks_like_asset(value):
        return value
    if value.startswith(("http://", "https://", "ws://", "wss://")):
        return "url"
    if len(value) > 32:
        return "string_long"
    return "string"


def looks_like_asset(value: str) -> bool:
    if not value or len(value) > 24:
        return False
    return value.endswith("_otc") or value.isupper() and any(char.isalpha() for char in value)


def structural_signature(sample: dict[str, Any]) -> str:
    basis = {
        "event": sample.get("event_name"),
        "root": sample.get("payload_root_type"),
        "keys": sample.get("nested_key_paths"),
        "lists": sample.get("list_lengths"),
        "types": sample.get("value_types"),
        "args": sample.get("args_count"),
        "namespace": sample.get("namespace_present"),
        "ack": sample.get("ack_id_present"),
    }
    return json.dumps(basis, sort_keys=True, ensure_ascii=False)


def har_update_stream_shapes(paths: tuple[Path, ...] = PRIVATE_HARS) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        loaded = load_har(path)
        if not loaded.har:
            continue
        for entry in har_entries(loaded.har):
            messages = entry.get("_webSocketMessages") or entry.get("_websocketMessages") or entry.get("webSocketMessages") or []
            if not isinstance(messages, list):
                continue
            pending_event: str | None = None
            for message in messages:
                parsed = parse_socketio_frame(str(message.get("data") or ""))
                event_name = parsed.event_name
                payload = parsed.payload
                if parsed.frame_kind == "SOCKET_IO_BINARY_EVENT" and event_name == "updateStream":
                    pending_event = event_name
                    continue
                if parsed.frame_kind == "ENCODED_JSON" and pending_event:
                    event_name = pending_event
                    pending_event = None
                if event_name != "updateStream":
                    continue
                socket = _synthetic_socket()
                frame = PocketObservedFrame("har", "har", "received", None, "")
                sample = build_schema_sample("updateStream", payload, parsed, frame, socket)
                signature = structural_signature(sample)
                if signature in seen:
                    continue
                seen.add(signature)
                samples.append(sample)
                if len(samples) >= 20:
                    return samples
    return samples


def classify_compatibility(har_shapes: list[dict[str, Any]], live_shapes: list[dict[str, Any]]) -> str:
    if not har_shapes or not live_shapes:
        return "INSUFFICIENT_EVIDENCE"
    har_signatures = {structural_signature(shape) for shape in har_shapes}
    live_signatures = {structural_signature(shape) for shape in live_shapes}
    if har_signatures & live_signatures:
        return "IDENTICAL"
    live_has_candidates = any(shape.get("candidate_asset_paths") and shape.get("candidate_timestamp_paths") and shape.get("candidate_price_paths") for shape in live_shapes)
    if live_has_candidates:
        return "SCHEMA_VARIANT"
    return "INCOMPATIBLE"


def sanitization_audit(samples: list[dict[str, Any]]) -> dict[str, bool]:
    paths = [path for sample in samples for path in sample.get("candidate_asset_paths", []) + sample.get("candidate_timestamp_paths", []) + sample.get("candidate_price_paths", [])]
    return {
        "asset_preserved": any(path for sample in samples for path in sample.get("candidate_asset_paths", [])),
        "timestamp_preserved": any(path for sample in samples for path in sample.get("candidate_timestamp_paths", [])),
        "price_preserved": any(path for sample in samples for path in sample.get("candidate_price_paths", [])),
        "sensitive_paths_redacted": not any(any(marker in path.lower() for marker in SENSITIVE_MARKERS) for path in paths),
    }


def rejection_summary(samples: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for sample in samples:
        code = sample.get("rejection_code")
        if code:
            summary[str(code)] = summary.get(str(code), 0) + 1
    return summary


def cause_ticks_zero(samples: list[dict[str, Any]]) -> str:
    if not samples:
        return "INSUFFICIENT_EVIDENCE"
    if all(sample.get("parser_result") == "REJECTED" for sample in samples):
        return "PARSER_REJECTED_LIVE_SCHEMA"
    return "TICKS_NOT_ZERO_OR_PARTIAL"


def classify_chafor(samples: list[dict[str, Any]]) -> str:
    if not samples:
        return "UNKNOWN"
    joined_paths = " ".join(path for sample in samples for path in sample.get("nested_key_paths", []))
    if "asset" in joined_paths.lower() or any(sample.get("candidate_asset_paths") for sample in samples):
        return "MARKET_CONTROL"
    return "UNKNOWN"


def _synthetic_socket() -> PocketObservedSocket:
    return PocketObservedSocket("har", "har", "har", "har", "har", (), classification="MARKET_SOCKET", classification_reason="HAR_SAMPLE")
