from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from urllib.parse import parse_qs, urlsplit

from app.market.providers.pocket.cdp_client import PocketCDPClient
from app.market.providers.pocket.cdp_models import ObserverState, PocketCDPEvent, PocketObservedFrame, PocketObservedSocket
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.live_history_trace import PocketLiveHistoryTrace
from app.market.providers.pocket.live_period_trace import PocketLivePeriodTrace
from app.market.providers.pocket.live_schema_trace import PocketLiveSchemaTrace
from app.market.providers.pocket.models import PocketDomainEvent
from app.market.providers.pocket.target_manager import PocketTargetManager
from tools.pocket_discovery.sanitizer import sanitize, sanitize_url
from tools.pocket_discovery.socketio_parser import parse_socketio_frame
from tools.pocket_parser.asset_parser import parse_change_symbol, parse_update_assets
from tools.pocket_parser.chart_parser import audit_update_charts
from tools.pocket_parser.history_parser import parse_history_batch
from tools.pocket_parser.stream_parser import parse_update_stream

ALLOWED_MARKET_EVENTS = {"changeSymbol", "updateHistoryNewFast", "updateStream", "updateAssets", "updateCharts", "saveCharts"}
TRACE_EVENTS = {
    "changeSymbol",
    "updateHistoryNewFast",
    "updateHistory",
    "updateHistoryNew",
    "loadHistory",
    "history",
    "candles",
    "chart",
    "bars",
    "quotes",
    "updateStream",
    "updateAssets",
    "updateCharts",
    "chafor",
}
SENSITIVE_EVENTS = {"auth", "auth/success", "profile", "balance", "account"}
AUXILIARY_EVENTS = {"ping", "pong", "ping-server", "connect", "disconnect", "reconnect"}
MARKET_HOST_PREFIX = "api-"
MARKET_HOST_SUFFIX = ".po.market"


class PocketCDPObservationTransport:
    def __init__(
        self,
        client: PocketCDPClient,
        *,
        config: PocketProviderConfig | None = None,
        target_manager: PocketTargetManager | None = None,
    ) -> None:
        self.client = client
        self.config = config or PocketProviderConfig()
        self.target_manager = target_manager or PocketTargetManager(self.config.pocket_trade_url)
        self._queue: deque[PocketDomainEvent] = deque()
        self.domain_event_handler: Callable[[PocketDomainEvent], None] | None = None
        self._running = False
        self.observer_state: ObserverState = "STOPPED"
        self.target_id: str | None = None
        self.target_url_sanitized: str | None = None
        self.sockets: dict[str, PocketObservedSocket] = {}
        self.market_socket_request_id: str | None = None
        self.frames_sent_observed = 0
        self.frames_received_observed = 0
        self.events_parsed = 0
        self.change_symbol_events = 0
        self.history_batches = 0
        self.historical_candles = 0
        self.stream_events = 0
        self.ticks = 0
        self.asset_catalog_events = 0
        self.contexts_published = 0
        self.sensitive_events_discarded = 0
        self.non_market_frames_ignored = 0
        self.unknown_events = 0
        self.errors: list[str] = []
        self.payload_shapes: dict[str, dict[str, object]] = {}
        self.live_schema_trace = PocketLiveSchemaTrace()
        self.live_history_trace = PocketLiveHistoryTrace()
        self.live_period_trace = PocketLivePeriodTrace()
        self.last_update: float | None = None
        self._pending_binary_event_name: dict[str, str] = {}

    def start(self) -> None:
        self._running = True
        self.live_schema_trace.mark_observer_started()
        self.live_history_trace.mark_observer_started()
        self.observer_state = "WAITING_TARGET"
        target = self._wait_for_target()
        if target is None:
            self.observer_state = "DEGRADED"
            self.errors.append("POCKET_TARGET_NOT_FOUND")
            return
        self.live_history_trace.mark_target_found()
        self.target_id = target.target_id
        self.target_url_sanitized = sanitize_url(target.url)
        self.client.attach_target(target.target_id)
        self.live_schema_trace.mark_target_attached()
        self.live_history_trace.mark_target_attached()
        self.client.enable_network()
        self.live_history_trace.mark_network_enabled()
        self.observer_state = "WAITING_MARKET_SOCKET"
        while True:
            event = self.client.next_event()
            if event is None:
                break
            self._handle_cdp_event(event)
        if self.market_socket_request_id:
            self.observer_state = "OBSERVING"

    def _wait_for_target(self, *, timeout_seconds: float = 30.0):
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            target = self.target_manager.select_target(self.client.list_targets())
            if target is not None:
                return target
            time.sleep(0.25)
        return None

    def stop(self) -> None:
        self._running = False
        self._queue.clear()
        self.client.close()
        self.observer_state = "STOPPED"

    def is_running(self) -> bool:
        return self._running

    def next_event(self) -> PocketDomainEvent | None:
        if not self._running or not self._queue:
            return None
        return self._queue.popleft()

    def set_domain_event_handler(self, handler: Callable[[PocketDomainEvent], None] | None) -> None:
        self.domain_event_handler = handler

    def status(self) -> dict:
        return {
            "transport": "CDP_OBSERVATION",
            "running": self._running,
            "observer_state": self.observer_state,
            "target_found": self.target_id is not None,
            "target_url_sanitized": self.target_url_sanitized,
            "sockets_observed": len(self.sockets),
            "market_socket_found": self.market_socket_request_id is not None,
            "market_events_received": self.events_parsed,
            "market_events_processed": self.events_parsed - self.sensitive_events_discarded,
            "sensitive_events_discarded": self.sensitive_events_discarded,
            "unknown_events": self.unknown_events,
            "last_error_code": self.errors[-1] if self.errors else None,
            "last_update": self.last_update,
            "frames_sent_observed": self.frames_sent_observed,
            "frames_received_observed": self.frames_received_observed,
        }

    def _handle_cdp_event(self, event: PocketCDPEvent) -> None:
        method = event.method
        params = event.params
        if method == "Network.webSocketCreated":
            self._socket_created(params)
        elif method == "Network.webSocketFrameReceived":
            self._frame_observed(params, "received")
        elif method == "Network.webSocketFrameSent":
            self._frame_observed(params, "sent")
        elif method in {"Network.requestWillBeSent", "Network.responseReceived", "Network.loadingFinished"}:
            self.live_history_trace.record_http_event(method=method, params=params)

    def _socket_created(self, params: dict) -> None:
        request_id = str(params.get("requestId") or "")
        url = str(params.get("url") or "")
        if not request_id:
            return
        parsed = urlsplit(url)
        query = parse_qs(parsed.query)
        socket = PocketObservedSocket(
            request_id=request_id,
            target_id=self.target_id or "unknown",
            url_sanitized=sanitize_url(url),
            host=parsed.netloc,
            path=parsed.path,
            query_keys=tuple(sorted(query)),
            classification="CANDIDATE" if _looks_like_market_socket(parsed.netloc, parsed.path, query) else "UNKNOWN",
            classification_reason="URL_CANDIDATE" if _looks_like_market_socket(parsed.netloc, parsed.path, query) else "NO_MARKET_EVIDENCE",
        )
        self.sockets[request_id] = socket
        if socket.classification == "CANDIDATE":
            self.live_history_trace.mark_market_socket_created(_float_or_none(params.get("timestamp")))

    def _frame_observed(self, params: dict, direction: str) -> None:
        request_id = str(params.get("requestId") or "")
        response = params.get("response") if isinstance(params.get("response"), dict) else {}
        payload = str(response.get("payloadData") or "")
        timestamp = _float_or_none(params.get("timestamp"))
        if direction == "sent":
            self.frames_sent_observed += 1
        else:
            self.frames_received_observed += 1
        frame = PocketObservedFrame(request_id, self.target_id or "unknown", direction, timestamp, payload)
        socket = self.sockets.get(request_id)
        parsed = parse_socketio_frame(frame.payload_data)
        event_name = parsed.event_name
        effective_payload = parsed.payload
        if parsed.frame_kind == "ENCODED_JSON" and request_id in self._pending_binary_event_name:
            event_name = self._pending_binary_event_name.pop(request_id)
        if event_name in SENSITIVE_EVENTS or _payload_shape_looks_sensitive(effective_payload):
            self.sensitive_events_discarded += 1
            return
        if socket is None:
            socket = self._infer_socket_from_frame(request_id, event_name)
            if socket is None:
                self.non_market_frames_ignored += 1
                return
        if direction == "sent":
            socket.frames_sent_count += 1
        else:
            socket.frames_received_count += 1
        if parsed.frame_kind == "SOCKET_IO_BINARY_EVENT" and event_name:
            self._pending_binary_event_name[request_id] = event_name
            return
        if event_name:
            socket.event_names.add(event_name)
            self.events_parsed += 1
        if _is_market_evidence_socket(socket, event_name):
            socket.classification = "MARKET_SOCKET"
            if socket.classification_reason != "MARKET_EVENT_WITHOUT_SOCKET_CREATED":
                socket.classification_reason = "URL_AND_MARKET_EVENT_EVIDENCE"
            self.market_socket_request_id = socket.request_id
            self.live_history_trace.mark_market_socket_confirmed(frame.timestamp)
        elif socket.classification == "UNKNOWN" and event_name:
            socket.classification = "AUXILIARY_SOCKET"
            socket.classification_reason = "NON_MARKET_EVENT"
        if request_id != self.market_socket_request_id and event_name not in {"changeSymbol"}:
            if event_name in TRACE_EVENTS:
                self.live_history_trace.record_event(event_name=event_name, payload=effective_payload, parsed=parsed, frame=frame, socket=socket)
                self.live_period_trace.record_event(event_name=event_name, payload=effective_payload, parsed=parsed, frame=frame, socket=socket)
            self.non_market_frames_ignored += 1
            return
        if event_name in TRACE_EVENTS:
            self.live_schema_trace.record_event(event_name=event_name, payload=effective_payload, parsed=parsed, frame=frame, socket=socket)
            self.live_history_trace.record_event(event_name=event_name, payload=effective_payload, parsed=parsed, frame=frame, socket=socket)
            self.live_period_trace.record_event(event_name=event_name, payload=effective_payload, parsed=parsed, frame=frame, socket=socket)
        if event_name in AUXILIARY_EVENTS:
            return
        if event_name not in ALLOWED_MARKET_EVENTS:
            self.unknown_events += 1
            return
        sanitize(effective_payload)
        if event_name:
            self.payload_shapes.setdefault(event_name, _payload_shape(effective_payload))
        self._route_allowed_event(event_name, effective_payload, frame)

    def _route_allowed_event(self, event_name: str, payload: object, frame: PocketObservedFrame) -> None:
        try:
            if event_name == "changeSymbol":
                changed = parse_change_symbol(payload, frame.timestamp)
                self.change_symbol_events += 1
                self.contexts_published += 1
                self._publish(PocketDomainEvent("changeSymbol", changed, source="cdp", sequence=self.events_parsed))
            elif event_name == "updateHistoryNewFast":
                batch, rejections = parse_history_batch(payload, source_har="cdp", session_index=0, frame_index=self.events_parsed)
                if batch is not None:
                    self.history_batches += 1
                    self.historical_candles += len(batch.candles)
                    self._publish(PocketDomainEvent("updateHistoryNewFast", batch, source="cdp", sequence=self.events_parsed))
                if rejections:
                    self.errors.extend(rejection.code for rejection in rejections)
            elif event_name == "updateStream":
                ticks, rejections = parse_update_stream(payload, source_har="cdp", session_index=0, frame_index=self.events_parsed, sequence_start=self.ticks)
                self.stream_events += 1
                self.ticks += len(ticks)
                for tick in ticks:
                    self._publish(PocketDomainEvent("updateStream", tick, source="cdp", sequence=self.events_parsed))
                if rejections:
                    self.errors.extend(rejection.code for rejection in rejections)
            elif event_name == "updateAssets":
                assets = parse_update_assets(payload)
                self.asset_catalog_events += 1
                self._publish(PocketDomainEvent("updateAssets", tuple(assets), source="cdp", sequence=self.events_parsed))
            elif event_name == "updateCharts":
                self._publish(PocketDomainEvent("updateCharts", audit_update_charts(payload), source="cdp", sequence=self.events_parsed))
            elif event_name == "saveCharts":
                return
            self.last_update = frame.timestamp
        except ValueError as error:
            self.errors.append(str(error))

    def _publish(self, event: PocketDomainEvent) -> None:
        if self.domain_event_handler is not None:
            self.domain_event_handler(event)
            return
        self._queue.append(event)

    def _infer_socket_from_frame(self, request_id: str, event_name: str | None) -> PocketObservedSocket | None:
        if not request_id or event_name not in ALLOWED_MARKET_EVENTS:
            return None
        socket = PocketObservedSocket(
            request_id=request_id,
            target_id=self.target_id or "unknown",
            url_sanitized="unknown",
            host="unknown",
            path="unknown",
            query_keys=(),
            classification="MARKET_SOCKET",
            classification_reason="MARKET_EVENT_WITHOUT_SOCKET_CREATED",
        )
        socket.event_names.add(event_name)
        self.sockets[request_id] = socket
        self.market_socket_request_id = request_id
        self.live_history_trace.mark_market_socket_confirmed()
        return socket


def _looks_like_market_socket(host: str, path: str, query: dict[str, list[str]]) -> bool:
    return host.startswith(MARKET_HOST_PREFIX) and host.endswith(MARKET_HOST_SUFFIX) and "/socket.io/" in path and query.get("EIO") == ["4"] and query.get("transport") == ["websocket"]


def _is_market_evidence_socket(socket: PocketObservedSocket, event_name: str | None) -> bool:
    return socket.classification in {"CANDIDATE", "MARKET_SOCKET"} and event_name in {"updateStream", "updateHistoryNewFast", "updateAssets", "changeSymbol"}


def _payload_shape_looks_sensitive(payload: object) -> bool:
    text = str(payload).lower()
    return any(marker in text for marker in ("token", "cookie", "authorization", "bearer", "ssid", "password", "balance", "account", "profile"))


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _payload_shape(payload: object) -> dict[str, object]:
    if isinstance(payload, list):
        first = payload[0] if payload else None
        shape: dict[str, object] = {"type": "list", "length": len(payload), "first_type": type(first).__name__ if first is not None else None}
        if isinstance(first, list):
            shape["first_length"] = len(first)
            shape["first_item_types"] = [type(item).__name__ for item in first[:8]]
        elif isinstance(first, dict):
            shape["first_keys"] = sorted(str(key) for key in first.keys())[:12]
        return shape
    if isinstance(payload, dict):
        return {"type": "dict", "keys": sorted(str(key) for key in payload.keys())[:12]}
    return {"type": type(payload).__name__}
