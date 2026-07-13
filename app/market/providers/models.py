from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketProviderStatus:
    provider: str
    enabled: bool
    configured: bool
    connected: bool
    account_mode: str
    read_only: bool
    last_connected_at: str | None = None
    last_candle_at: str | None = None
    last_symbol: str | None = None
    last_raw_size: int | None = None
    last_batch_count: int = 0
    reconnect_count: int = 0
    last_error_code: str | None = None
    library_source: str | None = None
    library_version: str | None = None

    def sanitized(self) -> dict:
        return {
            "provider": self.provider,
            "enabled": self.enabled,
            "configured": self.configured,
            "connected": self.connected,
            "account_mode": self.account_mode,
            "read_only": self.read_only,
            "last_connected_at": self.last_connected_at,
            "last_candle_at": self.last_candle_at,
            "last_symbol": self.last_symbol,
            "last_raw_size": self.last_raw_size,
            "last_batch_count": self.last_batch_count,
            "reconnect_count": self.reconnect_count,
            "last_error_code": self.last_error_code,
            "library_source": self.library_source,
            "library_version": self.library_version,
        }


@dataclass(frozen=True)
class MarketAsset:
    symbol: str
    display_name: str
    market_type: str
    is_otc: bool
    is_open: bool
    provider: str

    def sanitized(self) -> dict:
        return {
            "symbol": self.symbol,
            "display_name": self.display_name,
            "market_type": self.market_type,
            "is_otc": self.is_otc,
            "is_open": self.is_open,
            "provider": self.provider,
        }


@dataclass(frozen=True)
class MarketCandleRequest:
    symbol: str
    raw_size: int
    limit: int
    market_type: str = "OTC"


@dataclass(frozen=True)
class ProviderCandle:
    provider: str
    market_type: str
    symbol: str
    raw_size: int
    start_timestamp: int
    end_timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    is_otc: bool
    source_verified: bool


@dataclass(frozen=True)
class MarketCandleBatch:
    provider: str
    market_type: str
    symbol: str
    raw_size: int
    candles: tuple[ProviderCandle, ...]
    rejected: int = 0
    last_error_code: str | None = None

    def sanitized(self) -> dict:
        return {
            "provider": self.provider,
            "market_type": self.market_type,
            "symbol": self.symbol,
            "raw_size": self.raw_size,
            "count": len(self.candles),
            "rejected": self.rejected,
            "last_error_code": self.last_error_code,
        }
