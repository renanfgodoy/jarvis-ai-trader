from __future__ import annotations

from app.market.chart.models import ChartCandle, ChartSeries
from app.market.store import CandleStore


class CandleChartService:
    """Read-only transformer from Candle Store candles to chart candles."""

    def __init__(self, candle_store: CandleStore) -> None:
        self._candle_store = candle_store

    def get_chart_series(self, active_id: int, raw_size: int, limit: int) -> ChartSeries:
        candles = self._candle_store.latest(active_id=active_id, raw_size=raw_size, limit=limit)
        chart_candles = tuple(
            ChartCandle(
                time=candle.start_timestamp,
                open=candle.open,
                high=candle.high_candidate,
                low=candle.low_candidate,
                close=candle.close,
            )
            for candle in candles
        )
        return ChartSeries(active_id=active_id, raw_size=raw_size, candles=chart_candles)
