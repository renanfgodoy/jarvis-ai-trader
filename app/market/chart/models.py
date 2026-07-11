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
    active_id: int
    raw_size: int
    candles: tuple[ChartCandle, ...]
