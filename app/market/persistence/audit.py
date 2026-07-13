from __future__ import annotations

from dataclasses import dataclass
import math
import time

from app.market.events.models import NormalizedMarketCandle
from app.market.store import CandleStore

FUTURE_TIMESTAMP_TOLERANCE_SECONDS = 60
EXTREME_PRICE_DISTANCE_RATIO = 0.5
EXTREME_RANGE_MULTIPLIER = 10


@dataclass(frozen=True)
class InvalidCandleRecord:
    active_id: int
    raw_size: int
    timestamp: int
    reason: str

    def sanitized(self) -> dict:
        return {
            "active_id": self.active_id,
            "raw_size": self.raw_size,
            "timestamp": self.timestamp,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CandleSeriesAudit:
    active_id: int
    raw_size: int
    count: int
    valid: int
    invalid: int
    first_timestamp: int | None
    last_timestamp: int | None
    price_min: float | None
    price_max: float | None
    low_min: float | None
    high_max: float | None
    open_min: float | None
    open_max: float | None
    close_min: float | None
    close_max: float | None

    def sanitized(self) -> dict:
        return {
            "active_id": self.active_id,
            "raw_size": self.raw_size,
            "count": self.count,
            "valid": self.valid,
            "invalid": self.invalid,
            "first_timestamp": self.first_timestamp,
            "last_timestamp": self.last_timestamp,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "low_min": self.low_min,
            "high_max": self.high_max,
            "open_min": self.open_min,
            "open_max": self.open_max,
            "close_min": self.close_min,
            "close_max": self.close_max,
        }


@dataclass(frozen=True)
class CandleIntegrityAudit:
    series_count: int
    total_candles: int
    valid_candles: int
    invalid_candles: int
    largest_price: float | None
    smallest_price: float | None
    largest_range: float | None
    smallest_range: float | None
    series: tuple[CandleSeriesAudit, ...]
    invalid_records: tuple[InvalidCandleRecord, ...]

    def sanitized(self) -> dict:
        return {
            "series_count": self.series_count,
            "total_candles": self.total_candles,
            "valid_candles": self.valid_candles,
            "invalid_candles": self.invalid_candles,
            "largest_price": self.largest_price,
            "smallest_price": self.smallest_price,
            "largest_range": self.largest_range,
            "smallest_range": self.smallest_range,
            "series": [item.sanitized() for item in self.series],
            "invalid_candle_records": [item.sanitized() for item in self.invalid_records],
        }


class CandleIntegrityAuditor:
    """Read-only integrity checks for normalized candles already in the store."""

    def __init__(self, candle_store: CandleStore) -> None:
        self._candle_store = candle_store

    def audit(self, *, now_timestamp: int | None = None) -> CandleIntegrityAudit:
        now = now_timestamp if now_timestamp is not None else int(time.time())
        series_audits: list[CandleSeriesAudit] = []
        invalid_records: list[InvalidCandleRecord] = []
        total_candles = 0
        valid_candles = 0
        invalid_candles = 0
        all_prices: list[float] = []
        all_ranges: list[float] = []

        for key in self._candle_store.series_keys():
            candles = self._candle_store.series(key.active_id, key.raw_size)
            series_result = self._audit_series(key.active_id, key.raw_size, candles, now_timestamp=now)
            series_audits.append(series_result.series)
            invalid_records.extend(series_result.invalid_records)
            total_candles += series_result.series.count
            valid_candles += series_result.series.valid
            invalid_candles += series_result.series.invalid
            all_prices.extend(series_result.prices)
            all_ranges.extend(series_result.ranges)

        return CandleIntegrityAudit(
            series_count=len(series_audits),
            total_candles=total_candles,
            valid_candles=valid_candles,
            invalid_candles=invalid_candles,
            largest_price=max(all_prices) if all_prices else None,
            smallest_price=min(all_prices) if all_prices else None,
            largest_range=max(all_ranges) if all_ranges else None,
            smallest_range=min(all_ranges) if all_ranges else None,
            series=tuple(series_audits),
            invalid_records=tuple(invalid_records),
        )

    def _audit_series(
        self,
        active_id: int,
        raw_size: int,
        candles: tuple[NormalizedMarketCandle, ...],
        *,
        now_timestamp: int,
    ) -> _SeriesAuditResult:
        valid_count = 0
        invalid_count = 0
        invalid_records: list[InvalidCandleRecord] = []
        previous_timestamp: int | None = None
        seen_timestamps: set[int] = set()
        prices: list[float] = []
        ranges: list[float] = []
        finite_closes = [candle.close for candle in candles if _is_finite(candle.close)]
        finite_ranges = [
            candle.high_candidate - candle.low_candidate
            for candle in candles
            if _is_finite(candle.high_candidate) and _is_finite(candle.low_candidate)
        ]
        reference_price = sum(finite_closes) / len(finite_closes) if finite_closes else None
        reference_range = sum(finite_ranges) / len(finite_ranges) if finite_ranges else None

        for candle in candles:
            reasons = _validate_candle(
                candle,
                previous_timestamp=previous_timestamp,
                seen_timestamps=seen_timestamps,
                now_timestamp=now_timestamp,
                reference_price=reference_price,
                reference_range=reference_range,
            )
            if reasons:
                invalid_count += 1
                invalid_records.append(
                    InvalidCandleRecord(
                        active_id=active_id,
                        raw_size=raw_size,
                        timestamp=candle.start_timestamp,
                        reason=";".join(reasons),
                    )
                )
            else:
                valid_count += 1

            previous_timestamp = candle.start_timestamp
            seen_timestamps.add(candle.start_timestamp)
            prices.extend(_finite_prices(candle))
            price_range = _finite_range(candle)
            if price_range is not None:
                ranges.append(price_range)

        series = CandleSeriesAudit(
            active_id=active_id,
            raw_size=raw_size,
            count=len(candles),
            valid=valid_count,
            invalid=invalid_count,
            first_timestamp=candles[0].start_timestamp if candles else None,
            last_timestamp=candles[-1].start_timestamp if candles else None,
            price_min=min(prices) if prices else None,
            price_max=max(prices) if prices else None,
            low_min=_safe_min([candle.low_candidate for candle in candles]),
            high_max=_safe_max([candle.high_candidate for candle in candles]),
            open_min=_safe_min([candle.open for candle in candles]),
            open_max=_safe_max([candle.open for candle in candles]),
            close_min=_safe_min([candle.close for candle in candles]),
            close_max=_safe_max([candle.close for candle in candles]),
        )
        return _SeriesAuditResult(series=series, invalid_records=tuple(invalid_records), prices=tuple(prices), ranges=tuple(ranges))


@dataclass(frozen=True)
class _SeriesAuditResult:
    series: CandleSeriesAudit
    invalid_records: tuple[InvalidCandleRecord, ...]
    prices: tuple[float, ...]
    ranges: tuple[float, ...]


def _validate_candle(
    candle: NormalizedMarketCandle,
    *,
    previous_timestamp: int | None,
    seen_timestamps: set[int],
    now_timestamp: int,
    reference_price: float | None,
    reference_range: float | None,
) -> tuple[str, ...]:
    reasons: list[str] = []
    price_fields = {
        "open": candle.open,
        "close": candle.close,
        "low": candle.low_candidate,
        "high": candle.high_candidate,
    }

    if any(math.isnan(value) for value in price_fields.values()):
        reasons.append("NAN_VALUE")
    if any(math.isinf(value) for value in price_fields.values()):
        reasons.append("INFINITE_VALUE")
    if any(value < 0 for value in price_fields.values()):
        reasons.append("NEGATIVE_PRICE")
    if any(value == 0 for value in price_fields.values()):
        reasons.append("ZERO_PRICE")

    if all(_is_finite(value) for value in price_fields.values()):
        if candle.high_candidate < candle.low_candidate:
            reasons.append("HIGH_BELOW_LOW")
        if not candle.low_candidate <= candle.open <= candle.high_candidate:
            reasons.append("OPEN_OUT_OF_RANGE")
        if not candle.low_candidate <= candle.close <= candle.high_candidate:
            reasons.append("CLOSE_OUT_OF_RANGE")
        if _is_extreme(candle.high_candidate, reference_price=reference_price, reference_range=reference_range):
            reasons.append("HIGH_EXTREME_OUTLIER")
        if _is_extreme(candle.low_candidate, reference_price=reference_price, reference_range=reference_range):
            reasons.append("LOW_EXTREME_OUTLIER")

    if candle.start_timestamp in seen_timestamps:
        reasons.append("DUPLICATE_TIMESTAMP")
    if previous_timestamp is not None and candle.start_timestamp < previous_timestamp:
        reasons.append("TIMESTAMP_OUT_OF_ORDER")
    if candle.start_timestamp > now_timestamp + FUTURE_TIMESTAMP_TOLERANCE_SECONDS:
        reasons.append("TIMESTAMP_IN_FUTURE")

    return tuple(reasons)


def _is_finite(value: float) -> bool:
    return math.isfinite(value)


def _finite_prices(candle: NormalizedMarketCandle) -> tuple[float, ...]:
    return tuple(
        value
        for value in (candle.open, candle.close, candle.low_candidate, candle.high_candidate)
        if _is_finite(value)
    )


def _finite_range(candle: NormalizedMarketCandle) -> float | None:
    if not _is_finite(candle.high_candidate) or not _is_finite(candle.low_candidate):
        return None
    return candle.high_candidate - candle.low_candidate


def _safe_min(values: list[float]) -> float | None:
    finite_values = [value for value in values if _is_finite(value)]
    return min(finite_values) if finite_values else None


def _safe_max(values: list[float]) -> float | None:
    finite_values = [value for value in values if _is_finite(value)]
    return max(finite_values) if finite_values else None


def _is_extreme(value: float, *, reference_price: float | None, reference_range: float | None) -> bool:
    if reference_price is None:
        return False
    minimum_distance = abs(reference_price) * EXTREME_PRICE_DISTANCE_RATIO
    if reference_range is not None:
        minimum_distance = max(minimum_distance, abs(reference_range) * EXTREME_RANGE_MULTIPLIER)
    return abs(value - reference_price) > max(minimum_distance, 1e-12)
