from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from app.market.providers.base import (
    BaseProvider,
    ProviderAlreadyRegisteredError,
    ProviderFactory,
    ProviderInvalidError,
    ProviderNotFoundError,
    ProviderRegistry,
)
from app.market.providers.pocket import (
    FakePocketProviderAdapter,
    FakePocketProviderBuilder,
    PocketProviderAdapter,
    PocketProviderBuilder,
)
from app.market.providers.pocket.runtime import PocketMarketRuntime


class MinimalProvider(BaseProvider):
    pass


def test_factory_registers_lists_detects_creates_and_unregisters_builder() -> None:
    factory = ProviderFactory()

    factory.register_builder("minimal", lambda config: MinimalProvider(str(config["name"])))

    assert factory.has_builder("minimal") is True
    assert factory.list_builders() == ("minimal",)
    assert factory.create("minimal", {"name": "created"}).provider_name() == "created"

    factory.unregister_builder("minimal")

    assert factory.has_builder("minimal") is False
    assert factory.list_builders() == ()


def test_factory_rejects_duplicate_missing_and_invalid_builders() -> None:
    factory = ProviderFactory()
    factory.register_builder("minimal", lambda config: MinimalProvider("minimal"))

    with pytest.raises(ProviderAlreadyRegisteredError):
        factory.register_builder("minimal", lambda config: MinimalProvider("minimal-2"))

    with pytest.raises(ProviderInvalidError):
        factory.register_builder("", lambda config: MinimalProvider("empty"))

    with pytest.raises(ProviderInvalidError):
        factory.register_builder("invalid", object())  # type: ignore[arg-type]

    with pytest.raises(ProviderNotFoundError):
        factory.unregister_builder("missing")

    with pytest.raises(ProviderNotFoundError):
        factory.create("missing")


def test_factory_rejects_builder_that_returns_invalid_provider() -> None:
    factory = ProviderFactory()
    factory.register_builder("bad", lambda config: object())  # type: ignore[return-value]

    with pytest.raises(ProviderInvalidError):
        factory.create("bad")


def test_factory_clear_removes_all_builders() -> None:
    factory = ProviderFactory()
    factory.register_builder("a", lambda config: MinimalProvider("a"))
    factory.register_builder("b", lambda config: MinimalProvider("b"))

    factory.clear()

    assert factory.list_builders() == ()


def test_registry_registers_switches_current_unregisters_and_clears() -> None:
    registry = ProviderRegistry()
    first = MinimalProvider("first")
    second = MinimalProvider("second")

    registry.register(first)
    registry.register(second)
    registry.set_current("second")

    assert registry.exists("first") is True
    assert registry.exists("missing") is False
    assert registry.list() == ("first", "second")
    assert registry.get("first") is first
    assert registry.current() is second

    registry.unregister("second")

    assert registry.current() is None
    assert registry.list() == ("first",)

    registry.clear()

    assert registry.list() == ()
    assert registry.current() is None


def test_registry_rejects_duplicate_missing_and_invalid_providers() -> None:
    registry = ProviderRegistry()
    registry.register(MinimalProvider("minimal"))

    with pytest.raises(ProviderAlreadyRegisteredError):
        registry.register(MinimalProvider("minimal"))

    with pytest.raises(ProviderInvalidError):
        registry.register(object())  # type: ignore[arg-type]

    with pytest.raises(ProviderNotFoundError):
        registry.get("missing")

    with pytest.raises(ProviderNotFoundError):
        registry.set_current("missing")

    with pytest.raises(ProviderNotFoundError):
        registry.unregister("missing")


def test_registry_is_safe_for_basic_parallel_registration() -> None:
    registry = ProviderRegistry()

    def register(index: int) -> None:
        registry.register(MinimalProvider(f"provider-{index}"))

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(register, range(20)))

    assert len(registry.list()) == 20
    assert registry.get("provider-19").provider_name() == "provider-19"


def test_official_pocket_builder_creates_adapter_without_starting_runtime() -> None:
    runtime = PocketMarketRuntime()
    factory = ProviderFactory()
    factory.register_builder(PocketProviderBuilder.provider_name, PocketProviderBuilder())

    provider = factory.create("POCKET", {"runtime": runtime})

    assert isinstance(provider, PocketProviderAdapter)
    assert provider.runtime is runtime
    assert provider.get_context().connection_state == "stopped"


def test_fake_pocket_builder_creates_independent_fake_provider() -> None:
    factory = ProviderFactory()
    factory.register_builder(FakePocketProviderBuilder.provider_name, FakePocketProviderBuilder())

    first = factory.create("FAKE_POCKET")
    second = factory.create("FAKE_POCKET")

    assert isinstance(first, FakePocketProviderAdapter)
    assert isinstance(second, FakePocketProviderAdapter)
    assert first is not second
    assert first.get_context() is not second.get_context()


def test_factory_and_registry_work_together_without_auto_starting_provider() -> None:
    factory = ProviderFactory()
    registry = ProviderRegistry()
    factory.register_builder("POCKET", PocketProviderBuilder())

    provider = factory.create("POCKET")
    registry.register(provider)
    registry.set_current("POCKET")

    assert registry.current() is provider
    assert registry.current().get_context().connection_state == "stopped"  # type: ignore[union-attr]
