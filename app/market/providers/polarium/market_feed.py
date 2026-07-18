from __future__ import annotations

from app.market.providers.iq_option.feed_quality import FeedQualityTracker
from app.market.providers.models import ProviderCandle
from app.market.providers.polarium.market_router import PolariumMarketRouter
from app.market.providers.polarium.models import POLARIUM_MARKET_TYPE, POLARIUM_PROVIDER, PolariumMarketEvent, PolariumMarketFeedResult
from app.market.store.types import CandleStoreWriteResult


class PolariumMarketFeed:
    def __init__(self, router: PolariumMarketRouter, feed_quality: FeedQualityTracker | None = None) -> None:
        self._router = router
        self._feed_quality = feed_quality or FeedQualityTracker()

    @property
    def feed_quality(self) -> FeedQualityTracker:
        return self._feed_quality

    def consume(self, event: PolariumMarketEvent, *, now_ms: int) -> PolariumMarketFeedResult:
        store_results = self._router.route(event)
        quality_symbol = event.symbol or str(event.active_id)
        for candle in event.candles:
            self._feed_quality.start(market_type=POLARIUM_MARKET_TYPE, symbol=quality_symbol, raw_size=candle.raw_size, now_ms=now_ms)
            self._feed_quality.record_event(
                market_type=POLARIUM_MARKET_TYPE,
                symbol=quality_symbol,
                raw_size=candle.raw_size,
                source_mode="NEAR_REALTIME",
                candle=ProviderCandle(
                    provider=POLARIUM_PROVIDER,
                    market_type=POLARIUM_MARKET_TYPE,
                    symbol=quality_symbol,
                    raw_size=candle.raw_size,
                    start_timestamp=candle.start_timestamp,
                    end_timestamp=candle.end_timestamp,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume,
                    is_otc=True,
                    source_verified=True,
                ),
                now_ms=now_ms,
            )
        return PolariumMarketFeedResult(
            status="processed",
            event_name=event.event_name,
            active_id=event.active_id,
            processed=len(event.candles),
            stored=_count(store_results, "added"),
            updated=_count(store_results, "updated"),
            ignored=_count(store_results, "ignored"),
            store_results=store_results,
        )


def _count(results: tuple[CandleStoreWriteResult, ...], status: str) -> int:
    return sum(1 for result in results if result.status == status)
