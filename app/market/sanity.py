from __future__ import annotations

from dataclasses import dataclass
import math
import time

from app.market.events.models import NormalizedMarketCandle


@dataclass(frozen=True)
class CandleSanityResult:
    accepted: bool
    error_code: str | None = None


class CandleSanityGuard:
    def __init__(self, *, min_timestamp: int = 1_500_000_000, future_tolerance_seconds: int = 300) -> None:
        self._min_timestamp = min_timestamp
        self._future_tolerance_seconds = future_tolerance_seconds

    def validate(self, candle: NormalizedMarketCandle, *, now_timestamp: int | None = None) -> CandleSanityResult:
        now = int(time.time()) if now_timestamp is None else now_timestamp
        if candle.start_timestamp < self._min_timestamp:
            return CandleSanityResult(False, "TIMESTAMP_BELOW_MINIMUM")
        if candle.start_timestamp > now + self._future_tolerance_seconds:
            return CandleSanityResult(False, "TIMESTAMP_IN_FUTURE")

        prices = (candle.open, candle.high_candidate, candle.low_candidate, candle.close)
        if any(math.isnan(value) for value in prices):
            return CandleSanityResult(False, "NAN_VALUE")
        if any(math.isinf(value) for value in prices):
            return CandleSanityResult(False, "INFINITE_VALUE")
        if any(value <= 0 for value in prices):
            return CandleSanityResult(False, "NON_POSITIVE_PRICE")
        if candle.high_candidate < candle.low_candidate:
            return CandleSanityResult(False, "HIGH_BELOW_LOW")
        if not candle.low_candidate <= candle.open <= candle.high_candidate:
            return CandleSanityResult(False, "OPEN_OUT_OF_RANGE")
        if not candle.low_candidate <= candle.close <= candle.high_candidate:
            return CandleSanityResult(False, "CLOSE_OUT_OF_RANGE")

        return CandleSanityResult(True)
