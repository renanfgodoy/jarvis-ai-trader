from __future__ import annotations

from dataclasses import dataclass

from app.market.events.models import MarketEventParseError, MarketEventRouteResult
from app.market.store.types import CandleStoreWriteResult


@dataclass(frozen=True)
class PipelineResult:
    success: bool
    processed: int
    stored: int
    ignored: int
    updated: int
    unsupported: int
    errors: tuple[MarketEventParseError, ...]
    store_results: tuple[CandleStoreWriteResult, ...]
    route_result: MarketEventRouteResult

    @property
    def rejected(self) -> int:
        return sum(1 for result in self.store_results if result.status == "rejected")
