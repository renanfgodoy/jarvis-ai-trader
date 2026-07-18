from __future__ import annotations

from app.market.providers.polarium.market_store_adapter import PolariumCandleStoreAdapter
from app.market.providers.polarium.models import PolariumMarketEvent
from app.market.store.types import CandleStoreWriteResult


class PolariumMarketRouter:
    """Routes parsed Polarium market events by active_id and raw_size."""

    def __init__(self, store_adapter: PolariumCandleStoreAdapter) -> None:
        self._store_adapter = store_adapter

    def route(self, event: PolariumMarketEvent) -> tuple[CandleStoreWriteResult, ...]:
        return tuple(self._store_adapter.write(candle, source_event=event.event_name) for candle in event.candles)
