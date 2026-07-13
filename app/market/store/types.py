from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CandleStoreWriteStatus = Literal["added", "updated", "ignored", "rejected"]


@dataclass(frozen=True, order=True)
class CandleSeriesKey:
    raw_size: int
    provider: str = "POLARIUM"
    symbol: str | None = None
    active_id: int | None = None


@dataclass(frozen=True)
class CandleStoreWriteResult:
    status: CandleStoreWriteStatus
    key: CandleSeriesKey | None
    start_timestamp: int | None
    reason: str
