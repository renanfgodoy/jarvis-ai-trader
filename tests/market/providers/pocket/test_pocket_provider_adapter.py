from __future__ import annotations

import pytest

from app.market.providers.base import MarketProvider, ProviderCandle, ProviderFactory, ProviderTick
from app.market.providers.pocket.adapter import (
    FakePocketProviderAdapter,
    PocketProviderAdapter,
    build_pocket_provider_adapter,
    pocket_candle_to_provider_candle,
    pocket_context_to_provider_context,
    pocket_tick_to_provider_tick,
)
from app.market.providers.pocket.models import PocketAssetCatalog
from app.market.providers.pocket.runtime import PocketMarketRuntime
from app.market.providers.pocket.session_context import PocketSessionContext
from tools.pocket_parser.history_parser import parse_history_batch
from tools.pocket_parser.models import PocketAssetInfo, PocketNormalizedCandle, PocketRealtimeTick


def test_pocket_provider_adapter_implements_market_provider() -> None:
    adapter = PocketProviderAdapter(PocketMarketRuntime())

    assert isinstance(adapter, MarketProvider)
    assert adapter.provider_name() == "POCKET"


def test_context_conversion_is_sanitized_and_provider_neutral() -> None:
    context = PocketSessionContext(
        connection_state="ONLINE",
        session_state="AUTHORIZED_REPLAY",
        asset="EURUSD_otc",
        display_name="EURUSD OTC",
        market_type="OTC",
        is_otc=True,
        period=300,
        timeframe="M5",
        last_price=1.234,
        history_count=55,
        history_state="READY",
        bootstrap_complete=True,
        last_update=1700000000.0,
        analysis_blocked=False,
        analysis_block_reason="READY",
    )

    provider_context = pocket_context_to_provider_context(context)

    assert provider_context.provider == "POCKET"
    assert provider_context.connection_state == "online"
    assert provider_context.symbol == "EURUSD OTC"
    assert provider_context.period == 300
    assert provider_context.readiness == "READY"
    assert "session_state" in provider_context.metadata


def test_tick_and_candle_conversions() -> None:
    tick = PocketRealtimeTick("EURUSD_otc", 1.2, 1700000001.0, "updateStream", 7, "fixture.har", 1)
    candle = PocketNormalizedCandle(
        provider="POCKET",
        symbol="EURUSD_otc",
        period=60,
        timeframe="M1",
        timestamp=1700000000.0,
        open=1.0,
        high=1.3,
        low=0.9,
        close=1.2,
        volume=10,
        is_closed=True,
        source_event="updateHistoryNewFast",
        source_har="fixture.har",
        session_index=1,
    )

    provider_tick = pocket_tick_to_provider_tick(tick, period=60)
    provider_candle = pocket_candle_to_provider_candle(candle)

    assert provider_tick.symbol == "EURUSD_otc"
    assert provider_tick.sequence == 7
    assert provider_candle.open == 1.0
    assert provider_candle.high == 1.3
    assert provider_candle.low == 0.9
    assert provider_candle.close == 1.2


def test_assets_conversion_uses_runtime_catalog() -> None:
    runtime = PocketMarketRuntime()
    runtime.asset_catalog = PocketAssetCatalog(
        assets=(
            PocketAssetInfo(
                symbol="EURUSD_otc",
                display_name="EUR/USD OTC",
                is_otc=True,
                market_type="OTC",
                is_available=True,
                payout=None,
                supported_periods=(60, 300),
                raw_fields_detected=(),
                unknown_numeric_fields=(),
                unknown_boolean_fields=(),
            ),
        )
    )
    adapter = PocketProviderAdapter(runtime)

    assets = adapter.get_assets()

    assert assets.provider == "POCKET"
    assert assets.assets[0].symbol == "EURUSD_otc"
    assert assets.assets[0].supported_periods == (60, 300)
    assert assets.assets[0].is_open is True


def test_history_and_readiness_are_read_from_existing_runtime_store() -> None:
    runtime = PocketMarketRuntime()
    batch, rejections = parse_history_batch(
        {
            "asset": "EURUSD_otc",
            "period": 60,
            "candles": [
                [1700000000, 1.0, 1.1, 1.2, 0.9, 10],
                [1700000060, 1.1, 1.2, 1.3, 1.0, 11],
            ],
        },
        source_har="fixture.har",
        session_index=1,
        frame_index=1,
    )
    assert batch is not None
    assert rejections == []
    runtime.store.add_historical(batch.candles)
    runtime.readiness.update_history(runtime.store.key("EURUSD_otc", 60), 2)
    adapter = PocketProviderAdapter(runtime)

    history = adapter.get_history("EURUSD_otc", 60, limit=1)
    readiness = adapter.get_readiness("EURUSD_otc", 60)

    assert history.history_count == 2
    assert len(history.candles) == 1
    assert history.candles[0].symbol == "EURUSD_otc"
    assert readiness.history_count == 2
    assert readiness.analysis_blocked is True


def test_health_maps_runtime_metrics_without_exposing_payloads() -> None:
    runtime = PocketMarketRuntime()
    runtime.metrics.events_received = 3
    runtime.metrics.ticks_processed = 2
    runtime.last_error = "SAFE_ERROR"
    adapter = PocketProviderAdapter(runtime)

    health = adapter.health()

    assert health.provider == "POCKET"
    assert health.read_only is True
    assert health.last_error_code == "SAFE_ERROR"
    assert health.metrics["events_received"] == 3
    assert health.metrics["ticks_processed"] == 2


def test_fake_pocket_provider_adapter_supports_test_history_and_ticks() -> None:
    candle = ProviderCandle(
        provider="POCKET",
        symbol="FAKE_otc",
        period=60,
        timestamp=1,
        open=1.0,
        high=1.2,
        low=0.9,
        close=1.1,
        volume=None,
        source="fake",
        is_closed=True,
    )
    tick = ProviderTick(provider="POCKET", symbol="FAKE_otc", period=60, timestamp=2, price=1.1, source="fake")
    adapter = FakePocketProviderAdapter(history={("FAKE_otc", 60): (candle,)}, ticks={("FAKE_otc", 60): (tick,)})

    assert adapter.get_history("FAKE_otc", 60).candles == (candle,)
    assert adapter.get_ticks("FAKE_otc", 60) == (tick,)


def test_builder_is_compatible_with_provider_factory() -> None:
    runtime = PocketMarketRuntime()
    factory = ProviderFactory()
    factory.register("POCKET", build_pocket_provider_adapter)

    adapter = factory.create("POCKET", {"runtime": runtime})

    assert isinstance(adapter, PocketProviderAdapter)
    assert adapter.runtime is runtime


def test_builder_rejects_invalid_runtime_config() -> None:
    with pytest.raises(TypeError):
        build_pocket_provider_adapter({"runtime": object()})
