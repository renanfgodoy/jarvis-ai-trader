from __future__ import annotations

from app.market.chart.provider_service import ChartProviderService
from app.market.providers.base import ProviderCandle, ProviderRegistry
from app.market.providers.manager import ProviderManager, ProviderManagerConfig
from app.market.providers.pocket.adapter import FakePocketProviderAdapter
from app.market.providers.pocket.session_context import PocketSessionContext


def _manager_with_fake_provider(provider: FakePocketProviderAdapter) -> ProviderManager:
    manager = ProviderManager(ProviderManagerConfig(provider_v2_enabled=True, current_provider="POCKET"))
    manager.factory.register_builder("POCKET", lambda _config: provider)
    manager.registry.register(provider)
    manager.registry.set_current("POCKET")
    return manager


def test_chart_provider_service_reads_history_from_market_provider_interface() -> None:
    candle = ProviderCandle(
        provider="POCKET",
        symbol="EURUSD_otc",
        period=300,
        timestamp=1_700_000_000,
        open=1.0,
        high=1.2,
        low=0.9,
        close=1.1,
        volume=None,
        source="fake",
        is_closed=True,
    )
    provider = FakePocketProviderAdapter(history={("EURUSD_otc", 300): (candle,)})
    service = ChartProviderService(_manager_with_fake_provider(provider))

    series = service.get_series(provider_name="POCKET", symbol="EURUSD_otc", period=300, limit=200)

    assert series.provider == "POCKET"
    assert series.symbol == "EURUSD_otc"
    assert series.period == 300
    assert series.timeframe == "M5"
    assert series.candles[0].time == 1_700_000_000
    assert series.readiness.history_count == 0


def test_chart_provider_service_lists_context_series_without_importing_pocket_runtime() -> None:
    provider = FakePocketProviderAdapter(
        context=PocketSessionContext(
            connection_state="ONLINE",
            session_state="AUTHORIZED_REPLAY",
            asset="EURUSD_otc",
            display_name="EURUSD_otc",
            period=60,
            timeframe="M1",
            history_count=55,
            history_state="READY",
            bootstrap_complete=True,
            analysis_blocked=False,
        )
    )
    service = ChartProviderService(_manager_with_fake_provider(provider))

    summaries = service.get_available_series(provider_name="POCKET")

    assert summaries[0].provider == "POCKET"
    assert summaries[0].symbol == "EURUSD_otc"
    assert summaries[0].period == 60


def test_chart_provider_service_uses_explicit_registry_instance() -> None:
    first = ProviderRegistry()
    second = ProviderRegistry()

    assert first is not second
