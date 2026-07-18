from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from app.market.providers.models import ProviderCandle

FeedQualityLevel = Literal["EXCELLENT", "GOOD", "LIMITED", "STALE", "NO_DATA", "CHECKING"]


@dataclass(frozen=True)
class FeedQualityThresholds:
    minimum_window_ms: int
    excellent_p95_ms: int
    good_p95_ms: int
    stale_after_seconds: int
    minimum_changes_for_ready: int


@dataclass(frozen=True)
class FeedQualitySnapshot:
    market_type: str
    symbol: str
    raw_size: int
    classification: FeedQualityLevel
    reason: str
    first_event_latency_ms: int | None
    last_event_at: int | None
    last_movement_at: int | None
    last_candle_timestamp: int | None
    events_received: int
    ohlc_changes: int
    identical_reads: int
    movement_rate: float
    average_movement_interval_ms: int | None
    p50_movement_interval_ms: int | None
    p95_movement_interval_ms: int | None
    maximum_movement_gap_ms: int | None
    stale_age_seconds: int | None
    source_mode: str
    errors: int
    reconnects: int
    measurement_window_ms: int
    minimum_window_ms: int

    def sanitized(self) -> dict:
        return {
            "market_type": self.market_type,
            "symbol": self.symbol,
            "raw_size": self.raw_size,
            "classification": self.classification,
            "reason": self.reason,
            "first_event_latency_ms": self.first_event_latency_ms,
            "last_event_at": self.last_event_at,
            "last_movement_at": self.last_movement_at,
            "last_candle_timestamp": self.last_candle_timestamp,
            "events_received": self.events_received,
            "ohlc_changes": self.ohlc_changes,
            "identical_reads": self.identical_reads,
            "movement_rate": round(self.movement_rate, 4),
            "average_movement_interval_ms": self.average_movement_interval_ms,
            "p50_movement_interval_ms": self.p50_movement_interval_ms,
            "p95_movement_interval_ms": self.p95_movement_interval_ms,
            "maximum_movement_gap_ms": self.maximum_movement_gap_ms,
            "stale_age_seconds": self.stale_age_seconds,
            "source_mode": self.source_mode,
            "errors": self.errors,
            "reconnects": self.reconnects,
            "measurement_window_ms": self.measurement_window_ms,
            "minimum_window_ms": self.minimum_window_ms,
        }


@dataclass
class _FeedQualityMetrics:
    started_at: int
    first_event_at: int | None = None
    last_event_at: int | None = None
    last_movement_at: int | None = None
    last_candle_timestamp: int | None = None
    events_received: int = 0
    ohlc_changes: int = 0
    identical_reads: int = 0
    movement_intervals_ms: list[int] = field(default_factory=list)
    source_mode: str = "CHECKING"
    errors: int = 0
    reconnects: int = 0
    last_signature: tuple[int, float, float, float, float] | None = None


class FeedQualityTracker:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str, int], _FeedQualityMetrics] = {}

    def start(self, *, market_type: str, symbol: str, raw_size: int, now_ms: int) -> None:
        self._metrics.setdefault(_key(market_type, symbol, raw_size), _FeedQualityMetrics(started_at=now_ms))

    def record_event(
        self,
        *,
        market_type: str,
        symbol: str,
        raw_size: int,
        source_mode: str,
        candle: ProviderCandle | None,
        now_ms: int,
        error_code: str | None = None,
    ) -> None:
        metrics = self._metrics.setdefault(_key(market_type, symbol, raw_size), _FeedQualityMetrics(started_at=now_ms))
        metrics.source_mode = source_mode
        if error_code:
            metrics.errors += 1
            return
        metrics.events_received += 1
        metrics.first_event_at = metrics.first_event_at or now_ms
        metrics.last_event_at = now_ms
        if candle is None:
            return
        metrics.last_candle_timestamp = candle.start_timestamp
        signature = _signature(candle)
        if metrics.last_signature is None:
            metrics.ohlc_changes += 1
            metrics.last_movement_at = now_ms
        elif metrics.last_signature == signature:
            metrics.identical_reads += 1
        else:
            metrics.ohlc_changes += 1
            if metrics.last_movement_at is not None:
                metrics.movement_intervals_ms.append(now_ms - metrics.last_movement_at)
                metrics.movement_intervals_ms = metrics.movement_intervals_ms[-100:]
            metrics.last_movement_at = now_ms
        metrics.last_signature = signature

    def record_reconnect(self, *, market_type: str, symbol: str, raw_size: int, now_ms: int) -> None:
        metrics = self._metrics.setdefault(_key(market_type, symbol, raw_size), _FeedQualityMetrics(started_at=now_ms))
        metrics.reconnects += 1

    def snapshot(self, *, market_type: str, symbol: str, raw_size: int, now_ms: int) -> FeedQualitySnapshot:
        thresholds = thresholds_for_raw_size(raw_size)
        metrics = self._metrics.get(_key(market_type, symbol, raw_size))
        if metrics is None:
            return _empty_snapshot(market_type, symbol, raw_size, thresholds)
        return classify_feed_quality(market_type=market_type, symbol=symbol, raw_size=raw_size, metrics=metrics, thresholds=thresholds, now_ms=now_ms)


def thresholds_for_raw_size(raw_size: int) -> FeedQualityThresholds:
    if raw_size <= 60:
        return FeedQualityThresholds(
            minimum_window_ms=15_000,
            excellent_p95_ms=3_000,
            good_p95_ms=8_000,
            stale_after_seconds=raw_size * 3,
            minimum_changes_for_ready=3,
        )
    if raw_size <= 300:
        return FeedQualityThresholds(
            minimum_window_ms=20_000,
            excellent_p95_ms=8_000,
            good_p95_ms=20_000,
            stale_after_seconds=raw_size * 3,
            minimum_changes_for_ready=2,
        )
    return FeedQualityThresholds(
        minimum_window_ms=30_000,
        excellent_p95_ms=15_000,
        good_p95_ms=45_000,
        stale_after_seconds=raw_size * 3,
        minimum_changes_for_ready=1,
    )


def classify_feed_quality(
    *,
    market_type: str,
    symbol: str,
    raw_size: int,
    metrics: _FeedQualityMetrics,
    thresholds: FeedQualityThresholds,
    now_ms: int,
) -> FeedQualitySnapshot:
    window_ms = max(0, now_ms - metrics.started_at)
    stale_age_seconds = _stale_age_seconds(metrics, now_ms)
    first_latency = metrics.first_event_at - metrics.started_at if metrics.first_event_at is not None else None
    average_interval = _average(metrics.movement_intervals_ms)
    p50_interval = _percentile(metrics.movement_intervals_ms, 0.5)
    p95_interval = _percentile(metrics.movement_intervals_ms, 0.95)
    max_gap = max(metrics.movement_intervals_ms) if metrics.movement_intervals_ms else None
    movement_rate = metrics.ohlc_changes / (window_ms / 1000) if window_ms > 0 else 0.0
    classification, reason = _classification(metrics, thresholds, window_ms, stale_age_seconds, p95_interval, movement_rate)
    return FeedQualitySnapshot(
        market_type=market_type,
        symbol=symbol,
        raw_size=raw_size,
        classification=classification,
        reason=reason,
        first_event_latency_ms=first_latency,
        last_event_at=metrics.last_event_at,
        last_movement_at=metrics.last_movement_at,
        last_candle_timestamp=metrics.last_candle_timestamp,
        events_received=metrics.events_received,
        ohlc_changes=metrics.ohlc_changes,
        identical_reads=metrics.identical_reads,
        movement_rate=movement_rate,
        average_movement_interval_ms=average_interval,
        p50_movement_interval_ms=p50_interval,
        p95_movement_interval_ms=p95_interval,
        maximum_movement_gap_ms=max_gap,
        stale_age_seconds=stale_age_seconds,
        source_mode=metrics.source_mode,
        errors=metrics.errors,
        reconnects=metrics.reconnects,
        measurement_window_ms=window_ms,
        minimum_window_ms=thresholds.minimum_window_ms,
    )


def _classification(
    metrics: _FeedQualityMetrics,
    thresholds: FeedQualityThresholds,
    window_ms: int,
    stale_age_seconds: int | None,
    p95_interval: int | None,
    movement_rate: float,
) -> tuple[FeedQualityLevel, str]:
    if metrics.events_received == 0:
        return ("CHECKING", "Aguardando primeiro evento") if window_ms < thresholds.minimum_window_ms else ("NO_DATA", "Sem eventos na janela")
    if metrics.source_mode == "NO_DATA":
        return "NO_DATA", "Sem dados utilizáveis"
    if metrics.source_mode == "STALE" or (stale_age_seconds is not None and stale_age_seconds > thresholds.stale_after_seconds):
        return "STALE", "Candle atrasado para o timeframe"
    if window_ms < thresholds.minimum_window_ms:
        return "CHECKING", "Janela mínima em formação"
    if metrics.source_mode == "SNAPSHOT":
        return "LIMITED", "Atualização predominante por snapshot"
    if metrics.ohlc_changes < thresholds.minimum_changes_for_ready:
        return "LIMITED", "Poucos movimentos reais observados"
    if p95_interval is not None and p95_interval <= thresholds.excellent_p95_ms and movement_rate >= 0.2:
        return "EXCELLENT", "Cadência excelente para o timeframe"
    if p95_interval is not None and p95_interval <= thresholds.good_p95_ms:
        return "GOOD", "Cadência adequada para o timeframe"
    return "LIMITED", "Gaps longos para o timeframe"


def _empty_snapshot(market_type: str, symbol: str, raw_size: int, thresholds: FeedQualityThresholds) -> FeedQualitySnapshot:
    return FeedQualitySnapshot(
        market_type=market_type,
        symbol=symbol,
        raw_size=raw_size,
        classification="CHECKING",
        reason="Contexto ainda não medido nesta sessão",
        first_event_latency_ms=None,
        last_event_at=None,
        last_movement_at=None,
        last_candle_timestamp=None,
        events_received=0,
        ohlc_changes=0,
        identical_reads=0,
        movement_rate=0.0,
        average_movement_interval_ms=None,
        p50_movement_interval_ms=None,
        p95_movement_interval_ms=None,
        maximum_movement_gap_ms=None,
        stale_age_seconds=None,
        source_mode="CHECKING",
        errors=0,
        reconnects=0,
        measurement_window_ms=0,
        minimum_window_ms=thresholds.minimum_window_ms,
    )


def _key(market_type: str, symbol: str, raw_size: int) -> tuple[str, str, int]:
    return (market_type.upper(), symbol, raw_size)


def _signature(candle: ProviderCandle) -> tuple[int, float, float, float, float]:
    return (candle.start_timestamp, candle.open, candle.high, candle.low, candle.close)


def _stale_age_seconds(metrics: _FeedQualityMetrics, now_ms: int) -> int | None:
    if metrics.last_candle_timestamp is None:
        return None
    return max(0, int(now_ms / 1000) - metrics.last_candle_timestamp)


def _average(values: list[int]) -> int | None:
    if not values:
        return None
    return int(sum(values) / len(values))


def _percentile(values: list[int], ratio: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * ratio))))
    return int(ordered[index])
