from __future__ import annotations

from typing import Protocol

from app.market.providers.base.contracts import (
    MarketProvider,
    ProviderAlreadyRegisteredError,
    ProviderError,
    ProviderFactoryCallable,
    ProviderInvalidError,
    ProviderNotFoundError,
    ProviderUnsupportedOperation,
)
from app.market.providers.base.factory import ProviderFactory
from app.market.providers.base.models import (
    ProviderAsset,
    ProviderAssets,
    ProviderCandle,
    ProviderCapability,
    ProviderContext,
    ProviderHealth,
    ProviderHistory,
    ProviderReadiness,
    ProviderStatus,
    ProviderTick,
)
from app.market.providers.base.provider import BaseProvider
from app.market.providers.base.registry import ProviderRegistry
from app.market.providers.models import MarketAsset, MarketCandleBatch, MarketCandleRequest, MarketProviderStatus


class MarketDataProvider(Protocol):
    provider_name: str

    def connection_status(self) -> MarketProviderStatus: ...

    def list_assets(self, market_type: str) -> tuple[MarketAsset, ...]: ...

    def get_candles(self, request: MarketCandleRequest) -> MarketCandleBatch: ...


__all__ = [
    "BaseProvider",
    "MarketDataProvider",
    "MarketProvider",
    "ProviderAlreadyRegisteredError",
    "ProviderAsset",
    "ProviderAssets",
    "ProviderCandle",
    "ProviderCapability",
    "ProviderContext",
    "ProviderError",
    "ProviderFactory",
    "ProviderFactoryCallable",
    "ProviderHealth",
    "ProviderHistory",
    "ProviderInvalidError",
    "ProviderNotFoundError",
    "ProviderReadiness",
    "ProviderRegistry",
    "ProviderStatus",
    "ProviderTick",
    "ProviderUnsupportedOperation",
]
