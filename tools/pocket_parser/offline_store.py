from __future__ import annotations

from dataclasses import asdict

from tools.pocket_parser.models import PocketNormalizedCandle


class PocketOfflineStore:
    def __init__(self) -> None:
        self._buckets: dict[str, dict[float, PocketNormalizedCandle]] = {}

    @staticmethod
    def key(asset: str, period: int) -> str:
        return f"POCKET:{asset}:{period}"

    def add_candles(self, candles: list[PocketNormalizedCandle] | tuple[PocketNormalizedCandle, ...]) -> None:
        for candle in candles:
            bucket = self._buckets.setdefault(self.key(candle.symbol, candle.period), {})
            bucket[candle.timestamp] = candle

    def list_buckets(self) -> tuple[str, ...]:
        return tuple(sorted(self._buckets))

    def count(self, key: str) -> int:
        return len(self._buckets.get(key, {}))

    def candles(self, key: str) -> tuple[PocketNormalizedCandle, ...]:
        return tuple(sorted(self._buckets.get(key, {}).values(), key=lambda item: item.timestamp))

    def first(self, key: str) -> PocketNormalizedCandle | None:
        items = self.candles(key)
        return items[0] if items else None

    def last(self, key: str) -> PocketNormalizedCandle | None:
        items = self.candles(key)
        return items[-1] if items else None

    def last_n(self, key: str, limit: int) -> tuple[PocketNormalizedCandle, ...]:
        return self.candles(key)[-limit:]

    def report(self) -> dict:
        buckets = {}
        for key in self.list_buckets():
            first = self.first(key)
            last = self.last(key)
            buckets[key] = {
                "count": self.count(key),
                "first_timestamp": first.timestamp if first else None,
                "last_timestamp": last.timestamp if last else None,
                "first": asdict(first) if first else None,
                "last": asdict(last) if last else None,
            }
        return {"bucket_count": len(buckets), "buckets": buckets}

