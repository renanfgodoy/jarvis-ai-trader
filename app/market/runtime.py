from __future__ import annotations

from app.market.chart.bucket_consistency import ChartBucketConsistencyDiagnostic
from app.market.chart.provider_service import ChartProviderService
from app.market.chart.runtime_service import MarketChartRuntimeService
from app.market.browser_bridge import AuthorizedBrowserBridgeRuntime
from app.core.config import settings
from app.market.pipeline import MarketPipeline
from app.market.persistence import CandlePersistenceService, SQLiteCandleRepository
from app.market.providers.iq_option.client import IQOptionReadOnlyClient
from app.market.providers.iq_option.config import load_iq_option_config
from app.market.providers.iq_option.provider import IQOptionMarketDataProvider
from app.market.providers.iq_option.runtime import IQOptionProviderRuntime
from app.market.providers.manager import ProviderManager
from app.market.providers.polarium.asset_switch_diagnostic import AssetSwitchDiagnostic
from app.market.providers.polarium.live_source import PolariumCDPLiveSource, PolariumCDPLiveSourceConfig
from app.market.providers.polarium.readiness import PolariumReadinessConfig
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.runtime_feed import ControlledMarketRuntimeFeed
from app.market.runtime_simulator import ControlledCandleStreamSimulator
from app.market.sanity import CandleSanityGuard
from app.market.store import CandleStore


market_candle_store = CandleStore()
market_candle_sanity_guard = CandleSanityGuard(
    min_timestamp=settings.market_candle_min_timestamp,
    future_tolerance_seconds=settings.market_candle_future_tolerance_seconds,
)
market_candle_persistence = CandlePersistenceService(
    SQLiteCandleRepository(settings.market_persistence_database_path),
    retention_per_series=settings.market_persistence_retention_per_series,
)
market_candle_persistence.restore_into_store(market_candle_store)
market_candle_store.set_write_observer(market_candle_persistence.persist_write)
market_pipeline = MarketPipeline(candle_store=market_candle_store)
chart_bucket_consistency_diagnostic = ChartBucketConsistencyDiagnostic()
market_chart_runtime_service = MarketChartRuntimeService(
    market_candle_store,
    bucket_diagnostic=chart_bucket_consistency_diagnostic,
)
market_provider_manager = ProviderManager.from_settings(settings)
market_provider_manager.initialize()
market_chart_provider_service = ChartProviderService(market_provider_manager)
polarium_asset_switch_diagnostic = AssetSwitchDiagnostic()
authorized_browser_bridge_runtime = AuthorizedBrowserBridgeRuntime(market_pipeline)
controlled_market_runtime_feed = ControlledMarketRuntimeFeed(market_pipeline)
controlled_candle_stream_simulator = ControlledCandleStreamSimulator(market_pipeline)
iq_option_provider_config = load_iq_option_config()
iq_option_market_data_provider = IQOptionMarketDataProvider(
    iq_option_provider_config,
    IQOptionReadOnlyClient(iq_option_provider_config),
)
iq_option_provider_runtime = IQOptionProviderRuntime(iq_option_market_data_provider, market_candle_store, market_candle_sanity_guard)
polarium_market_feed_runtime = PolariumMarketFeedRuntime(
    market_candle_store,
    readiness_config=PolariumReadinessConfig(
        limited_candles=settings.polarium_history_limited_candles,
        ready_candles=settings.polarium_history_ready_candles,
        stale_after_ms=settings.polarium_history_stale_after_ms,
    ),
    asset_switch_diagnostic=polarium_asset_switch_diagnostic,
)
polarium_cdp_live_source = PolariumCDPLiveSource(
    polarium_market_feed_runtime,
    PolariumCDPLiveSourceConfig(
        enabled=settings.polarium_cdp_live_enabled,
        chrome_path=settings.polarium_cdp_chrome_path,
        profile_dir=settings.polarium_cdp_profile_dir,
        trade_url=settings.polarium_trade_url,
        friday_frontend_url=settings.friday_frontend_url,
        cdp_port=settings.polarium_cdp_port,
        programmatic_selection_enabled=settings.polarium_programmatic_selection_enabled,
    ),
    candle_store=market_candle_store,
)
