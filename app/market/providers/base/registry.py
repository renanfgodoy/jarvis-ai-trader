from __future__ import annotations

from threading import RLock

from app.market.providers.base.contracts import (
    MarketProvider,
    ProviderAlreadyRegisteredError,
    ProviderInvalidError,
    ProviderNotFoundError,
)


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, MarketProvider] = {}
        self._current_provider_name: str | None = None
        self._lock = RLock()

    def register(self, provider: MarketProvider) -> None:
        if not isinstance(provider, MarketProvider):
            raise ProviderInvalidError("provider must implement MarketProvider")
        provider_name = provider.provider_name()
        if not provider_name.strip():
            raise ProviderInvalidError("provider_name is required")
        with self._lock:
            if provider_name in self._providers:
                raise ProviderAlreadyRegisteredError(provider_name)
            self._providers[provider_name] = provider

    def unregister(self, provider_name: str) -> None:
        with self._lock:
            if provider_name not in self._providers:
                raise ProviderNotFoundError(provider_name)
            del self._providers[provider_name]
            if self._current_provider_name == provider_name:
                self._current_provider_name = None

    def get(self, provider_name: str) -> MarketProvider:
        with self._lock:
            provider = self._providers.get(provider_name)
            if provider is None:
                raise ProviderNotFoundError(provider_name)
            return provider

    def exists(self, provider_name: str) -> bool:
        with self._lock:
            return provider_name in self._providers

    def list(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._providers.keys()))

    def current(self) -> MarketProvider | None:
        with self._lock:
            if self._current_provider_name is None:
                return None
            return self.get(self._current_provider_name)

    def set_current(self, provider_name: str) -> None:
        self.get(provider_name)
        with self._lock:
            self._current_provider_name = provider_name

    def clear(self) -> None:
        with self._lock:
            self._providers.clear()
            self._current_provider_name = None
