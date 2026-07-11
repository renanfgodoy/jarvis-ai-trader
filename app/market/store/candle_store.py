from __future__ import annotations

from app.market.events.models import NormalizedMarketCandle
from app.market.store.repository import InMemoryCandleRepository
from app.market.store.types import CandleSeriesKey, CandleStoreWriteResult


class CandleStore:
    """Passive in-memory store for normalized market candles."""

    def __init__(self, max_candles_per_series: int = 500, repository: InMemoryCandleRepository | None = None) -> None:
        if max_candles_per_series <= 0:
            raise ValueError("max_candles_per_series must be greater than zero")
        self.max_candles_per_series = max_candles_per_series
        self._repository = repository or InMemoryCandleRepository()

    def add(self, candle: NormalizedMarketCandle) -> CandleStoreWriteResult:
        key = self._key_for(candle)
        if key is None:
            return CandleStoreWriteResult(
                status="rejected",
                key=None,
                start_timestamp=candle.start_timestamp,
                reason="Candle requires active_id to be stored by active_id.",
            )

        series = list(self._repository.get_series(key))
        existing_index = _find_by_start_timestamp(series, candle.start_timestamp)
        if existing_index is not None:
            if series[existing_index] == candle:
                return CandleStoreWriteResult(
                    status="ignored",
                    key=key,
                    start_timestamp=candle.start_timestamp,
                    reason="Duplicate candle with identical timestamp and payload.",
                )
            series[existing_index] = candle
            self._repository.set_series(key, _trim_to_limit(_sort_series(series), self.max_candles_per_series))
            return CandleStoreWriteResult(
                status="updated",
                key=key,
                start_timestamp=candle.start_timestamp,
                reason="Existing candle with same start timestamp was updated.",
            )

        series.append(candle)
        self._repository.set_series(key, _trim_to_limit(_sort_series(series), self.max_candles_per_series))
        return CandleStoreWriteResult(
            status="added",
            key=key,
            start_timestamp=candle.start_timestamp,
            reason="New candle added to series.",
        )

    def add_many(self, candles: tuple[NormalizedMarketCandle, ...]) -> tuple[CandleStoreWriteResult, ...]:
        return tuple(self.add(candle) for candle in candles)

    def latest(self, active_id: int, raw_size: int, limit: int) -> tuple[NormalizedMarketCandle, ...]:
        if limit <= 0:
            return ()
        series = self._repository.get_series(CandleSeriesKey(active_id=active_id, raw_size=raw_size))
        return tuple(series[-limit:])

    def series(self, active_id: int, raw_size: int) -> tuple[NormalizedMarketCandle, ...]:
        return self._repository.get_series(CandleSeriesKey(active_id=active_id, raw_size=raw_size))

    def series_keys(self) -> tuple[CandleSeriesKey, ...]:
        return self._repository.keys()

    def clear(self) -> None:
        self._repository.clear()

    @staticmethod
    def _key_for(candle: NormalizedMarketCandle) -> CandleSeriesKey | None:
        if candle.active_id is None:
            return None
        return CandleSeriesKey(active_id=candle.active_id, raw_size=candle.raw_size)


def _find_by_start_timestamp(series: list[NormalizedMarketCandle], start_timestamp: int) -> int | None:
    for index, candle in enumerate(series):
        if candle.start_timestamp == start_timestamp:
            return index
    return None


def _sort_series(series: list[NormalizedMarketCandle]) -> tuple[NormalizedMarketCandle, ...]:
    return tuple(sorted(series, key=lambda candle: candle.start_timestamp))


def _trim_to_limit(series: tuple[NormalizedMarketCandle, ...], limit: int) -> tuple[NormalizedMarketCandle, ...]:
    if len(series) <= limit:
        return series
    return series[-limit:]
