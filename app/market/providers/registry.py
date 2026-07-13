from __future__ import annotations

from app.market.providers.base import MarketDataProvider


class MarketProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, MarketDataProvider] = {}

    def register(self, provider: MarketDataProvider) -> None:
        self._providers[provider.provider_name] = provider

    def list_provider_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers.keys()))

    def get(self, provider_name: str) -> MarketDataProvider | None:
        return self._providers.get(provider_name)
