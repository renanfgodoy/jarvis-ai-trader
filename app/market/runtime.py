from __future__ import annotations

from app.market.chart.runtime_service import MarketChartRuntimeService
from app.market.browser_bridge import AuthorizedBrowserBridgeRuntime
from app.core.config import settings
from app.market.pipeline import MarketPipeline
from app.market.persistence import CandlePersistenceService, SQLiteCandleRepository
from app.market.providers.iq_option.client import IQOptionReadOnlyClient
from app.market.providers.iq_option.config import load_iq_option_config
from app.market.providers.iq_option.provider import IQOptionMarketDataProvider
from app.market.providers.iq_option.runtime import IQOptionProviderRuntime
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
market_chart_runtime_service = MarketChartRuntimeService(market_candle_store)
authorized_browser_bridge_runtime = AuthorizedBrowserBridgeRuntime(market_pipeline)
controlled_market_runtime_feed = ControlledMarketRuntimeFeed(market_pipeline)
controlled_candle_stream_simulator = ControlledCandleStreamSimulator(market_pipeline)
iq_option_provider_config = load_iq_option_config()
iq_option_market_data_provider = IQOptionMarketDataProvider(
    iq_option_provider_config,
    IQOptionReadOnlyClient(iq_option_provider_config),
)
iq_option_provider_runtime = IQOptionProviderRuntime(iq_option_market_data_provider, market_candle_store, market_candle_sanity_guard)
