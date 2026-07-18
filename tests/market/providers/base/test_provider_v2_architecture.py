from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from app.market.providers.base import (
    BaseProvider,
    MarketProvider,
    ProviderAlreadyRegisteredError,
    ProviderAsset,
    ProviderAssets,
    ProviderCandle,
    ProviderFactory,
    ProviderHealth,
    ProviderHistory,
    ProviderNotFoundError,
    ProviderReadiness,
    ProviderRegistry,
    ProviderTick,
    ProviderUnsupportedOperation,
)


class FakeProvider(BaseProvider):
    def __init__(self, provider_name: str = "fake") -> None:
        super().__init__(provider_name, capabilities=frozenset({"assets", "history", "ticks", "read_only"}))

    def get_assets(self) -> ProviderAssets:
        return ProviderAssets(
            provider=self.provider_name(),
            assets=(
                ProviderAsset(
                    provider=self.provider_name(),
                    symbol="FAKE",
                    display_name="Fake Asset",
                    market_type="TEST",
                    supported_periods=(60, 300),
                    is_open=True,
                ),
            ),
            timestamp=1,
            source="fake",
        )

    def get_history(self, symbol: str, period: int, limit: int | None = None) -> ProviderHistory:
        candle = ProviderCandle(
            provider=self.provider_name(),
            symbol=symbol,
            period=period,
            timestamp=1000,
            open=1.0,
            high=1.2,
            low=0.9,
            close=1.1,
            volume=None,
            source="fake",
            is_closed=True,
        )
        candles = (candle,) if limit != 0 else ()
        return ProviderHistory(
            provider=self.provider_name(),
            symbol=symbol,
            period=period,
            candles=candles,
            history_count=len(candles),
            timestamp=1000,
            source="fake",
        )

    def get_ticks(self, symbol: str, period: int, limit: int | None = None) -> tuple[ProviderTick, ...]:
        return (
            ProviderTick(
                provider=self.provider_name(),
                symbol=symbol,
                period=period,
                timestamp=1001,
                price=1.1,
                source="fake",
            ),
        )

    def get_readiness(self, symbol: str, period: int) -> ProviderReadiness:
        return ProviderReadiness(
            provider=self.provider_name(),
            symbol=symbol,
            period=period,
            state="ready",
            history_count=1,
            required_history_count=1,
            analysis_blocked=False,
        )


def test_fake_provider_implements_market_provider_contract() -> None:
    provider = FakeProvider()

    assert isinstance(provider, MarketProvider)
    assert provider.provider_name() == "fake"
    assert provider.get_assets().assets[0].symbol == "FAKE"
    assert provider.get_history("FAKE", 60).history_count == 1
    assert provider.get_ticks("FAKE", 60)[0].price == 1.1
    assert provider.get_readiness("FAKE", 60).state == "ready"
    assert isinstance(provider.health(), ProviderHealth)


def test_registry_registers_lists_gets_and_switches_current_provider() -> None:
    registry = ProviderRegistry()
    provider = FakeProvider("fake-a")

    registry.register(provider)
    registry.set_current("fake-a")

    assert registry.list() == ("fake-a",)
    assert registry.get("fake-a") is provider
    assert registry.current() is provider


def test_registry_rejects_duplicate_and_unknown_providers() -> None:
    registry = ProviderRegistry()
    registry.register(FakeProvider("fake-a"))

    with pytest.raises(ProviderAlreadyRegisteredError):
        registry.register(FakeProvider("fake-a"))

    with pytest.raises(ProviderNotFoundError):
        registry.get("missing")

    with pytest.raises(ProviderNotFoundError):
        registry.unregister("missing")


def test_factory_creates_provider_from_registered_builder() -> None:
    factory = ProviderFactory()
    factory.register("fake", lambda config: FakeProvider(str(config["provider_name"])))

    provider = factory.create("fake", {"provider_name": "fake"})

    assert provider.provider_name() == "fake"
    assert factory.list() == ("fake",)


def test_factory_rejects_unknown_provider() -> None:
    factory = ProviderFactory()

    with pytest.raises(ProviderNotFoundError):
        factory.create("missing")


def test_base_provider_default_operations_are_explicitly_unsupported() -> None:
    provider = BaseProvider("base")

    with pytest.raises(ProviderUnsupportedOperation):
        provider.get_assets()

    with pytest.raises(ProviderUnsupportedOperation):
        provider.get_history("BASE", 60)

    with pytest.raises(ProviderUnsupportedOperation):
        provider.get_ticks("BASE", 60)

    with pytest.raises(ProviderUnsupportedOperation):
        provider.get_readiness("BASE", 60)


def test_base_provider_files_do_not_import_concrete_providers() -> None:
    base_dir = Path("app/market/providers/base")
    forbidden = ("pocket", "polarium", "iq_option")

    for path in base_dir.glob("*.py"):
        source = path.read_text()
        for name in forbidden:
            assert f"app.market.providers.{name}" not in source


def test_market_provider_contract_contains_required_methods() -> None:
    required_methods = {
        "provider_name",
        "start",
        "stop",
        "status",
        "get_context",
        "get_assets",
        "get_history",
        "get_ticks",
        "get_readiness",
        "health",
    }

    assert required_methods.issubset(set(dir(MarketProvider)))
    for method_name in required_methods:
        assert inspect.isfunction(getattr(MarketProvider, method_name))
