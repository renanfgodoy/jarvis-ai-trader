from __future__ import annotations

from app.market.chart.runtime_service import MarketChartRuntimeService
from app.market.pipeline import MarketPipeline
from app.market.runtime_feed import ControlledMarketRuntimeFeed
from app.market.runtime_simulator import ControlledCandleStreamSimulator
from app.market.store import CandleStore


# Process-local runtime state. It is intentionally in-memory and is reset when
# the backend process reloads.
market_candle_store = CandleStore()
market_pipeline = MarketPipeline(candle_store=market_candle_store)
market_chart_runtime_service = MarketChartRuntimeService(market_candle_store)
controlled_market_runtime_feed = ControlledMarketRuntimeFeed(market_pipeline)
controlled_candle_stream_simulator = ControlledCandleStreamSimulator(market_pipeline)
