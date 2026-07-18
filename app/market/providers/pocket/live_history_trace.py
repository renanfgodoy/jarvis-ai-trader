from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, urlsplit

from app.market.providers.pocket.cdp_models import PocketObservedFrame, PocketObservedSocket
from app.market.providers.pocket.live_schema_trace import structural_shape
from tools.pocket_discovery.models import ParsedSocketIOFrame
from tools.pocket_discovery.sanitizer import sanitize_url
from tools.pocket_parser.chart_parser import audit_update_charts
from tools.pocket_parser.history_parser import parse_history_batch

HISTORY_EVENT_NAMES = {
    "updateHistoryNewFast",
    "updateHistory",
    "updateHistoryNew",
    "loadHistory",
    "history",
    "candles",
    "chart",
    "bars",
    "quotes",
}
HTTP_HISTORY_MARKERS = ("history", "candle", "candles", "chart", "quotes", "bars", "series")


@dataclass
class PocketLiveHistoryTrace:
    observer_started_at: float | None = None
    chrome_started_at: float | None = None
    target_found_at: float | None = None
    target_attached_at: float | None = None
    network_enabled_at: float | None = None
    market_socket_created_at: float | None = None
    market_socket_confirmed_at: float | None = None
    first_change_symbol_at: float | None = None
    first_history_event_at: float | None = None
    first_update_charts_at: float | None = None
    first_update_stream_at: float | None = None
    first_tick_at: float | None = None
    history_candidates: list[dict[str, Any]] = field(default_factory=list)
    update_charts_samples: list[dict[str, Any]] = field(default_factory=list)
    socket_events: dict[str, dict[str, Any]] = field(default_factory=dict)
    http_requests: dict[str, dict[str, Any]] = field(default_factory=dict)
    http_candidates: list[dict[str, Any]] = field(default_factory=list)

    def mark_observer_started(self) -> None:
        self.observer_started_at = self.observer_started_at or time.monotonic()

    def mark_chrome_started(self) -> None:
        self.chrome_started_at = self.chrome_started_at or time.monotonic()

    def mark_target_found(self) -> None:
        self.target_found_at = self.target_found_at or time.monotonic()

    def mark_target_attached(self) -> None:
        self.target_attached_at = self.target_attached_at or time.monotonic()

    def mark_network_enabled(self) -> None:
        self.network_enabled_at = self.network_enabled_at or time.monotonic()

    def mark_market_socket_created(self, timestamp: float | None = None) -> None:
        self.market_socket_created_at = self.market_socket_created_at or timestamp or time.monotonic()

    def mark_market_socket_confirmed(self, timestamp: float | None = None) -> None:
        self.market_socket_confirmed_at = self.market_socket_confirmed_at or timestamp or time.monotonic()

    def record_event(
        self,
        *,
        event_name: str | None,
        payload: object,
        parsed: ParsedSocketIOFrame,
        frame: PocketObservedFrame,
        socket: PocketObservedSocket,
    ) -> None:
        if not event_name:
            return
        self._record_socket_event(socket, event_name, frame.direction)
        if event_name == "changeSymbol":
            self.first_change_symbol_at = self.first_change_symbol_at or frame.timestamp
        elif event_name == "updateStream":
            self.first_update_stream_at = self.first_update_stream_at or frame.timestamp
            self.first_tick_at = self.first_tick_at or frame.timestamp
        elif event_name == "updateCharts":
            self.first_update_charts_at = self.first_update_charts_at or frame.timestamp
            self._record_update_charts(payload, parsed, frame, socket)
        if event_name in HISTORY_EVENT_NAMES or _looks_like_history_name(event_name) or _looks_like_history_shape(payload):
            self._record_history_candidate(event_name, payload, parsed, frame, socket)

    def record_http_event(self, *, method: str, params: dict[str, Any]) -> None:
        if method == "Network.requestWillBeSent":
            self._record_http_request(params)
        elif method == "Network.responseReceived":
            self._record_http_response(params)
        elif method == "Network.loadingFinished":
            request_id = str(params.get("requestId") or "")
            if request_id in self.http_requests:
                self.http_requests[request_id]["loading_finished_at"] = _float_or_none(params.get("timestamp"))

    def history_report(self) -> dict[str, Any]:
        category = self.final_category()
        return {
            "timing": self.timing_report(),
            "history_candidates": self.history_candidates[:50],
            "history_candidates_count": len(self.history_candidates),
            "update_charts_samples": self.update_charts_samples[:20],
            "history_events_confirmed": sum(1 for item in self.history_candidates if item.get("classification") == "CONFIRMED_HISTORY_EVENT"),
            "historical_candles_detected": sum(int(item.get("count") or 0) for item in self.history_candidates if item.get("classification") == "CONFIRMED_HISTORY_EVENT"),
            "final_category": category,
            "analysis_blocked": category != "HISTORY_EVENT_CONFIRMED",
            "analysis_block_reason": None if category == "HISTORY_EVENT_CONFIRMED" else "POCKET_HISTORY_NOT_READY",
            "history_count": 0 if category != "HISTORY_EVENT_CONFIRMED" else None,
        }

    def http_report(self) -> dict[str, Any]:
        candidates = list(self.http_candidates)
        return {
            "candidate_count": len(candidates),
            "candidates": candidates[:100],
            "used_get_response_body": False,
            "headers_recorded": False,
            "body_recorded": False,
            "history_via_http": bool(candidates) and not any(item.get("classification") == "CONFIRMED_HISTORY_EVENT" for item in self.history_candidates),
        }

    def socket_report(self) -> dict[str, Any]:
        return {
            "sockets": list(self.socket_events.values()),
            "history_on_other_socket": any(
                item.get("classification") == "CONFIRMED_HISTORY_EVENT" and item.get("socket_classification") != "MARKET_SOCKET"
                for item in self.history_candidates
            ),
        }

    def timing_report(self) -> dict[str, Any]:
        return {
            "observer_started_at": self.observer_started_at,
            "chrome_started_at": self.chrome_started_at,
            "target_found_at": self.target_found_at,
            "target_attached_at": self.target_attached_at,
            "network_enabled_at": self.network_enabled_at,
            "market_socket_created_at": self.market_socket_created_at,
            "market_socket_confirmed_at": self.market_socket_confirmed_at,
            "first_change_symbol_at": self.first_change_symbol_at,
            "first_history_event_at": self.first_history_event_at,
            "first_update_charts_at": self.first_update_charts_at,
            "first_update_stream_at": self.first_update_stream_at,
            "first_tick_at": self.first_tick_at,
            "attach_classification": self.attach_classification(),
        }

    def final_category(self) -> str:
        confirmed = [item for item in self.history_candidates if item.get("classification") == "CONFIRMED_HISTORY_EVENT"]
        if confirmed:
            if any(item.get("socket_classification") != "MARKET_SOCKET" for item in confirmed):
                return "HISTORY_EVENT_OTHER_SOCKET"
            return "HISTORY_EVENT_CONFIRMED"
        if self.http_candidates and self.first_update_stream_at is not None:
            return "HISTORY_EVENT_HTTP_ONLY"
        if any(item.get("classification") == "AMBIGUOUS_HISTORY_EVENT" for item in self.history_candidates):
            return "HISTORY_EVENT_SCHEMA_AMBIGUOUS"
        if any(item.get("event_name") != "updateHistoryNewFast" for item in self.history_candidates):
            return "HISTORY_EVENT_DIFFERENT_NAME"
        if self.attach_classification() == "ATTACHED_AFTER_TERMINAL_LOAD" and self.first_update_stream_at is not None:
            return "HISTORY_EVENT_MISSED_BEFORE_ATTACH"
        if self.first_update_stream_at is not None:
            return "HISTORY_EVENT_NOT_TRIGGERED"
        return "HISTORY_EVENT_UNKNOWN"

    def attach_classification(self) -> str:
        if self.target_attached_at is None or self.first_update_stream_at is None:
            return "TIMING_UNKNOWN"
        if not _timestamps_are_comparable(self.target_attached_at, self.first_update_stream_at):
            return "TIMING_UNKNOWN"
        if self.first_change_symbol_at is not None and self.target_attached_at <= self.first_change_symbol_at:
            return "ATTACHED_BEFORE_TERMINAL_LOAD"
        if self.first_update_charts_at is not None and self.target_attached_at <= self.first_update_charts_at:
            return "ATTACHED_DURING_TERMINAL_LOAD"
        if self.target_attached_at > self.first_update_stream_at:
            return "ATTACHED_AFTER_TERMINAL_LOAD"
        return "ATTACHED_DURING_TERMINAL_LOAD"

    def _record_history_candidate(
        self,
        event_name: str,
        payload: object,
        parsed: ParsedSocketIOFrame,
        frame: PocketObservedFrame,
        socket: PocketObservedSocket,
    ) -> None:
        batch, rejections = parse_history_batch(payload, source_har="live-cdp", session_index=0, frame_index=len(self.history_candidates))
        shape = structural_shape(payload)
        classification = "CONFIRMED_HISTORY_EVENT" if batch is not None else _classify_history_shape(payload)
        if batch is not None:
            self.first_history_event_at = self.first_history_event_at or frame.timestamp
        self.history_candidates.append(
            {
                "event_name": event_name,
                "direction": frame.direction,
                "timestamp": frame.timestamp,
                "socket_classification": socket.classification,
                "frame_prefix": parsed.raw_type,
                "namespace": parsed.namespace,
                "ack_id_present": parsed.ack_id is not None,
                "classification": classification,
                "count": len(batch.candles) if batch is not None else 0,
                "parser_rejection_codes": [item.code for item in rejections],
                "payload_root_type": type(payload).__name__,
                "payload_depth": _max_depth(payload),
                "list_lengths": shape["list_lengths"],
                "key_paths": shape["key_paths"][:40],
                "candidate_asset_paths": shape["candidate_asset_paths"],
                "candidate_timestamp_paths": shape["candidate_timestamp_paths"],
                "candidate_price_paths": shape["candidate_price_paths"],
            }
        )

    def _record_update_charts(self, payload: object, parsed: ParsedSocketIOFrame, frame: PocketObservedFrame, socket: PocketObservedSocket) -> None:
        shape = structural_shape(payload)
        audit = audit_update_charts(payload)
        self.update_charts_samples.append(
            {
                "timestamp": frame.timestamp,
                "direction": frame.direction,
                "socket_classification": socket.classification,
                "frame_prefix": parsed.raw_type,
                "payload_root_type": type(payload).__name__,
                "payload_depth": _max_depth(payload),
                "key_paths": shape["key_paths"][:50],
                "list_lengths": shape["list_lengths"],
                "candidate_asset_paths": shape["candidate_asset_paths"],
                "candidate_timestamp_paths": shape["candidate_timestamp_paths"],
                "candidate_price_paths": shape["candidate_price_paths"],
                "contains_history": any(item.get("contains_candles") for item in audit),
                "contains_visual_state": any(item.get("contains_visual_state") for item in audit),
                "contains_period": any(item.get("chart_period") or item.get("fast_timeframe") for item in audit),
            }
        )

    def _record_socket_event(self, socket: PocketObservedSocket, event_name: str, direction: str) -> None:
        row = self.socket_events.setdefault(
            socket.request_id,
            {
                "request_id_masked": _mask(socket.request_id),
                "classification": socket.classification,
                "classification_reason": socket.classification_reason,
                "event_names": set(),
                "frames_received": 0,
                "frames_sent": 0,
                "candidate_history_shapes": 0,
                "candidate_market_events": 0,
            },
        )
        row["classification"] = socket.classification
        row["classification_reason"] = socket.classification_reason
        row["event_names"].add(event_name)
        if direction == "received":
            row["frames_received"] += 1
        else:
            row["frames_sent"] += 1
        if event_name in HISTORY_EVENT_NAMES or _looks_like_history_name(event_name):
            row["candidate_history_shapes"] += 1
        if event_name in {"changeSymbol", "updateHistoryNewFast", "updateStream", "updateAssets", "updateCharts", "saveCharts"}:
            row["candidate_market_events"] += 1
        row["event_names"] = set(row["event_names"])

    def _record_http_request(self, params: dict[str, Any]) -> None:
        request = params.get("request") if isinstance(params.get("request"), dict) else {}
        url = str(request.get("url") or "")
        method = str(request.get("method") or "")
        request_id = str(params.get("requestId") or "")
        if not request_id:
            return
        parsed = urlsplit(url)
        candidate_reason = _http_candidate_reason(parsed.path, parsed.query)
        self.http_requests[request_id] = {
            "request_id_masked": _mask(request_id),
            "sanitized_host": parsed.netloc,
            "sanitized_path": parsed.path,
            "sanitized_url": sanitize_url(url),
            "method": method,
            "status": None,
            "content_type": None,
            "initiator_type": _initiator_type(params),
            "timestamp": _float_or_none(params.get("timestamp")),
            "candidate_reason": candidate_reason,
        }

    def _record_http_response(self, params: dict[str, Any]) -> None:
        request_id = str(params.get("requestId") or "")
        response = params.get("response") if isinstance(params.get("response"), dict) else {}
        url = str(response.get("url") or "")
        parsed = urlsplit(url)
        row = self.http_requests.get(request_id)
        if row is None:
            candidate_reason = _http_candidate_reason(parsed.path, parsed.query)
            row = {
                "request_id_masked": _mask(request_id),
                "sanitized_host": parsed.netloc,
                "sanitized_path": parsed.path,
                "sanitized_url": sanitize_url(url),
                "method": None,
                "initiator_type": None,
                "timestamp": _float_or_none(params.get("timestamp")),
                "candidate_reason": candidate_reason,
            }
            self.http_requests[request_id] = row
        row["status"] = response.get("status")
        row["content_type"] = response.get("mimeType")
        if row.get("candidate_reason"):
            self.http_candidates.append(dict(row))


def socket_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in report.get("sockets", []):
        normalized = dict(row)
        if isinstance(normalized.get("event_names"), set):
            normalized["event_names"] = sorted(normalized["event_names"])
        rows.append(normalized)
    return rows


def _looks_like_history_name(event_name: str) -> bool:
    lowered = event_name.lower()
    return any(marker in lowered for marker in ("history", "candle", "candles", "chart", "bars", "quotes"))


def _looks_like_history_shape(payload: object) -> bool:
    if isinstance(payload, list):
        if len(payload) >= 10:
            return True
        return any(isinstance(item, list) and len(item) >= 10 for item in payload[:5])
    if isinstance(payload, dict):
        return any(_looks_like_history_shape(value) for value in payload.values())
    return False


def _classify_history_shape(payload: object) -> str:
    if _looks_like_history_shape(payload):
        return "CANDIDATE_HISTORY_EVENT"
    if isinstance(payload, (list, dict)):
        return "AMBIGUOUS_HISTORY_EVENT"
    return "NON_HISTORY_EVENT"


def _http_candidate_reason(path: str, query: str) -> str | None:
    lowered = f"{path}?{'&'.join(sorted(parse_qs(query)))}".lower()
    for marker in HTTP_HISTORY_MARKERS:
        if marker in lowered:
            return f"PATH_OR_QUERY_CONTAINS_{marker.upper()}"
    return None


def _initiator_type(params: dict[str, Any]) -> str | None:
    initiator = params.get("initiator")
    if isinstance(initiator, dict):
        value = initiator.get("type")
        return str(value) if value is not None else None
    return None


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _timestamps_are_comparable(left: float, right: float) -> bool:
    # CDP event timestamps and local monotonic timestamps can use different
    # epochs. Treat wildly different magnitudes as non-comparable instead of
    # manufacturing a timing conclusion.
    if left == 0 or right == 0:
        return True
    larger = max(abs(left), abs(right))
    smaller = min(abs(left), abs(right))
    return larger / max(smaller, 1.0) < 100


def _max_depth(value: object) -> int:
    if isinstance(value, dict) and value:
        return 1 + max(_max_depth(item) for item in value.values())
    if isinstance(value, list) and value:
        return 1 + max(_max_depth(item) for item in value)
    return 0


def _mask(value: str) -> str:
    if not value:
        return ""
    return f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "[REDACTED]"
