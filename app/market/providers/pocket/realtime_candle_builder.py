from __future__ import annotations

from dataclasses import replace

from app.market.providers.pocket.candle_store_adapter import PocketStoredCandle
from tools.pocket_parser.models import PocketRealtimeTick, SUPPORTED_PERIODS


class PocketRealtimeCandleBuilder:
    def __init__(self) -> None:
        self._open_candles: dict[tuple[str, int, float], PocketStoredCandle] = {}

    def update(self, tick: PocketRealtimeTick, period: int) -> tuple[PocketStoredCandle, str]:
        bucket_timestamp = tick.timestamp - (tick.timestamp % period)
        key = (tick.asset, period, bucket_timestamp)
        current = self._open_candles.get(key)
        if current is None:
            candle = PocketStoredCandle(
                provider="POCKET",
                asset=tick.asset,
                period=period,
                timeframe=SUPPORTED_PERIODS[period],
                timestamp=bucket_timestamp,
                open=tick.price,
                high=tick.price,
                low=tick.price,
                close=tick.price,
                volume=1,
                source_event="updateStream",
                is_realtime=True,
            )
            self._open_candles[key] = candle
            return candle, "created"
        volume = (current.volume or 0) + 1
        candle = replace(
            current,
            high=max(current.high, tick.price),
            low=min(current.low, tick.price),
            close=tick.price,
            volume=volume,
        )
        self._open_candles[key] = candle
        return candle, "updated"

    def clear(self) -> None:
        self._open_candles.clear()

