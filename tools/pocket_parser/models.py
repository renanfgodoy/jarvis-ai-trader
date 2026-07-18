from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Direction = Literal["sent", "received", "unknown"]
MarketType = Literal["OTC", "REGULAR"]

SUPPORTED_PERIODS = {60: "M1", 300: "M5", 900: "M15"}


@dataclass(frozen=True)
class PocketSocketEvent:
    event_name: str | None
    direction: Direction
    timestamp: float | None
    payload: Any
    source_har: str
    socket_host: str
    socket_path: str
    frame_index: int
    session_index: int
    frame_kind: str
    parse_error: str | None = None


@dataclass(frozen=True)
class PocketAssetChanged:
    asset: str
    display_name: str
    market_type: MarketType
    is_otc: bool
    period: int
    timeframe: str
    timestamp: float | None


@dataclass(frozen=True)
class PocketNormalizedCandle:
    provider: str
    symbol: str
    period: int
    timeframe: str
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    is_closed: bool
    source_event: str
    source_har: str
    session_index: int


@dataclass(frozen=True)
class PocketRealtimeTick:
    asset: str
    price: float
    timestamp: float
    source_event: str
    sequence: int
    source_har: str
    session_index: int


@dataclass(frozen=True)
class PocketHistoryBatch:
    asset: str
    period: int
    timeframe: str
    candles: tuple[PocketNormalizedCandle, ...]
    history_count: int
    first_timestamp: float | None
    last_timestamp: float | None
    source_event: str


@dataclass(frozen=True)
class PocketAssetInfo:
    symbol: str
    display_name: str
    is_otc: bool
    market_type: MarketType
    is_available: bool | None
    payout: float | None
    supported_periods: tuple[int, ...]
    raw_fields_detected: tuple[str, ...]
    unknown_numeric_fields: tuple[int, ...]
    unknown_boolean_fields: tuple[int, ...]


@dataclass
class Rejection:
    code: str
    event_name: str
    source_har: str
    session_index: int
    frame_index: int
    detail: str


@dataclass
class PocketReplayResult:
    har_paths: tuple[str, ...]
    sessions_processed: int = 0
    frames_total: int = 0
    frames_valid: int = 0
    frames_invalid: int = 0
    socketio_events: int = 0
    change_symbols: list[PocketAssetChanged] = field(default_factory=list)
    history_batches: list[PocketHistoryBatch] = field(default_factory=list)
    ticks: list[PocketRealtimeTick] = field(default_factory=list)
    assets: list[PocketAssetInfo] = field(default_factory=list)
    chart_updates: list[dict[str, Any]] = field(default_factory=list)
    unknown_events: dict[str, int] = field(default_factory=dict)
    rejections: list[Rejection] = field(default_factory=list)
    parse_errors: list[Rejection] = field(default_factory=list)

