from __future__ import annotations

from collections.abc import Iterable

from app.market.events.models import NormalizedMarketCandle
from app.market.store.types import CandleSeriesKey


class InMemoryCandleRepository:
    """Small in-memory repository scoped to one process.

    This repository intentionally has no filesystem, database, network, or
    connector dependency. It is a storage primitive for future runtime wiring.
    """

    def __init__(self) -> None:
        self._series: dict[CandleSeriesKey, list[NormalizedMarketCandle]] = {}

    def get_series(self, key: CandleSeriesKey) -> tuple[NormalizedMarketCandle, ...]:
        return tuple(self._series.get(key, ()))

    def set_series(self, key: CandleSeriesKey, candles: Iterable[NormalizedMarketCandle]) -> None:
        self._series[key] = list(candles)

    def keys(self) -> tuple[CandleSeriesKey, ...]:
        return tuple(sorted(self._series.keys()))

    def clear(self) -> None:
        self._series.clear()
