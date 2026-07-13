from __future__ import annotations

from app.market.chart.models import ChartSeries, ChartSeriesSummary
from app.market.chart.service import CandleChartService
from app.market.store import CandleStore
from app.market.store.types import CandleSeriesKey


class MarketChartRuntimeService:
    """Read-only runtime facade over an existing Candle Store instance."""

    def __init__(self, candle_store: CandleStore) -> None:
        self._chart_service = CandleChartService(candle_store)

    def get_series(self, active_id: int, raw_size: int, limit: int) -> ChartSeries:
        return self._chart_service.get_chart_series(active_id=active_id, raw_size=raw_size, limit=limit)

    def get_provider_series(self, provider: str, symbol: str, raw_size: int, limit: int) -> ChartSeries:
        key = CandleSeriesKey(provider=provider, symbol=symbol, active_id=None, raw_size=raw_size)
        return self._chart_service.get_chart_series_by_key(key=key, limit=limit)

    def get_available_series(self) -> tuple[ChartSeriesSummary, ...]:
        return self._chart_service.get_available_series()
