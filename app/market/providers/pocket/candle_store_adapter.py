from __future__ import annotations

from dataclasses import dataclass

from tools.pocket_parser.models import PocketNormalizedCandle


@dataclass(frozen=True)
class PocketStoredCandle:
    provider: str
    asset: str
    period: int
    timeframe: str
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    source_event: str
    is_realtime: bool = False


class PocketCandleStoreAdapter:
    def __init__(self) -> None:
        self._series: dict[str, dict[float, PocketStoredCandle]] = {}

    @staticmethod
    def key(asset: str, period: int) -> str:
        return f"POCKET:{asset}:{period}"

    def add_historical(self, candles: tuple[PocketNormalizedCandle, ...]) -> int:
        written = 0
        for candle in candles:
            stored = PocketStoredCandle(
                provider="POCKET",
                asset=candle.symbol,
                period=candle.period,
                timeframe=candle.timeframe,
                timestamp=candle.timestamp,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                source_event=candle.source_event,
                is_realtime=False,
            )
            bucket = self._series.setdefault(self.key(stored.asset, stored.period), {})
            if bucket.get(stored.timestamp) != stored:
                written += 1
            bucket[stored.timestamp] = stored
        return written

    def add_realtime(self, candle: PocketStoredCandle) -> str:
        bucket = self._series.setdefault(self.key(candle.asset, candle.period), {})
        status = "created" if candle.timestamp not in bucket else "updated"
        bucket[candle.timestamp] = candle
        return status

    def list_buckets(self) -> tuple[str, ...]:
        return tuple(sorted(self._series))

    def candles(self, key: str) -> tuple[PocketStoredCandle, ...]:
        return tuple(sorted(self._series.get(key, {}).values(), key=lambda item: item.timestamp))

    def count(self, key: str) -> int:
        return len(self._series.get(key, {}))

    def last(self, key: str) -> PocketStoredCandle | None:
        items = self.candles(key)
        return items[-1] if items else None

    def clear(self) -> None:
        self._series.clear()

