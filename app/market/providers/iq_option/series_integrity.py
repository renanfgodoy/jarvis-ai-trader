from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from statistics import median

from app.market.events.models import NormalizedMarketCandle
from app.market.store import CandleStore
from app.market.store.types import CandleSeriesKey

PROVIDER_NAME = "IQ_OPTION"


@dataclass(frozen=True)
class IQOptionSeriesIntegrityReport:
    provider: str
    symbol: str
    raw_size: int
    count: int
    first_timestamp: int | None
    last_timestamp: int | None
    distinct_timestamps: int
    duplicate_timestamps: int
    timestamps_out_of_order: int
    price_min: float | None
    price_max: float | None
    largest_range: float | None
    largest_consecutive_gap: float | None
    distinct_providers: tuple[str, ...]
    distinct_symbols: tuple[str, ...]
    distinct_raw_sizes: tuple[int, ...]
    integrity_status: str
    reason_codes: tuple[str, ...]

    def sanitized(self) -> dict:
        return {
            "provider": self.provider,
            "symbol": self.symbol,
            "raw_size": self.raw_size,
            "count": self.count,
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
            "distinct_timestamps": self.distinct_timestamps,
            "duplicate_timestamps": self.duplicate_timestamps,
            "timestamps_out_of_order": self.timestamps_out_of_order,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "largest_range": self.largest_range,
            "largest_consecutive_gap": self.largest_consecutive_gap,
            "distinct_providers": list(self.distinct_providers),
            "distinct_symbols": list(self.distinct_symbols),
            "distinct_raw_sizes": list(self.distinct_raw_sizes),
            "integrity_status": self.integrity_status,
            "reason_codes": list(self.reason_codes),
        }


class IQOptionSeriesIntegrityAnalyzer:
    """Read-only integrity diagnostics for a provider-native IQ Option series."""

    def __init__(self, candle_store: CandleStore) -> None:
        self._candle_store = candle_store

    def analyze(self, *, symbol: str, raw_size: int) -> IQOptionSeriesIntegrityReport:
        key = CandleSeriesKey(provider=PROVIDER_NAME, symbol=symbol, active_id=None, raw_size=raw_size)
        candles = self._candle_store.series_by_key(key)
        return analyze_iq_option_candles(symbol=symbol, raw_size=raw_size, candles=candles)


def analyze_iq_option_candles(
    *, symbol: str, raw_size: int, candles: tuple[NormalizedMarketCandle, ...]
) -> IQOptionSeriesIntegrityReport:
    ordered = tuple(sorted(candles, key=lambda candle: candle.start_timestamp))
    timestamps = [candle.start_timestamp for candle in ordered]
    distinct_timestamps = len(set(timestamps))
    duplicate_timestamps = len(timestamps) - distinct_timestamps
    timestamps_out_of_order = sum(1 for previous, current in zip(candles, candles[1:]) if current.start_timestamp < previous.start_timestamp)
    distinct_providers = tuple(sorted({_provider_for(candle) for candle in ordered}))
    distinct_symbols = tuple(sorted({candle.symbol for candle in ordered if candle.symbol}))
    distinct_raw_sizes = tuple(sorted({candle.raw_size for candle in ordered}))
    prices = [price for candle in ordered for price in (candle.open, candle.close, candle.low_candidate, candle.high_candidate) if isfinite(price)]
    ranges = [abs(candle.high_candidate - candle.low_candidate) for candle in ordered if isfinite(candle.high_candidate) and isfinite(candle.low_candidate)]
    close_gaps = [abs(current.close - previous.close) for previous, current in zip(ordered, ordered[1:]) if isfinite(current.close) and isfinite(previous.close)]
    reason_codes: list[str] = []

    if duplicate_timestamps:
        reason_codes.append("DUPLICATE_TIMESTAMP")
    if timestamps_out_of_order:
        reason_codes.append("OUT_OF_ORDER_TIMESTAMP")
    if distinct_providers and distinct_providers != (PROVIDER_NAME,):
        reason_codes.append("PROVIDER_MISMATCH")
    if distinct_symbols and distinct_symbols != (symbol,):
        reason_codes.append("SYMBOL_MISMATCH")
    if distinct_raw_sizes and distinct_raw_sizes != (raw_size,):
        reason_codes.append("TIMEFRAME_MISMATCH")
    if _has_price_cluster_split(ordered):
        reason_codes.append("PRICE_CLUSTER_SPLIT")
    if _has_extreme_consecutive_gap(ordered):
        reason_codes.append("EXTREME_CONSECUTIVE_GAP")

    return IQOptionSeriesIntegrityReport(
        provider=PROVIDER_NAME,
        symbol=symbol,
        raw_size=raw_size,
        count=len(ordered),
        first_timestamp=timestamps[0] if timestamps else None,
        last_timestamp=timestamps[-1] if timestamps else None,
        distinct_timestamps=distinct_timestamps,
        duplicate_timestamps=duplicate_timestamps,
        timestamps_out_of_order=timestamps_out_of_order,
        price_min=min(prices) if prices else None,
        price_max=max(prices) if prices else None,
        largest_range=max(ranges) if ranges else None,
        largest_consecutive_gap=max(close_gaps) if close_gaps else None,
        distinct_providers=distinct_providers,
        distinct_symbols=distinct_symbols,
        distinct_raw_sizes=distinct_raw_sizes,
        integrity_status="FAIL" if reason_codes else "OK",
        reason_codes=tuple(reason_codes),
    )


def _provider_for(candle: NormalizedMarketCandle) -> str:
    return PROVIDER_NAME if candle.source == "iq_option" else "POLARIUM"


def _has_price_cluster_split(candles: tuple[NormalizedMarketCandle, ...]) -> bool:
    closes = [candle.close for candle in candles if isfinite(candle.close)]
    if len(closes) < 12:
        return False
    midpoint = median(closes)
    if midpoint <= 0:
        return False
    low_cluster = [close for close in closes if close < midpoint * 0.98]
    high_cluster = [close for close in closes if close > midpoint * 1.02]
    return len(low_cluster) >= 3 and len(high_cluster) >= 3


def _has_extreme_consecutive_gap(candles: tuple[NormalizedMarketCandle, ...]) -> bool:
    if len(candles) < 2:
        return False
    ranges = [abs(candle.high_candidate - candle.low_candidate) for candle in candles if isfinite(candle.high_candidate) and isfinite(candle.low_candidate)]
    baseline_range = median(ranges) if ranges else 0
    for previous, current in zip(candles, candles[1:]):
        if not isfinite(previous.close) or not isfinite(current.close):
            continue
        gap = abs(current.close - previous.close)
        relative_threshold = max(abs(previous.close), abs(current.close)) * 0.02
        range_threshold = baseline_range * 20 if baseline_range > 0 else 0
        if gap > max(relative_threshold, range_threshold):
            return True
    return False
