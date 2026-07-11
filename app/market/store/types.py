from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CandleStoreWriteStatus = Literal["added", "updated", "ignored", "rejected"]


@dataclass(frozen=True, order=True)
class CandleSeriesKey:
    active_id: int
    raw_size: int


@dataclass(frozen=True)
class CandleStoreWriteResult:
    status: CandleStoreWriteStatus
    key: CandleSeriesKey | None
    start_timestamp: int | None
    reason: str
