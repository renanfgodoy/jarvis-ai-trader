from __future__ import annotations

from app.market.chart.bucket_consistency import ChartBucketConsistencyDiagnostic, candle_bounds
from app.market.chart.models import ChartCandle, ChartSeries, ChartSeriesSummary
from app.market.store import CandleStore
from app.market.store.types import CandleSeriesKey


class CandleChartService:
    """Read-only transformer from Candle Store candles to chart candles."""

    def __init__(self, candle_store: CandleStore, bucket_diagnostic: ChartBucketConsistencyDiagnostic | None = None) -> None:
        self._candle_store = candle_store
        self._bucket_diagnostic = bucket_diagnostic

    def get_chart_series(self, active_id: int, raw_size: int, limit: int) -> ChartSeries:
        key = CandleSeriesKey(provider="POLARIUM", active_id=active_id, raw_size=raw_size)
        self._observe(
            "CHART_STORE_KEY_RESOLVED",
            active_id_requested=active_id,
            raw_size_requested=raw_size,
            store_key=key,
        )
        candles = self._candle_store.latest_by_key(key, limit=limit)
        first_timestamp, last_timestamp = candle_bounds(candles)
        self._observe(
            "CHART_BUCKET_FOUND" if candles else "CHART_BUCKET_MISSING",
            active_id_requested=active_id,
            raw_size_requested=raw_size,
            store_key=key,
            bucket_exists=bool(candles),
            bucket_count=len(candles),
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
        )
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

    def _observe(self, event: str, **details: object) -> None:
        if self._bucket_diagnostic is None:
            return
        self._bucket_diagnostic.observe(event, **details)  # type: ignore[arg-type]


def _latest_symbol(candles: tuple) -> str | None:
    for candle in reversed(candles):
        if candle.symbol:
            return candle.symbol
    return None
