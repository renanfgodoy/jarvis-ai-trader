from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Direction = Literal["sent", "received", "unknown"]
SocketClassification = Literal["MARKET_SOCKET", "ACCOUNT_SOCKET", "CHAT_SOCKET", "ANALYTICS_SOCKET", "UNKNOWN_SOCKET"]


@dataclass(frozen=True)
class HarLoadResult:
    path: str
    exists: bool
    size_bytes: int
    valid_json: bool
    entry_count: int
    error: str | None = None
    har: dict[str, Any] | None = None


@dataclass(frozen=True)
class ParsedSocketIOFrame:
    raw_type: str
    frame_kind: str
    event_name: str | None
    payload: Any
    payload_type: str | None
    payload_keys: tuple[str, ...]
    parse_error: str | None = None
    namespace: str | None = None
    ack_id: str | None = None
    args: tuple[Any, ...] = ()


@dataclass
class SocketFrameSummary:
    direction: Direction
    timestamp: str | None
    frame_kind: str
    event_name: str | None
    payload_type: str | None
    payload_keys: tuple[str, ...]
    sample_sanitized: Any


@dataclass
class WebSocketSummary:
    har_path: str
    url_sanitized: str
    host: str
    path: str
    query_keys: tuple[str, ...]
    transport: str | None
    socket_io_version: str | None
    opened_at: str | None
    closed_at: str | None
    frames_sent: int
    frames_received: int
    heartbeat_count: int
    event_names: tuple[str, ...]
    classification: SocketClassification
    frames: tuple[SocketFrameSummary, ...] = field(default_factory=tuple)


@dataclass
class HttpEndpointSummary:
    har_path: str
    host: str
    path: str
    method: str
    status: int | None
    content_type: str | None
    response_shape: Any
    probable_responsibility: str


@dataclass
class EventCatalogEntry:
    event_name: str
    direction: Direction
    count: int
    first_seen: str | None
    last_seen: str | None
    payload_shape: Any
    payload_keys: tuple[str, ...]
    sample_sanitized: Any
    probable_responsibility: str
    confidence: str


@dataclass
class PocketDiscoveryReport:
    har_paths: tuple[str, ...]
    missing_hars: tuple[str, ...]
    total_requests: int
    websocket_count: int
    main_socket: str | None
    protocol: str | None
    sent_events: tuple[str, ...]
    received_events: tuple[str, ...]
    confirmed_preliminary_change_symbol: bool
    sockets: tuple[WebSocketSummary, ...]
    http_endpoints: tuple[HttpEndpointSummary, ...]
    event_catalog: tuple[EventCatalogEntry, ...]
    viability_classification: str
    technical_score: float
    adapter_decision: str
    risks: tuple[str, ...]
    gaps: tuple[str, ...]
