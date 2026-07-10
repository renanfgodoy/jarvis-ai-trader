from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol

from app.models.candle import Timeframe

MarketDataSource = Literal["POLARIUM", "QUADCODE", "TRADINGVIEW", "SIMULATED", "UNKNOWN"]
MarketDataAvailability = Literal["AVAILABLE", "UNAVAILABLE", "PARTIAL", "UNKNOWN"]


@dataclass(frozen=True)
class MarketDataCandle:
    """Normalized internal candle contract for future real market data adapters.

    This contract is intentionally data-only. It does not fetch, infer, synthesize,
    or backfill candles. Adapter implementations must populate it only from
    observed provider payloads.
    """

    symbol: str
    timeframe: Timeframe
    open: float
    high: float
    low: float
    close: float
    timestamp: datetime
    source: MarketDataSource
    confirmed: bool


@dataclass(frozen=True)
class MarketDataAsset:
    symbol: str
    provider_symbol: str | None
    status: str
    source: MarketDataSource
    updated_at: datetime | None = None


@dataclass(frozen=True)
class MarketDataDiscoveryStatus:
    assets: MarketDataAvailability
    candles: MarketDataAvailability
    timestamps: MarketDataAvailability
    stream: MarketDataAvailability
    snapshot: MarketDataAvailability
    history: MarketDataAvailability
    reason: str


class MarketDataAdapter(Protocol):
    """Read-only adapter boundary for real market data discovery.

    Implementations must use authorized sessions only and must not send orders.
    """

    source: MarketDataSource

    def discovery_status(self) -> MarketDataDiscoveryStatus:
        """Return what the adapter can prove from observed evidence."""

    def list_assets(self) -> list[MarketDataAsset]:
        """Return observed assets only."""

    def get_candles(self, symbol: str, timeframe: Timeframe, limit: int) -> list[MarketDataCandle]:
        """Return observed OHLC candles only; never generate synthetic candles."""
