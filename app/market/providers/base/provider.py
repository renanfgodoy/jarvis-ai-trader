from __future__ import annotations

from app.market.providers.base.contracts import ProviderUnsupportedOperation
from app.market.providers.base.models import (
    ProviderAssets,
    ProviderCapability,
    ProviderContext,
    ProviderHealth,
    ProviderHistory,
    ProviderReadiness,
    ProviderStatus,
    ProviderTick,
)


class BaseProvider:
    def __init__(
        self,
        provider_name: str,
        *,
        capabilities: frozenset[ProviderCapability] | None = None,
        status: ProviderStatus = "stopped",
    ) -> None:
        self._provider_name = provider_name
        self._capabilities = capabilities or frozenset()
        self._status = status

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return self._capabilities

    def provider_name(self) -> str:
        return self._provider_name

    def start(self) -> None:
        self._status = "online"

    def stop(self) -> None:
        self._status = "stopped"

    def status(self) -> ProviderContext:
        return self.get_context()

    def get_context(self) -> ProviderContext:
        return ProviderContext(
            provider=self._provider_name,
            asset=None,
            symbol=None,
            timeframe=None,
            period=None,
            connection_state=self._status,
            history_state="unknown",
            readiness="unknown",
            last_price=None,
            history_count=0,
            timestamp=None,
        )

    def get_assets(self) -> ProviderAssets:
        raise ProviderUnsupportedOperation("assets are not supported by this provider")

    def get_history(self, symbol: str, period: int, limit: int | None = None) -> ProviderHistory:
        raise ProviderUnsupportedOperation("history is not supported by this provider")

    def get_ticks(self, symbol: str, period: int, limit: int | None = None) -> tuple[ProviderTick, ...]:
        raise ProviderUnsupportedOperation("ticks are not supported by this provider")

    def get_readiness(self, symbol: str, period: int) -> ProviderReadiness:
        raise ProviderUnsupportedOperation("readiness is not supported by this provider")

    def health(self) -> ProviderHealth:
        return ProviderHealth(provider=self._provider_name, status=self._status, read_only=True)
