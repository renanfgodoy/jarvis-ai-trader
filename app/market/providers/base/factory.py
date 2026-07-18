from __future__ import annotations

from typing import Mapping

from app.market.providers.base.contracts import (
    MarketProvider,
    ProviderAlreadyRegisteredError,
    ProviderFactoryCallable,
    ProviderInvalidError,
    ProviderNotFoundError,
)


class ProviderFactory:
    def __init__(self) -> None:
        self._builders: dict[str, ProviderFactoryCallable] = {}

    def register_builder(self, provider_name: str, builder: ProviderFactoryCallable) -> None:
        normalized_name = provider_name.strip()
        if not normalized_name:
            raise ProviderInvalidError("provider_name is required")
        if not callable(builder):
            raise ProviderInvalidError("builder must be callable")
        if normalized_name in self._builders:
            raise ProviderAlreadyRegisteredError(normalized_name)
        self._builders[normalized_name] = builder

    def register(self, provider_name: str, builder: ProviderFactoryCallable) -> None:
        self.register_builder(provider_name, builder)

    def unregister_builder(self, provider_name: str) -> None:
        if provider_name not in self._builders:
            raise ProviderNotFoundError(provider_name)
        del self._builders[provider_name]

    def create(self, provider_name: str, config: Mapping[str, object] | None = None) -> MarketProvider:
        builder = self._builders.get(provider_name)
        if builder is None:
            raise ProviderNotFoundError(provider_name)
        provider = builder(config or {})
        if not isinstance(provider, MarketProvider):
            raise ProviderInvalidError(provider_name)
        return provider

    def has_builder(self, provider_name: str) -> bool:
        return provider_name in self._builders

    def list_builders(self) -> tuple[str, ...]:
        return tuple(sorted(self._builders.keys()))

    def list(self) -> tuple[str, ...]:
        return self.list_builders()

    def clear(self) -> None:
        self._builders.clear()
