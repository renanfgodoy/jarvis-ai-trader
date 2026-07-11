from __future__ import annotations

from app.market.chart.runtime_service import MarketChartRuntimeService
from app.market.pipeline import MarketPipeline
from app.market.store import CandleStore


# Process-local runtime state. It is intentionally in-memory and is reset when
# the backend process reloads.
market_candle_store = CandleStore()
market_pipeline = MarketPipeline(candle_store=market_candle_store)
market_chart_runtime_service = MarketChartRuntimeService(market_candle_store)
