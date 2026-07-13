from __future__ import annotations

from app.market.chart.models import ChartCandle, ChartSeries, ChartSeriesSummary
from app.market.store import CandleStore
from app.market.store.types import CandleSeriesKey


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
        return ChartSeries(provider="POLARIUM", active_id=active_id, symbol=_latest_symbol(candles), raw_size=raw_size, candles=chart_candles)

    def get_chart_series_by_key(self, key: CandleSeriesKey, limit: int) -> ChartSeries:
        candles = self._candle_store.latest_by_key(key, limit=limit)
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
        return ChartSeries(provider=key.provider, active_id=key.active_id, symbol=_latest_symbol(candles) or key.symbol, raw_size=key.raw_size, candles=chart_candles)

    def get_available_series(self) -> tuple[ChartSeriesSummary, ...]:
        summaries: list[ChartSeriesSummary] = []
        for key in self._candle_store.series_keys():
            candles = self._candle_store.series_by_key(key)
            latest = candles[-1] if candles else None
            summaries.append(
                ChartSeriesSummary(
                    provider=key.provider,
                    active_id=key.active_id,
                    symbol=_latest_symbol(candles),
                    raw_size=key.raw_size,
                    count=len(candles),
                    latest_time=latest.start_timestamp if latest else None,
                )
            )
        return tuple(summaries)


def _latest_symbol(candles: tuple) -> str | None:
    for candle in reversed(candles):
        if candle.symbol:
            return candle.symbol
    return None
