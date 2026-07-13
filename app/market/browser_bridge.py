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
        "candles",
        "get-first-candles",
        "first-candles",
        "candle-generated",
        "candles-generated",
        "sendMessage",
        "subscribeMessage",
        "historical-transport-discovery",
        "runtime-store-discovery",
        "timeSync",
    }
)

PIPELINE_EVENTS = frozenset({"first-candles", "candle-generated", "candles-generated"})
HISTORICAL_DISCOVERY_EVENTS = frozenset({"candles", "candles-generated", "get-first-candles", "first-candles", "sendMessage", "subscribeMessage"})

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
STRUCTURE_MAX_DEPTH = 6
STRUCTURE_MAX_PATHS = 80
OUTBOUND_SHAPE_LIMIT = 8
OHLC_MARKERS = ("open", "close", "min", "max", "high", "low", "o", "c", "h", "l")
OUTBOUND_FIELD_NAMES = ("active_id", "activeId", "size", "raw_size", "rawSize", "count", "from", "to", "limit", "offset", "chunk_size", "chunkSize")
TRANSPORT_SHAPE_LIMIT = 8
RUNTIME_STORE_CANDIDATE_LIMIT = 12


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
class HistoricalFirstCandlesDiagnostic:
    first_candles_seen_main: int = 0
    first_candles_relayed: int = 0
    first_candles_received_backend: int = 0
    first_candles_adapter_accepted: int = 0
    first_candles_parsed: int = 0
    first_candles_stored: int = 0
    first_candles_collection_count: int = 0
    first_candles_last_error_code: str | None = None
    event_name: str | None = None
    direction: str | None = None
    top_level_type: str | None = None
    top_level_keys: tuple[str, ...] = ()
    msg_type: str | None = None
    msg_keys: tuple[str, ...] = ()
    body_type: str | None = None
    body_keys: tuple[str, ...] = ()
    candidate_collection_path: str | None = None
    candidate_collection_length: int | None = None
    received_at: int | float | str | None = None
    relay_ready_at: int | float | str | None = None
    websocket_created_at: int | float | str | None = None
    parsed_count: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    rejected_count: int = 0
    stored_count: int = 0
    ignored_count: int = 0
    updated_count: int = 0
    route_status: str | None = None
    pipeline_success: bool | None = None
    pipeline_errors: tuple[str, ...] = ()
    distinct_active_ids: tuple[int, ...] = ()
    distinct_raw_sizes: tuple[int, ...] = ()

    def sanitized(self) -> dict[str, Any]:
        return {
            "first_candles_seen_main": self.first_candles_seen_main,
            "first_candles_relayed": self.first_candles_relayed,
            "first_candles_received_backend": self.first_candles_received_backend,
            "first_candles_adapter_accepted": self.first_candles_adapter_accepted,
            "first_candles_parsed": self.first_candles_parsed,
            "first_candles_stored": self.first_candles_stored,
            "first_candles_collection_count": self.first_candles_collection_count,
            "first_candles_last_error_code": self.first_candles_last_error_code,
            "event_name": self.event_name,
            "direction": self.direction,
            "top_level_type": self.top_level_type,
            "top_level_keys": list(self.top_level_keys),
            "msg_type": self.msg_type,
            "msg_keys": list(self.msg_keys),
            "body_type": self.body_type,
            "body_keys": list(self.body_keys),
            "candidate_collection_path": self.candidate_collection_path,
            "candidate_collection_length": self.candidate_collection_length,
            "received_at": self.received_at,
            "relay_ready_at": self.relay_ready_at,
            "websocket_created_at": self.websocket_created_at,
            "parsed_count": self.parsed_count,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "rejected_count": self.rejected_count,
            "stored_count": self.stored_count,
            "ignored_count": self.ignored_count,
            "updated_count": self.updated_count,
            "route_status": self.route_status,
            "pipeline_success": self.pipeline_success,
            "pipeline_errors": list(self.pipeline_errors),
            "distinct_active_ids": list(self.distinct_active_ids),
            "distinct_raw_sizes": list(self.distinct_raw_sizes),
        }


@dataclass
class HistoricalSeriesDiscovery:
    candidate_events_seen: int = 0
    candidate_requests_seen: int = 0
    candidate_responses_seen: int = 0
    last_request_event_name: str | None = None
    last_response_event_name: str | None = None
    last_collection_path: str | None = None
    last_collection_length: int | None = None
    last_distinct_timestamps: int = 0
    last_distinct_raw_sizes: int = 0
    last_distinct_active_ids: int = 0
    historical_series_confirmed: bool = False
    historical_series_event_name: str | None = None
    historical_series_request_ref: str | None = None
    last_error_code: str | None = None

    def sanitized(self) -> dict[str, Any]:
        return {
            "candidate_events_seen": self.candidate_events_seen,
            "candidate_requests_seen": self.candidate_requests_seen,
            "candidate_responses_seen": self.candidate_responses_seen,
            "last_request_event_name": self.last_request_event_name,
            "last_response_event_name": self.last_response_event_name,
            "last_collection_path": self.last_collection_path,
            "last_collection_length": self.last_collection_length,
            "last_distinct_timestamps": self.last_distinct_timestamps,
            "last_distinct_raw_sizes": self.last_distinct_raw_sizes,
            "last_distinct_active_ids": self.last_distinct_active_ids,
            "historical_series_confirmed": self.historical_series_confirmed,
            "historical_series_event_name": self.historical_series_event_name,
            "historical_series_request_ref": self.historical_series_request_ref,
            "last_error_code": self.last_error_code,
        }


@dataclass
class CandlesGeneratedDiagnostic:
    seen_main: int = 0
    relayed: int = 0
    received_backend: int = 0
    top_level_type: str | None = None
    top_level_keys: tuple[str, ...] = ()
    msg_type: str | None = None
    msg_keys: tuple[str, ...] = ()
    body_type: str | None = None
    body_keys: tuple[str, ...] = ()
    nested_array_paths: tuple[str, ...] = ()
    nested_object_paths: tuple[str, ...] = ()
    candidate_collection_path: str | None = None
    candidate_collection_type: str | None = None
    candidate_collection_length: int | None = None
    distinct_timestamps: int = 0
    distinct_raw_sizes: int = 0
    distinct_active_ids: int = 0
    request_ref: str | None = None
    direction: str | None = None
    received_at: int | float | str | None = None
    last_error_code: str | None = None
    historical_series_confirmed: bool = False

    def sanitized(self) -> dict[str, Any]:
        return {
            "seen_main": self.seen_main,
            "relayed": self.relayed,
            "received_backend": self.received_backend,
            "top_level_type": self.top_level_type,
            "top_level_keys": list(self.top_level_keys),
            "msg_type": self.msg_type,
            "msg_keys": list(self.msg_keys),
            "body_type": self.body_type,
            "body_keys": list(self.body_keys),
            "nested_array_paths": list(self.nested_array_paths),
            "nested_object_paths": list(self.nested_object_paths),
            "candidate_collection_path": self.candidate_collection_path,
            "candidate_collection_type": self.candidate_collection_type,
            "candidate_collection_length": self.candidate_collection_length,
            "distinct_timestamps": self.distinct_timestamps,
            "distinct_raw_sizes": self.distinct_raw_sizes,
            "distinct_active_ids": self.distinct_active_ids,
            "request_ref": self.request_ref,
            "direction": self.direction,
            "received_at": self.received_at,
            "last_error_code": self.last_error_code,
            "historical_series_confirmed": self.historical_series_confirmed,
        }


@dataclass
class OutboundCandleRequestDiagnostic:
    seen_main: int = 0
    relayed: int = 0
    event_name: str | None = None
    inner_event_name: str | None = None
    direction: str | None = None
    top_level_type: str | None = None
    top_level_keys: tuple[str, ...] = ()
    msg_type: str | None = None
    msg_keys: tuple[str, ...] = ()
    body_type: str | None = None
    body_keys: tuple[str, ...] = ()
    has_active_id: bool = False
    has_size: bool = False
    has_count: bool = False
    has_from: bool = False
    has_to: bool = False
    has_limit: bool = False
    has_offset: bool = False
    has_chunk_size: bool = False
    numeric_field_names: tuple[str, ...] = ()
    string_field_names: tuple[str, ...] = ()
    array_paths: tuple[str, ...] = ()
    object_paths: tuple[str, ...] = ()
    request_ref: str | None = None
    correlation_status: str | None = None
    correlated_response_event_name: str | None = None
    correlated_response_collection_path: str | None = None
    correlated_response_collection_length: int | None = None
    correlated_response_distinct_timestamps: int = 0
    received_at: int | float | str | None = None
    last_error_code: str | None = None

    def sanitized(self) -> dict[str, Any]:
        return {
            "seen_main": self.seen_main,
            "relayed": self.relayed,
            "event_name": self.event_name,
            "inner_event_name": self.inner_event_name,
            "direction": self.direction,
            "top_level_type": self.top_level_type,
            "top_level_keys": list(self.top_level_keys),
            "msg_type": self.msg_type,
            "msg_keys": list(self.msg_keys),
            "body_type": self.body_type,
            "body_keys": list(self.body_keys),
            "has_active_id": self.has_active_id,
            "has_size": self.has_size,
            "has_count": self.has_count,
            "has_from": self.has_from,
            "has_to": self.has_to,
            "has_limit": self.has_limit,
            "has_offset": self.has_offset,
            "has_chunk_size": self.has_chunk_size,
            "numeric_field_names": list(self.numeric_field_names),
            "string_field_names": list(self.string_field_names),
            "array_paths": list(self.array_paths),
            "object_paths": list(self.object_paths),
            "request_ref": self.request_ref,
            "correlation_status": self.correlation_status,
            "correlated_response_event_name": self.correlated_response_event_name,
            "correlated_response_collection_path": self.correlated_response_collection_path,
            "correlated_response_collection_length": self.correlated_response_collection_length,
            "correlated_response_distinct_timestamps": self.correlated_response_distinct_timestamps,
            "received_at": self.received_at,
            "last_error_code": self.last_error_code,
        }


@dataclass
class OutboundRequestShape:
    shape_ref: str
    occurrences: int = 0
    inner_event_name: str | None = None
    top_level_keys: tuple[str, ...] = ()
    msg_keys: tuple[str, ...] = ()
    body_keys: tuple[str, ...] = ()
    has_active_id: bool = False
    has_size: bool = False
    has_count: bool = False
    has_from: bool = False
    has_to: bool = False
    has_limit: bool = False
    has_offset: bool = False
    correlated_response_event_names: set[str] = field(default_factory=set)

    def sanitized(self) -> dict[str, Any]:
        return {
            "shape_ref": self.shape_ref,
            "occurrences": self.occurrences,
            "inner_event_name": self.inner_event_name,
            "top_level_keys": list(self.top_level_keys),
            "msg_keys": list(self.msg_keys),
            "body_keys": list(self.body_keys),
            "has_active_id": self.has_active_id,
            "has_size": self.has_size,
            "has_count": self.has_count,
            "has_from": self.has_from,
            "has_to": self.has_to,
            "has_limit": self.has_limit,
            "has_offset": self.has_offset,
            "correlated_response_event_names": sorted(self.correlated_response_event_names),
        }


@dataclass
class HistoricalTransportDiscovery:
    fetch_requests_seen: int = 0
    fetch_responses_seen: int = 0
    xhr_requests_seen: int = 0
    xhr_responses_seen: int = 0
    websocket_candidates_seen: int = 0
    last_transport: str | None = None
    last_method: str | None = None
    last_url_host: str | None = None
    last_url_path_sanitized: str | None = None
    last_status_code: int | None = None
    last_content_type: str | None = None
    candidate_collection_path: str | None = None
    candidate_collection_type: str | None = None
    candidate_collection_length: int | None = None
    distinct_timestamps: int = 0
    distinct_raw_sizes: int = 0
    distinct_active_ids: int = 0
    historical_candidate_found: bool = False
    historical_quality: str | None = None
    historical_transport: str | None = None
    historical_request_ref: str | None = None
    page_bridge_installed_at: int | float | str | None = None
    fetch_interceptor_installed_at: int | float | str | None = None
    xhr_interceptor_installed_at: int | float | str | None = None
    websocket_created_at: int | float | str | None = None
    first_historical_candidate_at: int | float | str | None = None
    last_error_code: str | None = None
    top_level_type: str | None = None
    top_level_keys: tuple[str, ...] = ()
    nested_array_paths: tuple[str, ...] = ()
    nested_object_paths: tuple[str, ...] = ()

    def sanitized(self) -> dict[str, Any]:
        return {
            "fetch_requests_seen": self.fetch_requests_seen,
            "fetch_responses_seen": self.fetch_responses_seen,
            "xhr_requests_seen": self.xhr_requests_seen,
            "xhr_responses_seen": self.xhr_responses_seen,
            "websocket_candidates_seen": self.websocket_candidates_seen,
            "last_transport": self.last_transport,
            "last_method": self.last_method,
            "last_url_host": self.last_url_host,
            "last_url_path_sanitized": self.last_url_path_sanitized,
            "last_status_code": self.last_status_code,
            "last_content_type": self.last_content_type,
            "candidate_collection_path": self.candidate_collection_path,
            "candidate_collection_type": self.candidate_collection_type,
            "candidate_collection_length": self.candidate_collection_length,
            "distinct_timestamps": self.distinct_timestamps,
            "distinct_raw_sizes": self.distinct_raw_sizes,
            "distinct_active_ids": self.distinct_active_ids,
            "historical_candidate_found": self.historical_candidate_found,
            "historical_quality": self.historical_quality,
            "historical_transport": self.historical_transport,
            "historical_request_ref": self.historical_request_ref,
            "page_bridge_installed_at": self.page_bridge_installed_at,
            "fetch_interceptor_installed_at": self.fetch_interceptor_installed_at,
            "xhr_interceptor_installed_at": self.xhr_interceptor_installed_at,
            "websocket_created_at": self.websocket_created_at,
            "first_historical_candidate_at": self.first_historical_candidate_at,
            "last_error_code": self.last_error_code,
            "top_level_type": self.top_level_type,
            "top_level_keys": list(self.top_level_keys),
            "nested_array_paths": list(self.nested_array_paths),
            "nested_object_paths": list(self.nested_object_paths),
        }


@dataclass
class HistoricalTransportShape:
    shape_ref: str
    transport: str | None = None
    method: str | None = None
    host: str | None = None
    path_shape: str | None = None
    content_type: str | None = None
    top_level_type: str | None = None
    top_level_keys: tuple[str, ...] = ()
    nested_array_paths: tuple[str, ...] = ()
    nested_object_paths: tuple[str, ...] = ()
    candidate_collection_path: str | None = None
    candidate_collection_length: int | None = None
    distinct_timestamps: int = 0
    distinct_raw_sizes: int = 0
    distinct_active_ids: int = 0
    occurrences: int = 0

    def sanitized(self) -> dict[str, Any]:
        return {
            "shape_ref": self.shape_ref,
            "transport": self.transport,
            "method": self.method,
            "host": self.host,
            "path_shape": self.path_shape,
            "content_type": self.content_type,
            "top_level_type": self.top_level_type,
            "top_level_keys": list(self.top_level_keys),
            "nested_array_paths": list(self.nested_array_paths),
            "nested_object_paths": list(self.nested_object_paths),
            "candidate_collection_path": self.candidate_collection_path,
            "candidate_collection_length": self.candidate_collection_length,
            "distinct_timestamps": self.distinct_timestamps,
            "distinct_raw_sizes": self.distinct_raw_sizes,
            "distinct_active_ids": self.distinct_active_ids,
            "occurrences": self.occurrences,
        }


@dataclass
class RuntimeStoreDiscovery:
    scan_started_at: int | float | str | None = None
    scan_completed_at: int | float | str | None = None
    scan_duration_ms: int | None = None
    window_globals_scanned: int = 0
    react_nodes_scanned: int = 0
    redux_candidates: int = 0
    mobx_candidates: int = 0
    zustand_candidates: int = 0
    chart_engine_candidates: int = 0
    datafeed_candidates: int = 0
    storage_candidates: int = 0
    worker_candidates: int = 0
    candidate_found: bool = False
    candidate_type: str | None = None
    candidate_ref: str | None = None
    candidate_path: str | None = None
    candidate_collection_type: str | None = None
    candidate_collection_length: int | None = None
    candidate_distinct_timestamps: int = 0
    candidate_distinct_raw_sizes: int = 0
    candidate_distinct_active_ids: int = 0
    candidate_quality: str | None = None
    candidate_readable_passively: bool = False
    last_error_code: str | None = None

    def sanitized(self) -> dict[str, Any]:
        return {
            "scan_started_at": self.scan_started_at,
            "scan_completed_at": self.scan_completed_at,
            "scan_duration_ms": self.scan_duration_ms,
            "window_globals_scanned": self.window_globals_scanned,
            "react_nodes_scanned": self.react_nodes_scanned,
            "redux_candidates": self.redux_candidates,
            "mobx_candidates": self.mobx_candidates,
            "zustand_candidates": self.zustand_candidates,
            "chart_engine_candidates": self.chart_engine_candidates,
            "datafeed_candidates": self.datafeed_candidates,
            "storage_candidates": self.storage_candidates,
            "worker_candidates": self.worker_candidates,
            "candidate_found": self.candidate_found,
            "candidate_type": self.candidate_type,
            "candidate_ref": self.candidate_ref,
            "candidate_path": self.candidate_path,
            "candidate_collection_type": self.candidate_collection_type,
            "candidate_collection_length": self.candidate_collection_length,
            "candidate_distinct_timestamps": self.candidate_distinct_timestamps,
            "candidate_distinct_raw_sizes": self.candidate_distinct_raw_sizes,
            "candidate_distinct_active_ids": self.candidate_distinct_active_ids,
            "candidate_quality": self.candidate_quality,
            "candidate_readable_passively": self.candidate_readable_passively,
            "last_error_code": self.last_error_code,
        }


@dataclass
class RuntimeStoreCandidate:
    candidate_ref: str
    source_type: str | None = None
    name_sanitized: str | None = None
    path_sanitized: str | None = None
    object_type: str | None = None
    top_level_keys: tuple[str, ...] = ()
    method_names: tuple[str, ...] = ()
    array_paths: tuple[str, ...] = ()
    object_paths: tuple[str, ...] = ()
    collection_length: int | None = None
    distinct_timestamps: int = 0
    distinct_raw_sizes: int = 0
    distinct_active_ids: int = 0
    quality: str | None = None
    readable_passively: bool = False
    occurrences: int = 0

    def sanitized(self) -> dict[str, Any]:
        return {
            "candidate_ref": self.candidate_ref,
            "source_type": self.source_type,
            "name_sanitized": self.name_sanitized,
            "path_sanitized": self.path_sanitized,
            "object_type": self.object_type,
            "top_level_keys": list(self.top_level_keys),
            "method_names": list(self.method_names),
            "array_paths": list(self.array_paths),
            "object_paths": list(self.object_paths),
            "collection_length": self.collection_length,
            "distinct_timestamps": self.distinct_timestamps,
            "distinct_raw_sizes": self.distinct_raw_sizes,
            "distinct_active_ids": self.distinct_active_ids,
            "quality": self.quality,
            "readable_passively": self.readable_passively,
            "occurrences": self.occurrences,
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
    current_symbol: str | None = None
    symbol_found: bool = False
    symbol_source: str | None = None
    source: str = POLARIUM_AUTHORIZED_BROWSER_SOURCE
    data_classification: str = "DISCONNECTED"
    last_trace: BrowserBridgeTrace = field(default_factory=BrowserBridgeTrace)
    historical_diagnostic: HistoricalFirstCandlesDiagnostic = field(default_factory=HistoricalFirstCandlesDiagnostic)
    historical_series_discovery: HistoricalSeriesDiscovery = field(default_factory=HistoricalSeriesDiscovery)
    candles_generated_diagnostic: CandlesGeneratedDiagnostic = field(default_factory=CandlesGeneratedDiagnostic)
    outbound_candle_request_diagnostic: OutboundCandleRequestDiagnostic = field(default_factory=OutboundCandleRequestDiagnostic)
    outbound_request_shapes: dict[str, OutboundRequestShape] = field(default_factory=dict)
    historical_transport_discovery: HistoricalTransportDiscovery = field(default_factory=HistoricalTransportDiscovery)
    historical_transport_shapes: dict[str, HistoricalTransportShape] = field(default_factory=dict)
    runtime_store_discovery: RuntimeStoreDiscovery = field(default_factory=RuntimeStoreDiscovery)
    runtime_store_candidates: dict[str, RuntimeStoreCandidate] = field(default_factory=dict)

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
            "current_symbol": self.current_symbol,
            "symbol_found": self.symbol_found,
            "symbol_source": self.symbol_source,
            "source": self.source,
            "data_classification": self.data_classification,
            "last_trace": self.last_trace.sanitized(),
            "historical_diagnostic": self.historical_diagnostic.sanitized(),
            "historical_series_discovery": self.historical_series_discovery.sanitized(),
            "candles_generated_diagnostic": self.candles_generated_diagnostic.sanitized(),
            "outbound_candle_request_diagnostic": self.outbound_candle_request_diagnostic.sanitized(),
            "outbound_request_shapes": [shape.sanitized() for shape in self.outbound_request_shapes.values()],
            "historical_transport_discovery": self.historical_transport_discovery.sanitized(),
            "historical_transport_shapes": [shape.sanitized() for shape in self.historical_transport_shapes.values()],
            "runtime_store_discovery": self.runtime_store_discovery.sanitized(),
            "runtime_store_candidates": [candidate.sanitized() for candidate in self.runtime_store_candidates.values()],
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

        if event_name in HISTORICAL_DISCOVERY_EVENTS:
            self._record_historical_series_discovery(payload, event_name)

        if event_name in {"sendMessage", "get-first-candles", "subscribeMessage"}:
            self._record_outbound_candle_request(payload, event_name)

        if event_name == "historical-transport-discovery":
            self._record_historical_transport_discovery(payload)

        if event_name == "runtime-store-discovery":
            self._record_runtime_store_discovery(payload)

        if event_name == "candles-generated":
            self._record_candles_generated_diagnostic(payload)

        if event_name == "first-candles":
            self._record_first_candles_received(payload)

        normalized = _normalize_for_pipeline(event_name, payload)
        self._status.last_trace.adapter_accepted = True
        self._status.last_trace.payload_converted = _trace_payload(normalized)
        self._status.last_trace.pipeline_input = _trace_payload(normalized)
        if event_name == "first-candles":
            self._status.historical_diagnostic.first_candles_adapter_accepted += 1
        self._status.accepted_count += 1
        self._status.connected = True
        self._status.bridge_active = True
        self._status.last_event_name = event_name
        self._status.last_event_at = _utcnow()
        self._status.last_error_code = None
        self._status.data_classification = POLARIUM_AUTHORIZED_BROWSER_LABEL

        if event_name not in PIPELINE_EVENTS:
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
        if event_name == "first-candles":
            self._record_first_candles_pipeline_result(result)
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
        if event_name == "first-candles":
            self._status.historical_diagnostic.first_candles_last_error_code = error_code
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
            if candle.symbol:
                self._status.current_symbol = candle.symbol
                self._status.symbol_found = True
                self._status.symbol_source = "polarium_observed_payload"

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
                    "symbol": candle.symbol,
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

    def _record_first_candles_received(self, payload: dict[str, Any]) -> None:
        diagnostic = _first_candles_diagnostic_from_payload(payload)
        self._status.historical_diagnostic.first_candles_received_backend += 1
        self._status.historical_diagnostic.first_candles_seen_main += diagnostic.first_candles_seen_main
        self._status.historical_diagnostic.first_candles_relayed += diagnostic.first_candles_relayed
        self._status.historical_diagnostic.first_candles_collection_count = diagnostic.first_candles_collection_count
        self._status.historical_diagnostic.first_candles_last_error_code = None
        self._status.historical_diagnostic.event_name = diagnostic.event_name
        self._status.historical_diagnostic.direction = diagnostic.direction
        self._status.historical_diagnostic.top_level_type = diagnostic.top_level_type
        self._status.historical_diagnostic.top_level_keys = diagnostic.top_level_keys
        self._status.historical_diagnostic.msg_type = diagnostic.msg_type
        self._status.historical_diagnostic.msg_keys = diagnostic.msg_keys
        self._status.historical_diagnostic.body_type = diagnostic.body_type
        self._status.historical_diagnostic.body_keys = diagnostic.body_keys
        self._status.historical_diagnostic.candidate_collection_path = diagnostic.candidate_collection_path
        self._status.historical_diagnostic.candidate_collection_length = diagnostic.candidate_collection_length
        self._status.historical_diagnostic.received_at = diagnostic.received_at
        self._status.historical_diagnostic.relay_ready_at = diagnostic.relay_ready_at
        self._status.historical_diagnostic.websocket_created_at = diagnostic.websocket_created_at

    def _record_first_candles_pipeline_result(self, result: PipelineResult) -> None:
        parsed = len(result.route_result.candles)
        self._status.historical_diagnostic.first_candles_parsed += parsed
        self._status.historical_diagnostic.first_candles_stored += result.stored + result.updated
        invalid_count = len(result.errors)
        rejected_count = result.rejected
        self._status.historical_diagnostic.parsed_count = parsed
        self._status.historical_diagnostic.valid_count = parsed
        self._status.historical_diagnostic.invalid_count = invalid_count
        self._status.historical_diagnostic.rejected_count = rejected_count
        self._status.historical_diagnostic.stored_count = result.stored
        self._status.historical_diagnostic.ignored_count = result.ignored
        self._status.historical_diagnostic.updated_count = result.updated
        self._status.historical_diagnostic.route_status = result.route_result.status
        self._status.historical_diagnostic.pipeline_success = result.success
        self._status.historical_diagnostic.pipeline_errors = tuple(error.code for error in result.errors)
        self._status.historical_diagnostic.distinct_active_ids = tuple(
            sorted({candle.active_id for candle in result.route_result.candles if candle.active_id is not None})
        )
        self._status.historical_diagnostic.distinct_raw_sizes = tuple(sorted({candle.raw_size for candle in result.route_result.candles}))
        if not result.success:
            store_rejection = next((write.reason for write in result.store_results if write.status == "rejected"), None)
            error_code = result.errors[0].code if result.errors else store_rejection or "PIPELINE_REJECTED"
            self._status.historical_diagnostic.first_candles_last_error_code = error_code

    def _record_historical_series_discovery(self, payload: dict[str, Any], event_name: str) -> None:
        discovery = _historical_series_discovery_from_payload(payload, event_name)
        self._status.historical_series_discovery.candidate_events_seen += 1
        if discovery.candidate_requests_seen:
            self._status.historical_series_discovery.candidate_requests_seen += discovery.candidate_requests_seen
            self._status.historical_series_discovery.last_request_event_name = discovery.last_request_event_name
        if discovery.candidate_responses_seen:
            self._status.historical_series_discovery.candidate_responses_seen += discovery.candidate_responses_seen
            self._status.historical_series_discovery.last_response_event_name = discovery.last_response_event_name
        self._status.historical_series_discovery.last_collection_path = discovery.last_collection_path
        self._status.historical_series_discovery.last_collection_length = discovery.last_collection_length
        self._status.historical_series_discovery.last_distinct_timestamps = discovery.last_distinct_timestamps
        self._status.historical_series_discovery.last_distinct_raw_sizes = discovery.last_distinct_raw_sizes
        self._status.historical_series_discovery.last_distinct_active_ids = discovery.last_distinct_active_ids
        self._status.historical_series_discovery.historical_series_confirmed = discovery.historical_series_confirmed
        self._status.historical_series_discovery.historical_series_event_name = discovery.historical_series_event_name
        self._status.historical_series_discovery.historical_series_request_ref = discovery.historical_series_request_ref
        self._status.historical_series_discovery.last_error_code = discovery.last_error_code

    def _record_candles_generated_diagnostic(self, payload: dict[str, Any]) -> None:
        diagnostic = _candles_generated_diagnostic_from_payload(payload)
        self._status.candles_generated_diagnostic.seen_main += diagnostic.seen_main
        self._status.candles_generated_diagnostic.relayed += diagnostic.relayed
        self._status.candles_generated_diagnostic.received_backend += 1
        self._status.candles_generated_diagnostic.top_level_type = diagnostic.top_level_type
        self._status.candles_generated_diagnostic.top_level_keys = diagnostic.top_level_keys
        self._status.candles_generated_diagnostic.msg_type = diagnostic.msg_type
        self._status.candles_generated_diagnostic.msg_keys = diagnostic.msg_keys
        self._status.candles_generated_diagnostic.body_type = diagnostic.body_type
        self._status.candles_generated_diagnostic.body_keys = diagnostic.body_keys
        self._status.candles_generated_diagnostic.nested_array_paths = diagnostic.nested_array_paths
        self._status.candles_generated_diagnostic.nested_object_paths = diagnostic.nested_object_paths
        self._status.candles_generated_diagnostic.candidate_collection_path = diagnostic.candidate_collection_path
        self._status.candles_generated_diagnostic.candidate_collection_type = diagnostic.candidate_collection_type
        self._status.candles_generated_diagnostic.candidate_collection_length = diagnostic.candidate_collection_length
        self._status.candles_generated_diagnostic.distinct_timestamps = diagnostic.distinct_timestamps
        self._status.candles_generated_diagnostic.distinct_raw_sizes = diagnostic.distinct_raw_sizes
        self._status.candles_generated_diagnostic.distinct_active_ids = diagnostic.distinct_active_ids
        self._status.candles_generated_diagnostic.request_ref = diagnostic.request_ref
        self._status.candles_generated_diagnostic.direction = diagnostic.direction
        self._status.candles_generated_diagnostic.received_at = diagnostic.received_at
        self._status.candles_generated_diagnostic.last_error_code = diagnostic.last_error_code
        self._status.candles_generated_diagnostic.historical_series_confirmed = diagnostic.historical_series_confirmed
        if diagnostic.request_ref and diagnostic.direction == "server_to_client":
            self._link_response_to_outbound_request(diagnostic.request_ref, "candles-generated", diagnostic)

    def _record_outbound_candle_request(self, payload: dict[str, Any], event_name: str) -> None:
        diagnostic = _outbound_request_diagnostic_from_payload(payload, event_name)
        self._status.outbound_candle_request_diagnostic.seen_main += diagnostic.seen_main
        self._status.outbound_candle_request_diagnostic.relayed += diagnostic.relayed
        self._status.outbound_candle_request_diagnostic.event_name = diagnostic.event_name
        self._status.outbound_candle_request_diagnostic.inner_event_name = diagnostic.inner_event_name
        self._status.outbound_candle_request_diagnostic.direction = diagnostic.direction
        self._status.outbound_candle_request_diagnostic.top_level_type = diagnostic.top_level_type
        self._status.outbound_candle_request_diagnostic.top_level_keys = diagnostic.top_level_keys
        self._status.outbound_candle_request_diagnostic.msg_type = diagnostic.msg_type
        self._status.outbound_candle_request_diagnostic.msg_keys = diagnostic.msg_keys
        self._status.outbound_candle_request_diagnostic.body_type = diagnostic.body_type
        self._status.outbound_candle_request_diagnostic.body_keys = diagnostic.body_keys
        self._status.outbound_candle_request_diagnostic.has_active_id = diagnostic.has_active_id
        self._status.outbound_candle_request_diagnostic.has_size = diagnostic.has_size
        self._status.outbound_candle_request_diagnostic.has_count = diagnostic.has_count
        self._status.outbound_candle_request_diagnostic.has_from = diagnostic.has_from
        self._status.outbound_candle_request_diagnostic.has_to = diagnostic.has_to
        self._status.outbound_candle_request_diagnostic.has_limit = diagnostic.has_limit
        self._status.outbound_candle_request_diagnostic.has_offset = diagnostic.has_offset
        self._status.outbound_candle_request_diagnostic.has_chunk_size = diagnostic.has_chunk_size
        self._status.outbound_candle_request_diagnostic.numeric_field_names = diagnostic.numeric_field_names
        self._status.outbound_candle_request_diagnostic.string_field_names = diagnostic.string_field_names
        self._status.outbound_candle_request_diagnostic.array_paths = diagnostic.array_paths
        self._status.outbound_candle_request_diagnostic.object_paths = diagnostic.object_paths
        self._status.outbound_candle_request_diagnostic.request_ref = diagnostic.request_ref
        self._status.outbound_candle_request_diagnostic.correlation_status = diagnostic.correlation_status
        self._status.outbound_candle_request_diagnostic.received_at = diagnostic.received_at
        self._status.outbound_candle_request_diagnostic.last_error_code = diagnostic.last_error_code
        self._record_outbound_shape(diagnostic)

    def _record_outbound_shape(self, diagnostic: OutboundCandleRequestDiagnostic) -> None:
        fingerprint = _outbound_shape_fingerprint(diagnostic)
        shape = self._status.outbound_request_shapes.get(fingerprint)
        if shape is None:
            if len(self._status.outbound_request_shapes) >= OUTBOUND_SHAPE_LIMIT:
                self._status.outbound_candle_request_diagnostic.last_error_code = "OUTBOUND_SHAPE_LIMIT_REACHED"
                return
            shape = OutboundRequestShape(
                shape_ref=f"request_shape_{len(self._status.outbound_request_shapes) + 1}",
                inner_event_name=diagnostic.inner_event_name,
                top_level_keys=diagnostic.top_level_keys,
                msg_keys=diagnostic.msg_keys,
                body_keys=diagnostic.body_keys,
                has_active_id=diagnostic.has_active_id,
                has_size=diagnostic.has_size,
                has_count=diagnostic.has_count,
                has_from=diagnostic.has_from,
                has_to=diagnostic.has_to,
                has_limit=diagnostic.has_limit,
                has_offset=diagnostic.has_offset,
            )
            self._status.outbound_request_shapes[fingerprint] = shape
        shape.occurrences += 1

    def _link_response_to_outbound_request(self, request_ref: str, event_name: str, diagnostic: CandlesGeneratedDiagnostic) -> None:
        if self._status.outbound_candle_request_diagnostic.request_ref == request_ref:
            self._status.outbound_candle_request_diagnostic.correlation_status = "CONFIRMED_BY_REQUEST_ID"
            self._status.outbound_candle_request_diagnostic.correlated_response_event_name = event_name
            self._status.outbound_candle_request_diagnostic.correlated_response_collection_path = diagnostic.candidate_collection_path
            self._status.outbound_candle_request_diagnostic.correlated_response_collection_length = diagnostic.candidate_collection_length
            self._status.outbound_candle_request_diagnostic.correlated_response_distinct_timestamps = diagnostic.distinct_timestamps
        for shape in self._status.outbound_request_shapes.values():
            if self._status.outbound_candle_request_diagnostic.request_ref == request_ref:
                shape.correlated_response_event_names.add(event_name)

    def _record_historical_transport_discovery(self, payload: dict[str, Any]) -> None:
        diagnostic = _historical_transport_discovery_from_payload(payload)
        self._status.historical_transport_discovery.fetch_requests_seen += diagnostic.fetch_requests_seen
        self._status.historical_transport_discovery.fetch_responses_seen += diagnostic.fetch_responses_seen
        self._status.historical_transport_discovery.xhr_requests_seen += diagnostic.xhr_requests_seen
        self._status.historical_transport_discovery.xhr_responses_seen += diagnostic.xhr_responses_seen
        self._status.historical_transport_discovery.websocket_candidates_seen += diagnostic.websocket_candidates_seen
        self._status.historical_transport_discovery.last_transport = diagnostic.last_transport
        self._status.historical_transport_discovery.last_method = diagnostic.last_method
        self._status.historical_transport_discovery.last_url_host = diagnostic.last_url_host
        self._status.historical_transport_discovery.last_url_path_sanitized = diagnostic.last_url_path_sanitized
        self._status.historical_transport_discovery.last_status_code = diagnostic.last_status_code
        self._status.historical_transport_discovery.last_content_type = diagnostic.last_content_type
        self._status.historical_transport_discovery.candidate_collection_path = diagnostic.candidate_collection_path
        self._status.historical_transport_discovery.candidate_collection_type = diagnostic.candidate_collection_type
        self._status.historical_transport_discovery.candidate_collection_length = diagnostic.candidate_collection_length
        self._status.historical_transport_discovery.distinct_timestamps = diagnostic.distinct_timestamps
        self._status.historical_transport_discovery.distinct_raw_sizes = diagnostic.distinct_raw_sizes
        self._status.historical_transport_discovery.distinct_active_ids = diagnostic.distinct_active_ids
        self._status.historical_transport_discovery.page_bridge_installed_at = diagnostic.page_bridge_installed_at
        self._status.historical_transport_discovery.fetch_interceptor_installed_at = diagnostic.fetch_interceptor_installed_at
        self._status.historical_transport_discovery.xhr_interceptor_installed_at = diagnostic.xhr_interceptor_installed_at
        self._status.historical_transport_discovery.websocket_created_at = diagnostic.websocket_created_at
        self._status.historical_transport_discovery.last_error_code = diagnostic.last_error_code
        if diagnostic.historical_candidate_found:
            self._status.historical_transport_discovery.historical_candidate_found = True
            self._status.historical_transport_discovery.historical_quality = diagnostic.historical_quality
            self._status.historical_transport_discovery.historical_transport = diagnostic.historical_transport
            self._status.historical_transport_discovery.historical_request_ref = diagnostic.historical_request_ref
            self._status.historical_transport_discovery.first_historical_candidate_at = (
                self._status.historical_transport_discovery.first_historical_candidate_at or diagnostic.first_historical_candidate_at
            )
        self._record_transport_shape(diagnostic)

    def _record_transport_shape(self, diagnostic: HistoricalTransportDiscovery) -> None:
        fingerprint = _transport_shape_fingerprint(diagnostic)
        shape = self._status.historical_transport_shapes.get(fingerprint)
        if shape is None:
            if len(self._status.historical_transport_shapes) >= TRANSPORT_SHAPE_LIMIT:
                self._status.historical_transport_discovery.last_error_code = "TRANSPORT_SHAPE_LIMIT_REACHED"
                return
            shape = HistoricalTransportShape(
                shape_ref=f"transport_shape_{len(self._status.historical_transport_shapes) + 1}",
                transport=diagnostic.last_transport,
                method=diagnostic.last_method,
                host=diagnostic.last_url_host,
                path_shape=diagnostic.last_url_path_sanitized,
                content_type=diagnostic.last_content_type,
                top_level_type=diagnostic.top_level_type,
                top_level_keys=diagnostic.top_level_keys,
                nested_array_paths=diagnostic.nested_array_paths,
                nested_object_paths=diagnostic.nested_object_paths,
                candidate_collection_path=diagnostic.candidate_collection_path,
                candidate_collection_length=diagnostic.candidate_collection_length,
                distinct_timestamps=diagnostic.distinct_timestamps,
                distinct_raw_sizes=diagnostic.distinct_raw_sizes,
                distinct_active_ids=diagnostic.distinct_active_ids,
            )
            self._status.historical_transport_shapes[fingerprint] = shape
        shape.occurrences += 1

    def _record_runtime_store_discovery(self, payload: dict[str, Any]) -> None:
        diagnostic = _runtime_store_discovery_from_payload(payload)
        self._status.runtime_store_discovery = diagnostic
        incoming_candidates = payload.get("runtime_store_candidates")
        if not isinstance(incoming_candidates, list):
            incoming_candidates = []
        for incoming in incoming_candidates:
            if not isinstance(incoming, dict):
                continue
            candidate = _runtime_store_candidate_from_payload(incoming)
            if candidate is None:
                continue
            fingerprint = _runtime_store_candidate_fingerprint(candidate)
            existing = self._status.runtime_store_candidates.get(fingerprint)
            if existing is None:
                if len(self._status.runtime_store_candidates) >= RUNTIME_STORE_CANDIDATE_LIMIT:
                    self._status.runtime_store_discovery.last_error_code = "RUNTIME_STORE_CANDIDATE_LIMIT_REACHED"
                    return
                self._status.runtime_store_candidates[fingerprint] = candidate
            else:
                existing.occurrences += max(candidate.occurrences, 1)


def _normalize_for_pipeline(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    return adapt_browser_bridge_payload(event_name, payload)


def _runtime_store_discovery_from_payload(payload: dict[str, Any]) -> RuntimeStoreDiscovery:
    incoming = payload.get("runtime_store_discovery")
    if not isinstance(incoming, dict):
        incoming = {}
    distinct_timestamps = _safe_int(incoming.get("candidate_distinct_timestamps")) or 0
    distinct_raw_sizes = _safe_int(incoming.get("candidate_distinct_raw_sizes")) or 0
    distinct_active_ids = _safe_int(incoming.get("candidate_distinct_active_ids")) or 0
    has_readable_counts = distinct_active_ids > 0 or distinct_raw_sizes > 0 or distinct_timestamps > 0
    structural_candidate = (
        not has_readable_counts
        and (_safe_int(incoming.get("candidate_collection_length")) or 0) >= 2
        and _safe_path(incoming.get("candidate_path")) is not None
    )
    candidate_found = bool(incoming.get("candidate_found")) and (
        (distinct_active_ids == 1 and distinct_raw_sizes == 1 and distinct_timestamps >= 2) or structural_candidate
    )
    return RuntimeStoreDiscovery(
        scan_started_at=_safe_scalar(incoming.get("scan_started_at")),
        scan_completed_at=_safe_scalar(incoming.get("scan_completed_at")),
        scan_duration_ms=_safe_int(incoming.get("scan_duration_ms")),
        window_globals_scanned=_safe_int(incoming.get("window_globals_scanned")) or 0,
        react_nodes_scanned=_safe_int(incoming.get("react_nodes_scanned")) or 0,
        redux_candidates=_safe_int(incoming.get("redux_candidates")) or 0,
        mobx_candidates=_safe_int(incoming.get("mobx_candidates")) or 0,
        zustand_candidates=_safe_int(incoming.get("zustand_candidates")) or 0,
        chart_engine_candidates=_safe_int(incoming.get("chart_engine_candidates")) or 0,
        datafeed_candidates=_safe_int(incoming.get("datafeed_candidates")) or 0,
        storage_candidates=_safe_int(incoming.get("storage_candidates")) or 0,
        worker_candidates=_safe_int(incoming.get("worker_candidates")) or 0,
        candidate_found=candidate_found,
        candidate_type=_safe_runtime_source_type(incoming.get("candidate_type")) if candidate_found else None,
        candidate_ref=_safe_runtime_ref(incoming.get("candidate_ref")) if candidate_found else None,
        candidate_path=_safe_path(incoming.get("candidate_path")) if candidate_found else None,
        candidate_collection_type=_safe_collection_type(incoming.get("candidate_collection_type")) if candidate_found else None,
        candidate_collection_length=_safe_int(incoming.get("candidate_collection_length")) if candidate_found else None,
        candidate_distinct_timestamps=distinct_timestamps,
        candidate_distinct_raw_sizes=distinct_raw_sizes,
        candidate_distinct_active_ids=distinct_active_ids,
        candidate_quality=_historical_quality(distinct_timestamps) if candidate_found and distinct_timestamps >= 2 else None,
        candidate_readable_passively=bool(incoming.get("candidate_readable_passively")) and candidate_found,
        last_error_code=_safe_str(incoming.get("last_error_code")),
    )


def _runtime_store_candidate_from_payload(incoming: dict[str, Any]) -> RuntimeStoreCandidate | None:
    candidate_ref = _safe_runtime_ref(incoming.get("candidate_ref"))
    if candidate_ref is None:
        return None
    distinct_timestamps = _safe_int(incoming.get("distinct_timestamps")) or 0
    return RuntimeStoreCandidate(
        candidate_ref=candidate_ref,
        source_type=_safe_runtime_source_type(incoming.get("source_type")),
        name_sanitized=_safe_runtime_name(incoming.get("name_sanitized")),
        path_sanitized=_safe_path(incoming.get("path_sanitized")),
        object_type=_safe_str(incoming.get("object_type")),
        top_level_keys=_safe_key_tuple(incoming.get("top_level_keys"), hide_market_fields=True),
        method_names=_safe_method_tuple(incoming.get("method_names")),
        array_paths=_safe_path_tuple(incoming.get("array_paths")),
        object_paths=_safe_path_tuple(incoming.get("object_paths")),
        collection_length=_safe_int(incoming.get("collection_length")),
        distinct_timestamps=distinct_timestamps,
        distinct_raw_sizes=_safe_int(incoming.get("distinct_raw_sizes")) or 0,
        distinct_active_ids=_safe_int(incoming.get("distinct_active_ids")) or 0,
        quality=_historical_quality(distinct_timestamps) if distinct_timestamps >= 2 else None,
        readable_passively=bool(incoming.get("readable_passively")),
        occurrences=max(_safe_int(incoming.get("occurrences")) or 0, 1),
    )


def _runtime_store_candidate_fingerprint(candidate: RuntimeStoreCandidate) -> str:
    return "|".join(
        (
            candidate.source_type or "",
            candidate.name_sanitized or "",
            candidate.path_sanitized or "",
            candidate.object_type or "",
            str(candidate.collection_length),
            str(candidate.distinct_timestamps),
            str(candidate.distinct_raw_sizes),
            str(candidate.distinct_active_ids),
        )
    )


def _historical_transport_discovery_from_payload(payload: dict[str, Any]) -> HistoricalTransportDiscovery:
    incoming = payload.get("historical_transport_discovery")
    if not isinstance(incoming, dict):
        incoming = {}
    transport = _safe_transport(incoming.get("last_transport"))
    distinct_timestamps = _safe_int(incoming.get("distinct_timestamps")) or 0
    distinct_raw_sizes = _safe_int(incoming.get("distinct_raw_sizes")) or 0
    distinct_active_ids = _safe_int(incoming.get("distinct_active_ids")) or 0
    historical_candidate = distinct_active_ids == 1 and distinct_raw_sizes == 1 and distinct_timestamps >= 2
    return HistoricalTransportDiscovery(
        fetch_requests_seen=_safe_int(incoming.get("fetch_requests_seen")) or (1 if transport == "fetch_request" else 0),
        fetch_responses_seen=_safe_int(incoming.get("fetch_responses_seen")) or (1 if transport == "fetch_response" else 0),
        xhr_requests_seen=_safe_int(incoming.get("xhr_requests_seen")) or (1 if transport == "xhr_request" else 0),
        xhr_responses_seen=_safe_int(incoming.get("xhr_responses_seen")) or (1 if transport == "xhr_response" else 0),
        websocket_candidates_seen=_safe_int(incoming.get("websocket_candidates_seen")) or (1 if transport == "websocket" else 0),
        last_transport=transport,
        last_method=_safe_http_method(incoming.get("last_method")),
        last_url_host=_safe_host(incoming.get("last_url_host")),
        last_url_path_sanitized=_safe_path(incoming.get("last_url_path_sanitized")),
        last_status_code=_safe_int(incoming.get("last_status_code")),
        last_content_type=_safe_content_type(incoming.get("last_content_type")),
        candidate_collection_path=_safe_path(incoming.get("candidate_collection_path")),
        candidate_collection_type=_safe_str(incoming.get("candidate_collection_type")),
        candidate_collection_length=_safe_int(incoming.get("candidate_collection_length")),
        distinct_timestamps=distinct_timestamps,
        distinct_raw_sizes=distinct_raw_sizes,
        distinct_active_ids=distinct_active_ids,
        historical_candidate_found=historical_candidate,
        historical_quality=_historical_quality(distinct_timestamps) if historical_candidate else None,
        historical_transport=transport if historical_candidate else None,
        historical_request_ref=_safe_request_ref(incoming.get("historical_request_ref")),
        page_bridge_installed_at=_safe_scalar(incoming.get("page_bridge_installed_at")),
        fetch_interceptor_installed_at=_safe_scalar(incoming.get("fetch_interceptor_installed_at")),
        xhr_interceptor_installed_at=_safe_scalar(incoming.get("xhr_interceptor_installed_at")),
        websocket_created_at=_safe_scalar(incoming.get("websocket_created_at")),
        first_historical_candidate_at=_safe_scalar(incoming.get("first_historical_candidate_at")),
        last_error_code=_safe_str(incoming.get("last_error_code")),
        top_level_type=_safe_str(incoming.get("top_level_type")),
        top_level_keys=_safe_key_tuple(incoming.get("top_level_keys"), hide_market_fields=True),
        nested_array_paths=_safe_path_tuple(incoming.get("nested_array_paths")),
        nested_object_paths=_safe_path_tuple(incoming.get("nested_object_paths")),
    )


def _historical_quality(distinct_timestamps: int) -> str:
    if distinct_timestamps >= 100:
        return "BROAD"
    if distinct_timestamps >= 20:
        return "USEFUL"
    if distinct_timestamps >= 2:
        return "SHORT"
    return "NONE"


def _transport_shape_fingerprint(diagnostic: HistoricalTransportDiscovery) -> str:
    return "|".join(
        (
            diagnostic.last_transport or "",
            diagnostic.last_method or "",
            diagnostic.last_url_host or "",
            diagnostic.last_url_path_sanitized or "",
            diagnostic.last_content_type or "",
            diagnostic.candidate_collection_path or "",
            str(diagnostic.distinct_timestamps),
            str(diagnostic.distinct_raw_sizes),
            str(diagnostic.distinct_active_ids),
        )
    )


def _outbound_request_diagnostic_from_payload(payload: dict[str, Any], event_name: str) -> OutboundCandleRequestDiagnostic:
    incoming = payload.get("outbound_candle_request_diagnostic")
    message = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    if isinstance(incoming, dict):
        return OutboundCandleRequestDiagnostic(
            seen_main=max(_safe_int(incoming.get("seen_main")) or 0, 1),
            relayed=max(_safe_int(incoming.get("relayed")) or 0, 1),
            event_name=_safe_str(incoming.get("event_name")) or event_name,
            inner_event_name=_safe_str(incoming.get("inner_event_name")),
            direction=_safe_str(incoming.get("direction")) or "client_to_server",
            top_level_type=_safe_str(incoming.get("top_level_type")),
            top_level_keys=_safe_key_tuple(incoming.get("top_level_keys"), hide_market_fields=True),
            msg_type=_safe_str(incoming.get("msg_type")),
            msg_keys=_safe_key_tuple(incoming.get("msg_keys"), hide_market_fields=True),
            body_type=_safe_str(incoming.get("body_type")),
            body_keys=_safe_key_tuple(incoming.get("body_keys"), hide_market_fields=True),
            has_active_id=bool(incoming.get("has_active_id")),
            has_size=bool(incoming.get("has_size")),
            has_count=bool(incoming.get("has_count")),
            has_from=bool(incoming.get("has_from")),
            has_to=bool(incoming.get("has_to")),
            has_limit=bool(incoming.get("has_limit")),
            has_offset=bool(incoming.get("has_offset")),
            has_chunk_size=bool(incoming.get("has_chunk_size")),
            numeric_field_names=_safe_field_name_tuple(incoming.get("numeric_field_names")),
            string_field_names=_safe_field_name_tuple(incoming.get("string_field_names")),
            array_paths=_safe_path_tuple(incoming.get("array_paths")),
            object_paths=_safe_path_tuple(incoming.get("object_paths")),
            request_ref=_safe_request_ref(incoming.get("request_ref")),
            correlation_status=_safe_correlation_status(incoming.get("correlation_status")),
            received_at=_safe_scalar(incoming.get("received_at")),
            last_error_code=_safe_str(incoming.get("last_error_code")),
        )
    return _structural_outbound_request_diagnostic(message, event_name)


def _structural_outbound_request_diagnostic(message: dict[str, Any], event_name: str) -> OutboundCandleRequestDiagnostic:
    msg = message.get("msg") if isinstance(message.get("msg"), dict) else None
    body = msg.get("body") if isinstance(msg, dict) and isinstance(msg.get("body"), dict) else None
    array_paths, object_paths = _collect_structure_paths(message)
    numeric_fields, string_fields = _collect_field_type_names(message)
    return OutboundCandleRequestDiagnostic(
        seen_main=0,
        relayed=0,
        event_name=event_name,
        inner_event_name=_inner_event_name(message),
        direction="client_to_server",
        top_level_type=_type_name(message),
        top_level_keys=_safe_key_tuple(list(message.keys()), hide_market_fields=True),
        msg_type=_type_name(msg),
        msg_keys=_safe_key_tuple(list(msg.keys()) if isinstance(msg, dict) else (), hide_market_fields=True),
        body_type=_type_name(body),
        body_keys=_safe_key_tuple(list(body.keys()) if isinstance(body, dict) else (), hide_market_fields=True),
        has_active_id=_has_any_field(message, ("active_id", "activeId", "active", "asset_id")),
        has_size=_has_any_field(message, ("size", "raw_size", "rawSize", "timeframe_size")),
        has_count=_has_any_field(message, ("count",)),
        has_from=_has_any_field(message, ("from", "start", "start_timestamp", "startTimestamp")),
        has_to=_has_any_field(message, ("to", "end", "end_timestamp", "endTimestamp")),
        has_limit=_has_any_field(message, ("limit",)),
        has_offset=_has_any_field(message, ("offset",)),
        has_chunk_size=_has_any_field(message, ("chunk_size", "chunkSize")),
        numeric_field_names=tuple(sorted(numeric_fields)),
        string_field_names=tuple(sorted(string_fields)),
        array_paths=array_paths,
        object_paths=object_paths,
        request_ref=None,
        correlation_status="TEMPORAL_CANDIDATE",
    )


def _candles_generated_diagnostic_from_payload(payload: dict[str, Any]) -> CandlesGeneratedDiagnostic:
    incoming = payload.get("candles_generated_diagnostic")
    message = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    if isinstance(incoming, dict):
        return CandlesGeneratedDiagnostic(
            seen_main=max(_safe_int(incoming.get("seen_main")) or 0, 1),
            relayed=max(_safe_int(incoming.get("relayed")) or 0, 1),
            top_level_type=_safe_str(incoming.get("top_level_type")),
            top_level_keys=_safe_key_tuple(incoming.get("top_level_keys"), hide_market_fields=True),
            msg_type=_safe_str(incoming.get("msg_type")),
            msg_keys=_safe_key_tuple(incoming.get("msg_keys"), hide_market_fields=True),
            body_type=_safe_str(incoming.get("body_type")),
            body_keys=_safe_key_tuple(incoming.get("body_keys"), hide_market_fields=True),
            nested_array_paths=_safe_path_tuple(incoming.get("nested_array_paths")),
            nested_object_paths=_safe_path_tuple(incoming.get("nested_object_paths")),
            candidate_collection_path=_safe_path(incoming.get("candidate_collection_path")),
            candidate_collection_type=_safe_str(incoming.get("candidate_collection_type")),
            candidate_collection_length=_safe_int(incoming.get("candidate_collection_length")),
            distinct_timestamps=_safe_int(incoming.get("distinct_timestamps")) or 0,
            distinct_raw_sizes=_safe_int(incoming.get("distinct_raw_sizes")) or 0,
            distinct_active_ids=_safe_int(incoming.get("distinct_active_ids")) or 0,
            request_ref=_safe_request_ref(incoming.get("request_ref")),
            direction=_safe_str(incoming.get("direction")) or "server_to_client",
            received_at=_safe_scalar(incoming.get("received_at")),
            last_error_code=_safe_str(incoming.get("last_error_code")),
            historical_series_confirmed=bool(incoming.get("historical_series_confirmed"))
            and (_safe_int(incoming.get("distinct_active_ids")) or 0) == 1
            and (_safe_int(incoming.get("distinct_raw_sizes")) or 0) == 1
            and (_safe_int(incoming.get("distinct_timestamps")) or 0) >= 20,
        )

    return _structural_candles_generated_diagnostic(message)


def _structural_candles_generated_diagnostic(message: dict[str, Any]) -> CandlesGeneratedDiagnostic:
    msg = message.get("msg") if isinstance(message.get("msg"), dict) else None
    body = msg.get("body") if isinstance(msg, dict) and isinstance(msg.get("body"), dict) else None
    array_paths, object_paths = _collect_structure_paths(message)
    collection_path, collection_type, collection_length = _find_structural_collection(message)
    active_ids, raw_sizes, timestamps = _collect_collection_metadata(message)
    historical_confirmed = len(active_ids) == 1 and len(raw_sizes) == 1 and len(timestamps) >= 20
    return CandlesGeneratedDiagnostic(
        seen_main=0,
        relayed=0,
        top_level_type=_type_name(message),
        top_level_keys=_safe_key_tuple(list(message.keys()), hide_market_fields=True),
        msg_type=_type_name(msg),
        msg_keys=_safe_key_tuple(list(msg.keys()) if isinstance(msg, dict) else (), hide_market_fields=True),
        body_type=_type_name(body),
        body_keys=_safe_key_tuple(list(body.keys()) if isinstance(body, dict) else (), hide_market_fields=True),
        nested_array_paths=array_paths,
        nested_object_paths=object_paths,
        candidate_collection_path=collection_path,
        candidate_collection_type=collection_type,
        candidate_collection_length=collection_length,
        distinct_timestamps=len(timestamps),
        distinct_raw_sizes=len(raw_sizes),
        distinct_active_ids=len(active_ids),
        direction="server_to_client",
        historical_series_confirmed=historical_confirmed,
    )


def _historical_series_discovery_from_payload(payload: dict[str, Any], event_name: str) -> HistoricalSeriesDiscovery:
    incoming = payload.get("discovery")
    if isinstance(incoming, dict):
        direction = _safe_str(incoming.get("direction"))
        is_request = direction == "client_to_server"
        distinct_active_ids = _safe_int(incoming.get("distinct_active_ids")) or 0
        distinct_raw_sizes = _safe_int(incoming.get("distinct_raw_sizes")) or 0
        distinct_timestamps = _safe_int(incoming.get("distinct_timestamps")) or 0
        historical_confirmed = bool(incoming.get("historical_series_confirmed")) and distinct_active_ids == 1 and distinct_raw_sizes == 1 and distinct_timestamps >= 20
        return HistoricalSeriesDiscovery(
            candidate_events_seen=1,
            candidate_requests_seen=1 if is_request else 0,
            candidate_responses_seen=0 if is_request else 1,
            last_request_event_name=event_name if is_request else None,
            last_response_event_name=None if is_request else event_name,
            last_collection_path=_safe_str(incoming.get("collection_path")),
            last_collection_length=_safe_int(incoming.get("collection_length")),
            last_distinct_timestamps=distinct_timestamps,
            last_distinct_raw_sizes=distinct_raw_sizes,
            last_distinct_active_ids=distinct_active_ids,
            historical_series_confirmed=historical_confirmed,
            historical_series_event_name=event_name if historical_confirmed else None,
            historical_series_request_ref=_safe_request_ref(incoming.get("request_ref")) if historical_confirmed else None,
            last_error_code=None,
        )

    message = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    collection_path, collection_length = _find_candidate_collection(message)
    active_ids, raw_sizes, timestamps = _collect_collection_metadata(message)
    distinct_active_ids = len(active_ids)
    distinct_raw_sizes = len(raw_sizes)
    distinct_timestamps = len(timestamps)
    historical_confirmed = distinct_active_ids == 1 and distinct_raw_sizes == 1 and distinct_timestamps >= 20
    is_request = event_name in {"get-first-candles", "subscribeMessage", "sendMessage"}
    return HistoricalSeriesDiscovery(
        candidate_events_seen=1,
        candidate_requests_seen=1 if is_request else 0,
        candidate_responses_seen=0 if is_request else 1,
        last_request_event_name=event_name if is_request else None,
        last_response_event_name=None if is_request else event_name,
        last_collection_path=collection_path,
        last_collection_length=collection_length,
        last_distinct_timestamps=distinct_timestamps,
        last_distinct_raw_sizes=distinct_raw_sizes,
        last_distinct_active_ids=distinct_active_ids,
        historical_series_confirmed=historical_confirmed,
        historical_series_event_name=event_name if historical_confirmed else None,
        historical_series_request_ref=None,
    )


def _first_candles_diagnostic_from_payload(payload: dict[str, Any]) -> HistoricalFirstCandlesDiagnostic:
    incoming = payload.get("diagnostic")
    if not isinstance(incoming, dict):
        incoming = {}
    message = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    structure = _structural_first_candles_diagnostic(message)
    collection_length = _safe_int(incoming.get("candidate_collection_length"))
    collection_path = _safe_str(incoming.get("candidate_collection_path"))
    if collection_length is None:
        collection_length = structure.first_candles_collection_count
    if collection_path is None:
        collection_path = structure.candidate_collection_path

    return HistoricalFirstCandlesDiagnostic(
        first_candles_seen_main=max(_safe_int(incoming.get("first_candles_seen_main")) or 0, 1 if incoming else 0),
        first_candles_relayed=max(_safe_int(incoming.get("first_candles_relayed")) or 0, 1 if incoming.get("relay_ready_at") else 0),
        first_candles_collection_count=collection_length or 0,
        event_name=_safe_str(incoming.get("event_name")) or "first-candles",
        direction=_safe_str(incoming.get("direction")) or "server_to_client",
        top_level_type=_safe_str(incoming.get("top_level_type")) or structure.top_level_type,
        top_level_keys=_safe_key_tuple(incoming.get("top_level_keys")) or structure.top_level_keys,
        msg_type=_safe_str(incoming.get("msg_type")) or structure.msg_type,
        msg_keys=_safe_key_tuple(incoming.get("msg_keys")) or structure.msg_keys,
        body_type=_safe_str(incoming.get("body_type")) or structure.body_type,
        body_keys=_safe_key_tuple(incoming.get("body_keys")) or structure.body_keys,
        candidate_collection_path=collection_path,
        candidate_collection_length=collection_length,
        received_at=_safe_scalar(incoming.get("received_at")),
        relay_ready_at=_safe_scalar(incoming.get("relay_ready_at")),
        websocket_created_at=_safe_scalar(incoming.get("websocket_created_at")),
    )


def _structural_first_candles_diagnostic(message: dict[str, Any]) -> HistoricalFirstCandlesDiagnostic:
    msg = message.get("msg") if isinstance(message.get("msg"), dict) else None
    body = msg.get("body") if isinstance(msg, dict) and isinstance(msg.get("body"), dict) else None
    collection_path, collection_length = _find_candidate_collection(message)
    return HistoricalFirstCandlesDiagnostic(
        first_candles_collection_count=collection_length or 0,
        event_name="first-candles",
        direction="server_to_client",
        top_level_type=_type_name(message),
        top_level_keys=_safe_key_tuple(list(message.keys())),
        msg_type=_type_name(msg),
        msg_keys=_safe_key_tuple(list(msg.keys()) if isinstance(msg, dict) else ()),
        body_type=_type_name(body),
        body_keys=_safe_key_tuple(list(body.keys()) if isinstance(body, dict) else ()),
        candidate_collection_path=collection_path,
        candidate_collection_length=collection_length,
    )


def _find_candidate_collection(value: Any, *, path: str = "", depth: int = 0) -> tuple[str | None, int | None]:
    if depth > TRACE_MAX_DEPTH or not isinstance(value, (dict, list)):
        return None, None
    if isinstance(value, list):
        for index, child in enumerate(value[:TRACE_MAX_LIST_ITEMS]):
            candidate_path, candidate_length = _find_candidate_collection(child, path=f"{path}.{index}" if path else str(index), depth=depth + 1)
            if candidate_path is not None:
                return candidate_path, candidate_length
        return None, None

    candles = value.get("candles")
    if isinstance(candles, list):
        return (f"{path}.candles" if path else "candles"), len(candles)
    candles_by_size = value.get("candles_by_size")
    if isinstance(candles_by_size, dict):
        return (f"{path}.candles_by_size" if path else "candles_by_size"), len(candles_by_size)

    for key in ("msg", "body", "data", "payload", "params"):
        child = value.get(key)
        if isinstance(child, (dict, list)):
            candidate_path, candidate_length = _find_candidate_collection(child, path=f"{path}.{key}" if path else key, depth=depth + 1)
            if candidate_path is not None:
                return candidate_path, candidate_length
    return None, None


def _collect_structure_paths(value: Any, *, path: str = "", depth: int = 0) -> tuple[tuple[str, ...], tuple[str, ...]]:
    array_paths: list[str] = []
    object_paths: list[str] = []
    _walk_structure_paths(value, path=path, depth=depth, array_paths=array_paths, object_paths=object_paths)
    return tuple(array_paths[:STRUCTURE_MAX_PATHS]), tuple(object_paths[:STRUCTURE_MAX_PATHS])


def _walk_structure_paths(value: Any, *, path: str, depth: int, array_paths: list[str], object_paths: list[str]) -> None:
    if depth > STRUCTURE_MAX_DEPTH or len(array_paths) + len(object_paths) >= STRUCTURE_MAX_PATHS:
        return
    if isinstance(value, list):
        if path:
            array_paths.append(path)
        for index, child in enumerate(value[:TRACE_MAX_LIST_ITEMS]):
            _walk_structure_paths(child, path=f"{path}.{index}" if path else str(index), depth=depth + 1, array_paths=array_paths, object_paths=object_paths)
        return
    if isinstance(value, dict):
        if path:
            object_paths.append(path)
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if any(marker in key_lower for marker in SENSITIVE_MARKERS):
                continue
            _walk_structure_paths(
                child,
                path=f"{path}.{key_text}" if path else key_text,
                depth=depth + 1,
                array_paths=array_paths,
                object_paths=object_paths,
            )


def _find_structural_collection(value: Any, *, path: str = "", depth: int = 0) -> tuple[str | None, str | None, int | None]:
    if depth > STRUCTURE_MAX_DEPTH:
        return None, None, None
    if isinstance(value, list):
        if _list_looks_like_collection(value):
            return path, "array", len(value)
        for index, child in enumerate(value[:TRACE_MAX_LIST_ITEMS]):
            candidate = _find_structural_collection(child, path=f"{path}.{index}" if path else str(index), depth=depth + 1)
            if candidate[0] is not None:
                return candidate
        return None, None, None
    if isinstance(value, dict):
        if path and _dict_keys_look_like_raw_sizes(value):
            return path, "object_indexed_by_raw_size", len(value)
        if path and _dict_looks_like_indexed_collection(value):
            return path, "object", len(value)
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if any(marker in key_lower for marker in SENSITIVE_MARKERS):
                continue
            candidate = _find_structural_collection(child, path=f"{path}.{key_text}" if path else key_text, depth=depth + 1)
            if candidate[0] is not None:
                return candidate
    return None, None, None


def _inner_event_name(value: dict[str, Any]) -> str | None:
    msg = value.get("msg")
    if isinstance(msg, dict):
        for key in ("name", "event", "type", "command", "method"):
            candidate = msg.get(key)
            if isinstance(candidate, str):
                return _safe_str(candidate)
        body = msg.get("body")
        if isinstance(body, dict):
            for key in ("name", "event", "type", "command", "method"):
                candidate = body.get(key)
                if isinstance(candidate, str):
                    return _safe_str(candidate)
    return None


def _has_any_field(value: Any, names: tuple[str, ...], *, depth: int = 0) -> bool:
    if depth > STRUCTURE_MAX_DEPTH:
        return False
    if isinstance(value, dict):
        if any(name in value for name in names):
            return True
        return any(_has_any_field(child, names, depth=depth + 1) for child in value.values())
    if isinstance(value, list):
        return any(_has_any_field(child, names, depth=depth + 1) for child in value[:TRACE_MAX_LIST_ITEMS])
    return False


def _collect_field_type_names(value: Any, *, depth: int = 0) -> tuple[set[str], set[str]]:
    numeric_fields: set[str] = set()
    string_fields: set[str] = set()
    if depth > STRUCTURE_MAX_DEPTH:
        return numeric_fields, string_fields
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if any(marker in key_lower for marker in SENSITIVE_MARKERS):
                continue
            if key_text in OUTBOUND_FIELD_NAMES:
                if isinstance(child, (int, float)) and not isinstance(child, bool):
                    numeric_fields.add(key_text)
                elif isinstance(child, str):
                    string_fields.add(key_text)
            child_numeric, child_string = _collect_field_type_names(child, depth=depth + 1)
            numeric_fields.update(child_numeric)
            string_fields.update(child_string)
    elif isinstance(value, list):
        for child in value[:TRACE_MAX_LIST_ITEMS]:
            child_numeric, child_string = _collect_field_type_names(child, depth=depth + 1)
            numeric_fields.update(child_numeric)
            string_fields.update(child_string)
    return numeric_fields, string_fields


def _outbound_shape_fingerprint(diagnostic: OutboundCandleRequestDiagnostic) -> str:
    parts = (
        diagnostic.event_name or "",
        diagnostic.inner_event_name or "",
        ",".join(diagnostic.top_level_keys),
        ",".join(diagnostic.msg_keys),
        ",".join(diagnostic.body_keys),
        str(diagnostic.has_active_id),
        str(diagnostic.has_size),
        str(diagnostic.has_count),
        str(diagnostic.has_from),
        str(diagnostic.has_to),
        str(diagnostic.has_limit),
        str(diagnostic.has_offset),
    )
    return "|".join(parts)


def _list_looks_like_collection(value: list[Any]) -> bool:
    if not value:
        return False
    inspected = [item for item in value[:TRACE_MAX_LIST_ITEMS] if isinstance(item, dict)]
    if not inspected:
        return False
    return sum(1 for item in inspected if _looks_like_candle_shape(item)) >= max(1, len(inspected) // 2)


def _dict_looks_like_indexed_collection(value: dict[str, Any]) -> bool:
    if not value:
        return False
    children = [child for child in list(value.values())[:TRACE_MAX_LIST_ITEMS] if isinstance(child, dict)]
    if not children:
        return False
    return sum(1 for child in children if _looks_like_candle_shape(child)) >= max(1, len(children) // 2)


def _dict_keys_look_like_raw_sizes(value: dict[str, Any]) -> bool:
    if not value:
        return False
    keys = list(value.keys())
    numeric_keys = [key for key in keys if _safe_int(key) is not None]
    return len(numeric_keys) == len(keys) and any(isinstance(child, dict) for child in value.values())


def _looks_like_candle_shape(value: dict[str, Any]) -> bool:
    has_time = any(name in value for name in ("from", "timestamp", "start_timestamp", "startTimestamp", "start", "at"))
    has_price = any(name in value for name in ("open", "o")) or any(name in value for name in ("close", "c"))
    return has_time or has_price


def _collect_collection_metadata(value: Any, *, depth: int = 0, active_id: Any = None, raw_size: Any = None) -> tuple[set[int], set[int], set[int]]:
    active_ids: set[int] = set()
    raw_sizes: set[int] = set()
    timestamps: set[int] = set()
    if depth > TRACE_MAX_DEPTH or not isinstance(value, (dict, list)):
        return active_ids, raw_sizes, timestamps

    if isinstance(value, list):
        for child in value[:MAX_ARRAY_ITEMS]:
            child_active_ids, child_raw_sizes, child_timestamps = _collect_collection_metadata(
                child, depth=depth + 1, active_id=active_id, raw_size=raw_size
            )
            active_ids.update(child_active_ids)
            raw_sizes.update(child_raw_sizes)
            timestamps.update(child_timestamps)
        return active_ids, raw_sizes, timestamps

    observed_active_id = _first_int_like(value, ("active_id", "activeId", "active", "asset_id")) or _safe_int(active_id)
    observed_raw_size = _first_int_like(value, ("size", "raw_size", "rawSize", "timeframe_size")) or _safe_int(raw_size)
    observed_timestamp = _first_int_like(value, ("from", "timestamp", "start_timestamp", "startTimestamp", "start", "at"))
    if observed_active_id is not None:
        active_ids.add(observed_active_id)
    if observed_raw_size is not None:
        raw_sizes.add(observed_raw_size)
    if observed_timestamp is not None:
        timestamps.add(observed_timestamp)

    candles = value.get("candles")
    if isinstance(candles, list):
        child_active_ids, child_raw_sizes, child_timestamps = _collect_collection_metadata(
            candles, depth=depth + 1, active_id=observed_active_id, raw_size=observed_raw_size
        )
        active_ids.update(child_active_ids)
        raw_sizes.update(child_raw_sizes)
        timestamps.update(child_timestamps)
    elif isinstance(candles, dict):
        for size, candle in candles.items():
            child_active_ids, child_raw_sizes, child_timestamps = _collect_collection_metadata(
                candle, depth=depth + 1, active_id=observed_active_id, raw_size=size
            )
            active_ids.update(child_active_ids)
            raw_sizes.update(child_raw_sizes)
            timestamps.update(child_timestamps)

    candles_by_size = value.get("candles_by_size")
    if isinstance(candles_by_size, dict):
        for size, candle in candles_by_size.items():
            child_active_ids, child_raw_sizes, child_timestamps = _collect_collection_metadata(
                candle, depth=depth + 1, active_id=observed_active_id, raw_size=size
            )
            active_ids.update(child_active_ids)
            raw_sizes.update(child_raw_sizes)
            timestamps.update(child_timestamps)

    for key in ("msg", "body", "data", "payload", "params"):
        child = value.get(key)
        if isinstance(child, (dict, list)):
            child_active_ids, child_raw_sizes, child_timestamps = _collect_collection_metadata(
                child, depth=depth + 1, active_id=observed_active_id, raw_size=observed_raw_size
            )
            active_ids.update(child_active_ids)
            raw_sizes.update(child_raw_sizes)
            timestamps.update(child_timestamps)
    for key, child in value.items():
        if key in {"msg", "body", "data", "payload", "params", "candles", "candles_by_size"}:
            continue
        key_lower = str(key).lower()
        if any(marker in key_lower for marker in SENSITIVE_MARKERS):
            continue
        if isinstance(child, (dict, list)):
            child_active_ids, child_raw_sizes, child_timestamps = _collect_collection_metadata(
                child, depth=depth + 1, active_id=observed_active_id, raw_size=observed_raw_size
            )
            active_ids.update(child_active_ids)
            raw_sizes.update(child_raw_sizes)
            timestamps.update(child_timestamps)
    return active_ids, raw_sizes, timestamps


def _first_int_like(source: dict[str, Any], names: tuple[str, ...]) -> int | None:
    for name in names:
        if name in source:
            value = _safe_int(source[name])
            if value is not None:
                return value
    return None


def _type_name(value: Any) -> str:
    if isinstance(value, list):
        return "array"
    if value is None:
        return "null"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _safe_key_tuple(value: Any, *, hide_market_fields: bool = False) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    keys = []
    for item in value:
        text = str(item)
        lowered = text.lower()
        if _has_sensitive_marker_text(lowered):
            continue
        if hide_market_fields and lowered in OHLC_MARKERS:
            continue
        keys.append(text)
        if len(keys) >= 80:
            break
    return tuple(keys)


def _safe_str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    lowered = value.lower()
    if _has_sensitive_marker_text(lowered):
        return None
    return value[:160]


def _safe_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _safe_request_ref(value: Any) -> str | None:
    text = _safe_str(value)
    if text is None:
        return None
    if not text.startswith("request-"):
        return None
    suffix = text.removeprefix("request-")
    if not suffix.isdigit():
        return None
    return text


def _safe_path(value: Any) -> str | None:
    text = _safe_str(value)
    if text is None:
        return None
    lowered = text.lower()
    if _has_sensitive_marker_text(lowered):
        return None
    return text


def _safe_path_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    paths = []
    for item in value:
        path = _safe_path(item)
        if path is None:
            continue
        paths.append(path)
        if len(paths) >= STRUCTURE_MAX_PATHS:
            break
    return tuple(paths)


def _safe_field_name_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    fields = []
    for item in value:
        text = _safe_str(item)
        if text is None or text not in OUTBOUND_FIELD_NAMES:
            continue
        fields.append(text)
        if len(fields) >= 40:
            break
    return tuple(fields)


def _safe_method_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    methods = []
    for item in value:
        text = _safe_runtime_name(item)
        if text is None:
            continue
        methods.append(text)
        if len(methods) >= 40:
            break
    return tuple(methods)


def _safe_correlation_status(value: Any) -> str | None:
    text = _safe_str(value)
    if text in {"CONFIRMED_BY_REQUEST_ID", "TEMPORAL_CANDIDATE", "UNRELATED"}:
        return text
    return None


def _safe_transport(value: Any) -> str | None:
    text = _safe_str(value)
    if text in {"fetch_request", "fetch_response", "xhr_request", "xhr_response", "websocket"}:
        return text
    return None


def _safe_http_method(value: Any) -> str | None:
    text = _safe_str(value)
    if text is None:
        return None
    upper = text.upper()
    if upper in {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}:
        return upper
    return None


def _safe_host(value: Any) -> str | None:
    text = _safe_str(value)
    if text is None:
        return None
    lowered = text.lower()
    if _has_sensitive_marker_text(lowered):
        return None
    return lowered[:120]


def _safe_content_type(value: Any) -> str | None:
    text = _safe_str(value)
    if text is None:
        return None
    return text.split(";")[0].lower()[:120]


def _safe_runtime_source_type(value: Any) -> str | None:
    text = _safe_str(value)
    allowed = {
        "window_global",
        "react",
        "redux",
        "mobx",
        "zustand",
        "chart_engine",
        "datafeed",
        "indexeddb",
        "localstorage",
        "sessionstorage",
        "worker",
        "unknown",
    }
    return text if text in allowed else None


def _safe_collection_type(value: Any) -> str | None:
    text = _safe_str(value)
    return text if text in {"array", "object", "object_indexed", "map", "set", "unknown"} else None


def _safe_runtime_name(value: Any) -> str | None:
    text = _safe_str(value)
    if text is None:
        return None
    sanitized = "".join(char if char.isalnum() or char in "._-$[]" else "_" for char in text)[:120]
    lowered = sanitized.lower()
    if any(marker in lowered for marker in SENSITIVE_MARKERS):
        return None
    return sanitized or None


def _safe_runtime_ref(value: Any) -> str | None:
    text = _safe_runtime_name(value)
    if text is None:
        return None
    if not text.startswith("runtime_candidate_"):
        return None
    return text


def _safe_scalar(value: Any) -> int | float | str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return value
    return _safe_str(value)


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
            if _has_sensitive_marker_text(key_text):
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


def _has_sensitive_marker_text(text: str) -> bool:
    if "bearer " in text:
        return True
    for marker in SENSITIVE_MARKERS:
        if marker == "har":
            parts = [part for part in "".join(char if char.isalnum() else " " for char in text).split() if part]
            if marker in parts:
                return True
            continue
        if marker in text:
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
