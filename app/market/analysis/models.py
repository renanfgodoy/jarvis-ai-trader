from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.market.providers.base.models import ProviderCandle, ProviderTick


MarketState = Literal["EMPTY", "BOOTSTRAPPING", "LIMITED", "READY", "ERROR"]


@dataclass(frozen=True, slots=True)
class MarketStatistics:
    total_candles: int
    total_ticks: int
    first_timestamp: int | None
    last_timestamp: int | None
    duration: int | None
    average_price: float | None
    highest_price: float | None
    lowest_price: float | None
    price_range: float | None


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    current_price: float | None
    last_open: float | None
    last_close: float | None
    last_high: float | None
    last_low: float | None
    last_volume: float | None


@dataclass(frozen=True, slots=True)
class MarketMetadata:
    provider_name: str
    provider_version: str | None
    analysis_engine_version: str
    generated_at: int
    timezone: str


@dataclass(frozen=True, slots=True)
class MarketHealth:
    status: MarketState
    warnings: tuple[str, ...]
    errors: tuple[str, ...]
    quality_score: float
    history_ready: bool
    tick_ready: bool


@dataclass(frozen=True, slots=True)
class MarketAnalysis:
    provider: str
    symbol: str
    asset: str | None
    market_type: str | None
    timeframe: str | None
    period: int
    candles: tuple[ProviderCandle, ...]
    ticks: tuple[ProviderTick, ...]
    snapshot: MarketSnapshot
    statistics: MarketStatistics
    metadata: MarketMetadata
    health: MarketHealth
    created_at: int
    analysis_version: str
