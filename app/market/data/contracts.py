from dataclasses import dataclass
from typing import Literal


MarketEnvironment = Literal["DEMO", "REAL"]
MarketDataQuality = Literal["SIMULATED", "REAL", "DELAYED", "UNAVAILABLE"]


@dataclass(frozen=True)
class MarketAsset:
    symbol: str
    display_name: str
    status: str
    provider: str
    data_quality: MarketDataQuality


@dataclass(frozen=True)
class MarketContext:
    asset: str
    timeframe: str
    broker: str
    environment: MarketEnvironment
    currency: str


@dataclass(frozen=True)
class MarketSource:
    provider: str
    origin: str
    data_quality: MarketDataQuality | str
    connector_status: str


@dataclass(frozen=True)
class MarketStatus:
    market: str
    connection: str
    availability: str
    last_update: str


@dataclass(frozen=True)
class MarketAvailability:
    total_assets: int | str
    open_assets: int | str
    closed_assets: int | str
    selected_asset_status: str


@dataclass(frozen=True)
class MarketSnapshot:
    context: MarketContext
    source: MarketSource
    status: MarketStatus
    availability: MarketAvailability
    market_ready: bool
