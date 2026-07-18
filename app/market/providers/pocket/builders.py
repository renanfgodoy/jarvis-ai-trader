from __future__ import annotations

from typing import Mapping

from app.market.providers.base import MarketProvider, ProviderCandle, ProviderTick
from app.market.providers.pocket.adapter import FakePocketProviderAdapter, PocketProviderAdapter
from app.market.providers.pocket.models import PocketAssetCatalog
from app.market.providers.pocket.runtime import PocketMarketRuntime
from app.market.providers.pocket.session_context import PocketSessionContext


class PocketProviderBuilder:
    provider_name = "POCKET"

    def __call__(self, config: Mapping[str, object]) -> MarketProvider:
        runtime = config.get("runtime")
        if runtime is not None and not isinstance(runtime, PocketMarketRuntime):
            raise TypeError("runtime must be a PocketMarketRuntime instance")
        return PocketProviderAdapter(runtime=runtime)


class FakePocketProviderBuilder:
    provider_name = "FAKE_POCKET"

    def __call__(self, config: Mapping[str, object]) -> MarketProvider:
        context = config.get("context")
        catalog = config.get("catalog")
        history = config.get("history")
        ticks = config.get("ticks")
        if context is not None and not isinstance(context, PocketSessionContext):
            raise TypeError("context must be a PocketSessionContext instance")
        if catalog is not None and not isinstance(catalog, PocketAssetCatalog):
            raise TypeError("catalog must be a PocketAssetCatalog instance")
        return FakePocketProviderAdapter(
            context=context,
            catalog=catalog,
            history=history if _is_history_map(history) else None,
            ticks=ticks if _is_tick_map(ticks) else None,
        )


def _is_history_map(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, Mapping):
        raise TypeError("history must be a mapping")
    for key, candles in value.items():
        _validate_key(key, "history")
        if not isinstance(candles, tuple) or not all(isinstance(candle, ProviderCandle) for candle in candles):
            raise TypeError("history values must be tuples of ProviderCandle")
    return True


def _is_tick_map(value: object) -> bool:
    if value is None:
        return True
    if not isinstance(value, Mapping):
        raise TypeError("ticks must be a mapping")
    for key, ticks in value.items():
        _validate_key(key, "ticks")
        if not isinstance(ticks, tuple) or not all(isinstance(tick, ProviderTick) for tick in ticks):
            raise TypeError("ticks values must be tuples of ProviderTick")
    return True


def _validate_key(value: object, label: str) -> None:
    if not isinstance(value, tuple) or len(value) != 2 or not isinstance(value[0], str) or not isinstance(value[1], int):
        raise TypeError(f"{label} keys must be (symbol, period) tuples")
