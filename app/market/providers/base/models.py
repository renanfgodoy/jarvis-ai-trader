from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Mapping


ProviderCapability = Literal["assets", "history", "ticks", "realtime", "read_only"]
ProviderStatus = Literal["disabled", "stopped", "starting", "online", "degraded", "error"]


@dataclass(frozen=True, slots=True)
class ProviderContext:
    provider: str
    asset: str | None
    symbol: str | None
    timeframe: str | None
    period: int | None
    connection_state: ProviderStatus
    history_state: str
    readiness: str
    last_price: float | None
    history_count: int
    timestamp: int | None
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderAsset:
    provider: str
    symbol: str
    display_name: str
    market_type: str
    supported_periods: tuple[int, ...]
    is_open: bool
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderAssets:
    provider: str
    assets: tuple[ProviderAsset, ...]
    timestamp: int | None
    source: str


@dataclass(frozen=True, slots=True)
class ProviderCandle:
    provider: str
    symbol: str
    period: int
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    source: str
    is_closed: bool


@dataclass(frozen=True, slots=True)
class ProviderHistory:
    provider: str
    symbol: str
    period: int
    candles: tuple[ProviderCandle, ...]
    history_count: int
    timestamp: int | None
    source: str


@dataclass(frozen=True, slots=True)
class ProviderTick:
    provider: str
    symbol: str
    period: int | None
    timestamp: int
    price: float
    source: str
    sequence: int | None = None


@dataclass(frozen=True, slots=True)
class ProviderReadiness:
    provider: str
    symbol: str | None
    period: int | None
    state: str
    history_count: int
    required_history_count: int
    analysis_blocked: bool
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    provider: str
    status: ProviderStatus
    read_only: bool
    last_error_code: str | None = None
    metrics: Mapping[str, object] = field(default_factory=dict)
