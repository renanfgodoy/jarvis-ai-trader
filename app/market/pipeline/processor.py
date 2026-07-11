from __future__ import annotations

from typing import Any

from app.market.events.router import route_market_event
from app.market.pipeline.models import PipelineResult
from app.market.store import CandleStore


class MarketPipelineProcessor:
    """Passive processor that links Market Event Engine to Candle Store."""

    def __init__(self, candle_store: CandleStore | None = None) -> None:
        self.candle_store = candle_store or CandleStore()

    def process(self, message: dict[str, Any]) -> PipelineResult:
        route_result = route_market_event(message)

        if route_result.status != "parsed":
            unsupported = 1 if route_result.status == "unsupported" else 0
            return PipelineResult(
                success=False,
                processed=0,
                stored=0,
                ignored=0,
                updated=0,
                unsupported=unsupported,
                errors=route_result.errors,
                store_results=(),
                route_result=route_result,
            )

        store_results = self.candle_store.add_many(route_result.candles)
        stored = _count_store_status(store_results, "added")
        ignored = _count_store_status(store_results, "ignored")
        updated = _count_store_status(store_results, "updated")
        rejected = _count_store_status(store_results, "rejected")
        success = rejected == 0 and not route_result.errors

        return PipelineResult(
            success=success,
            processed=len(route_result.candles),
            stored=stored,
            ignored=ignored,
            updated=updated,
            unsupported=0,
            errors=route_result.errors,
            store_results=store_results,
            route_result=route_result,
        )


def _count_store_status(store_results: tuple, status: str) -> int:
    return sum(1 for result in store_results if result.status == status)
