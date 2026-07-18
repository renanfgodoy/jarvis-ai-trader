from __future__ import annotations

from app.market.analysis.exceptions import StatisticsError
from app.market.analysis.models import MarketStatistics
from app.market.providers.base.models import ProviderCandle, ProviderTick


class MarketStatisticsBuilder:
    def build(self, candles: tuple[ProviderCandle, ...], ticks: tuple[ProviderTick, ...]) -> MarketStatistics:
        timestamps = [item.timestamp for item in candles] + [item.timestamp for item in ticks]
        prices: list[float] = []
        for candle in candles:
            if candle.high < candle.low:
                raise StatisticsError("invalid candle range")
            prices.extend([candle.open, candle.high, candle.low, candle.close])
        prices.extend(tick.price for tick in ticks)

        if not prices:
            return MarketStatistics(
                total_candles=0,
                total_ticks=0,
                first_timestamp=None,
                last_timestamp=None,
                duration=None,
                average_price=None,
                highest_price=None,
                lowest_price=None,
                price_range=None,
            )

        first_timestamp = min(timestamps) if timestamps else None
        last_timestamp = max(timestamps) if timestamps else None
        highest = max(prices)
        lowest = min(prices)
        return MarketStatistics(
            total_candles=len(candles),
            total_ticks=len(ticks),
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
            duration=(last_timestamp - first_timestamp) if first_timestamp is not None and last_timestamp is not None else None,
            average_price=sum(prices) / len(prices),
            highest_price=highest,
            lowest_price=lowest,
            price_range=highest - lowest,
        )
