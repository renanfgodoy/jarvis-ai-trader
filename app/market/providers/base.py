from __future__ import annotations

from typing import Protocol

from app.market.providers.models import MarketAsset, MarketCandleBatch, MarketCandleRequest, MarketProviderStatus


class MarketDataProvider(Protocol):
    provider_name: str

    def connection_status(self) -> MarketProviderStatus: ...

    def list_assets(self, market_type: str) -> tuple[MarketAsset, ...]: ...

    def get_candles(self, request: MarketCandleRequest) -> MarketCandleBatch: ...
