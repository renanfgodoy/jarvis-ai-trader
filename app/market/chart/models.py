from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChartCandle:
    time: int
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class ChartSeries:
    provider: str
    active_id: int | None
    symbol: str | None
    raw_size: int
    candles: tuple[ChartCandle, ...]


@dataclass(frozen=True)
class ChartSeriesSummary:
    provider: str
    active_id: int | None
    symbol: str | None
    raw_size: int
    count: int
    latest_time: int | None
