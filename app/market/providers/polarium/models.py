from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.market.store.types import CandleStoreWriteResult

POLARIUM_PROVIDER = "POLARIUM"
POLARIUM_MARKET_TYPE = "POLARIUM_AUTHORIZED_MARKET"
POLARIUM_PLURAL_EVENT = "candles-generated"
POLARIUM_SINGULAR_EVENT = "candle-generated"
POLARIUM_SUPPORTED_SIZES = (60, 300, 900)

MarketFeedStatus = Literal["processed", "dropped", "invalid"]


@dataclass(frozen=True)
class PolariumMarketCandle:
    active_id: int
    symbol: str | None
    raw_size: int
    start_timestamp: int
    end_timestamp: int
    open: float
    close: float
    low: float
    high: float
    volume: float


@dataclass(frozen=True)
class PolariumMarketEvent:
    event_name: str
    active_id: int
    symbol: str | None
    timestamp: int | None
    bid: float | None
    ask: float | None
    value: float | None
    candles: tuple[PolariumMarketCandle, ...]


@dataclass(frozen=True)
class PolariumMarketFeedResult:
    status: MarketFeedStatus
    event_name: str | None
    active_id: int | None
    processed: int = 0
    stored: int = 0
    updated: int = 0
    ignored: int = 0
    dropped_reason: str | None = None
    store_results: tuple[CandleStoreWriteResult, ...] = ()


@dataclass(frozen=True)
class PolariumRuntimeStatus:
    read_only: bool
    connected: bool
    authenticated: bool
    market_socket_ready: bool
    subscriptions: tuple[int, ...]
    received: int
    processed: int
    dropped: int
    forbidden: int
    reconnects: int
    latest_active_id: int | None = None
    latest_symbol: str | None = None
    latest_raw_sizes: tuple[int, ...] = ()
    session_context: dict | None = None
    bootstrap: dict | None = None

    def sanitized(self) -> dict:
        return {
            "provider": POLARIUM_PROVIDER,
            "read_only": self.read_only,
            "connected": self.connected,
            "authenticated": self.authenticated,
            "market_socket_ready": self.market_socket_ready,
            "subscriptions": list(self.subscriptions),
            "received": self.received,
            "processed": self.processed,
            "dropped": self.dropped,
            "forbidden": self.forbidden,
            "reconnects": self.reconnects,
            "latest_active_id": self.latest_active_id,
            "latest_symbol": self.latest_symbol,
            "latest_raw_sizes": list(self.latest_raw_sizes),
            "session_context": self.session_context,
            "bootstrap": self.bootstrap,
        }
