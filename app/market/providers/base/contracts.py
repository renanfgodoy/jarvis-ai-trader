from __future__ import annotations

from typing import Callable, Mapping, Protocol, runtime_checkable

from app.market.providers.base.models import (
    ProviderAssets,
    ProviderContext,
    ProviderHealth,
    ProviderHistory,
    ProviderReadiness,
    ProviderTick,
)


class ProviderError(Exception):
    error_code = "PROVIDER_ERROR"


class ProviderAlreadyRegisteredError(ProviderError):
    error_code = "PROVIDER_ALREADY_REGISTERED"


class ProviderNotFoundError(ProviderError):
    error_code = "PROVIDER_NOT_FOUND"


class ProviderInvalidError(ProviderError):
    error_code = "PROVIDER_INVALID"


class ProviderUnsupportedOperation(ProviderError):
    error_code = "PROVIDER_UNSUPPORTED_OPERATION"


@runtime_checkable
class MarketProvider(Protocol):
    def provider_name(self) -> str: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def status(self) -> ProviderContext: ...

    def get_context(self) -> ProviderContext: ...

    def get_assets(self) -> ProviderAssets: ...

    def get_history(self, symbol: str, period: int, limit: int | None = None) -> ProviderHistory: ...

    def get_ticks(self, symbol: str, period: int, limit: int | None = None) -> tuple[ProviderTick, ...]: ...

    def get_readiness(self, symbol: str, period: int) -> ProviderReadiness: ...

    def health(self) -> ProviderHealth: ...


ProviderFactoryCallable = Callable[[Mapping[str, object]], MarketProvider]
