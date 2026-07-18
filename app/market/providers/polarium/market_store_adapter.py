from __future__ import annotations

from app.market.events.models import NormalizedMarketCandle
from app.market.providers.polarium.models import PolariumMarketCandle
from app.market.store import CandleStore
from app.market.store.types import CandleStoreWriteResult


class PolariumCandleStoreAdapter:
    def __init__(self, candle_store: CandleStore) -> None:
        self._candle_store = candle_store

    @property
    def candle_store(self) -> CandleStore:
        return self._candle_store

    def write(self, candle: PolariumMarketCandle, *, source_event: str) -> CandleStoreWriteResult:
        return self._candle_store.add(_normalize(candle, source_event=source_event))


def _normalize(candle: PolariumMarketCandle, *, source_event: str) -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=candle.active_id,
        symbol=candle.symbol,
        raw_size=candle.raw_size,
        timeframe=None,
        start_timestamp=candle.start_timestamp,
        end_timestamp=candle.end_timestamp,
        open=candle.open,
        close=candle.close,
        low_candidate=candle.low,
        high_candidate=candle.high,
        volume=candle.volume,
        source="polarium",
        source_event=source_event,
        source_verified=True,
        mapping_verified=False,
        mapping_notes=(
            "candles-generated active_id is provider-native.",
            "candles-generated candle sizes are provider-native raw sizes.",
            "min/max are preserved as low/high candidates from Polarium.",
        ),
    )
