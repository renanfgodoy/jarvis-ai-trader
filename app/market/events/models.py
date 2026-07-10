from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

MarketEventStatus = Literal["parsed", "unsupported", "invalid"]
MarketEventSource = Literal["polarium"]


@dataclass(frozen=True)
class MarketEventMetadata:
    source: MarketEventSource
    event_name: str | None
    request_id: str | None = None
    source_verified: bool = True


@dataclass(frozen=True)
class NormalizedMarketCandle:
    active_id: int | None
    symbol: None
    raw_size: int
    timeframe: None
    start_timestamp: int
    end_timestamp: int
    open: float
    close: float
    low_candidate: float
    high_candidate: float
    volume: float
    source: MarketEventSource
    source_event: str
    source_verified: bool
    mapping_verified: bool
    mapping_notes: tuple[str, ...]


@dataclass(frozen=True)
class MarketEventParseError:
    code: str
    message: str
    path: str


@dataclass(frozen=True)
class MarketEventRouteResult:
    status: MarketEventStatus
    metadata: MarketEventMetadata
    candles: tuple[NormalizedMarketCandle, ...] = ()
    errors: tuple[MarketEventParseError, ...] = ()
    raw_event: dict[str, Any] | None = None
