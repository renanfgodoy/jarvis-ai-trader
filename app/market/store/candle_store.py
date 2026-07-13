from __future__ import annotations

from app.market.events.models import NormalizedMarketCandle
from app.market.store.repository import InMemoryCandleRepository
from collections.abc import Callable

from app.market.store.types import CandleSeriesKey, CandleStoreWriteResult

CandleStoreWriteObserver = Callable[[NormalizedMarketCandle, CandleStoreWriteResult], None]


class CandleStore:
    """Passive in-memory store for normalized market candles."""

    def __init__(
        self,
        max_candles_per_series: int = 500,
        repository: InMemoryCandleRepository | None = None,
        write_observer: CandleStoreWriteObserver | None = None,
    ) -> None:
        if max_candles_per_series <= 0:
            raise ValueError("max_candles_per_series must be greater than zero")
        self.max_candles_per_series = max_candles_per_series
        self._repository = repository or InMemoryCandleRepository()
        self._write_observer = write_observer

    def set_write_observer(self, write_observer: CandleStoreWriteObserver | None) -> None:
        self._write_observer = write_observer

    @property
    def write_observer(self) -> CandleStoreWriteObserver | None:
        return self._write_observer

    def add(self, candle: NormalizedMarketCandle) -> CandleStoreWriteResult:
        key = self._key_for(candle)
        if key is None:
            return CandleStoreWriteResult(
                status="rejected",
                key=None,
                start_timestamp=candle.start_timestamp,
                reason="Candle requires provider-native active_id or symbol to be stored.",
            )

        series = list(self._repository.get_series(key))
        existing_index = _find_by_start_timestamp(series, candle.start_timestamp)
        if existing_index is not None:
            if series[existing_index] == candle:
                result = CandleStoreWriteResult(
                    status="ignored",
                    key=key,
                    start_timestamp=candle.start_timestamp,
                    reason="Duplicate candle with identical timestamp and payload.",
                )
                self._notify_write_observer(candle, result)
                return result
            series[existing_index] = candle
            self._repository.set_series(key, _trim_to_limit(_sort_series(series), self.max_candles_per_series))
            result = CandleStoreWriteResult(
                status="updated",
                key=key,
                start_timestamp=candle.start_timestamp,
                reason="Existing candle with same start timestamp was updated.",
            )
            self._notify_write_observer(candle, result)
            return result

        series.append(candle)
        self._repository.set_series(key, _trim_to_limit(_sort_series(series), self.max_candles_per_series))
        result = CandleStoreWriteResult(
            status="added",
            key=key,
            start_timestamp=candle.start_timestamp,
            reason="New candle added to series.",
        )
        self._notify_write_observer(candle, result)
        return result

    def add_many(self, candles: tuple[NormalizedMarketCandle, ...]) -> tuple[CandleStoreWriteResult, ...]:
        return tuple(self.add(candle) for candle in candles)

    def latest(self, active_id: int, raw_size: int, limit: int) -> tuple[NormalizedMarketCandle, ...]:
        if limit <= 0:
            return ()
        series = self._repository.get_series(CandleSeriesKey(provider="POLARIUM", active_id=active_id, raw_size=raw_size))
        return tuple(series[-limit:])

    def series(self, active_id: int, raw_size: int) -> tuple[NormalizedMarketCandle, ...]:
        return self._repository.get_series(CandleSeriesKey(provider="POLARIUM", active_id=active_id, raw_size=raw_size))

    def latest_by_key(self, key: CandleSeriesKey, limit: int) -> tuple[NormalizedMarketCandle, ...]:
        if limit <= 0:
            return ()
        series = self._repository.get_series(key)
        return tuple(series[-limit:])

    def series_by_key(self, key: CandleSeriesKey) -> tuple[NormalizedMarketCandle, ...]:
        return self._repository.get_series(key)

    def series_keys(self) -> tuple[CandleSeriesKey, ...]:
        return self._repository.keys()

    def clear(self) -> None:
        self._repository.clear()

    def _notify_write_observer(self, candle: NormalizedMarketCandle, result: CandleStoreWriteResult) -> None:
        if self._write_observer is None:
            return
        self._write_observer(candle, result)

    @staticmethod
    def _key_for(candle: NormalizedMarketCandle) -> CandleSeriesKey | None:
        provider = _provider_for(candle)
        if candle.active_id is not None:
            return CandleSeriesKey(provider=provider, active_id=candle.active_id, symbol=None, raw_size=candle.raw_size)
        if candle.symbol:
            return CandleSeriesKey(provider=provider, symbol=candle.symbol, active_id=None, raw_size=candle.raw_size)
        return None


def _provider_for(candle: NormalizedMarketCandle) -> str:
    if candle.source == "iq_option":
        return "IQ_OPTION"
    return "POLARIUM"


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
