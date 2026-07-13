from __future__ import annotations

import math

from fastapi.testclient import TestClient

from app.main import app
from app.market.events.models import NormalizedMarketCandle
from app.market.persistence import CandleIntegrityAuditor
from app.market.runtime import market_candle_persistence, market_candle_store
from app.market.store import CandleSeriesKey, CandleStore
from app.market.store.repository import InMemoryCandleRepository

client = TestClient(app)


def make_candle(
    start_timestamp: int,
    *,
    active_id: int = 76,
    raw_size: int = 60,
    open_price: float = 1.1,
    close: float = 1.2,
    low: float = 1.0,
    high: float = 1.3,
) -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=active_id,
        symbol=None,
        raw_size=raw_size,
        timeframe=None,
        start_timestamp=start_timestamp,
        end_timestamp=start_timestamp + raw_size,
        open=open_price,
        close=close,
        low_candidate=low,
        high_candidate=high,
        volume=0,
        source="polarium",
        source_event="candle-generated",
        source_verified=True,
        mapping_verified=False,
        mapping_notes=("sanitized fixture",),
    )


def audit_single(candle: NormalizedMarketCandle, *, now_timestamp: int = 1_000) -> dict:
    store = CandleStore()
    store.add(candle)
    return CandleIntegrityAuditor(store).audit(now_timestamp=now_timestamp).sanitized()


def invalid_reasons(audit: dict) -> str:
    return ";".join(item["reason"] for item in audit["invalid_candle_records"])


def test_valid_candle_passes_integrity_audit() -> None:
    audit = audit_single(make_candle(100))

    assert audit["series_count"] == 1
    assert audit["total_candles"] == 1
    assert audit["valid_candles"] == 1
    assert audit["invalid_candles"] == 0
    assert audit["invalid_candle_records"] == []


def test_high_lower_than_low_is_invalid() -> None:
    audit = audit_single(make_candle(100, low=1.3, high=1.0))

    assert "HIGH_BELOW_LOW" in invalid_reasons(audit)
    assert audit["invalid_candles"] == 1


def test_open_outside_price_range_is_invalid() -> None:
    audit = audit_single(make_candle(100, open_price=1.5))

    assert "OPEN_OUT_OF_RANGE" in invalid_reasons(audit)


def test_close_outside_price_range_is_invalid() -> None:
    audit = audit_single(make_candle(100, close=0.8))

    assert "CLOSE_OUT_OF_RANGE" in invalid_reasons(audit)


def test_duplicate_timestamp_is_invalid() -> None:
    repository = InMemoryCandleRepository()
    repository.set_series(
        CandleSeriesKey(active_id=76, raw_size=60),
        (make_candle(100), make_candle(100, close=1.25)),
    )
    store = CandleStore(repository=repository)

    audit = CandleIntegrityAuditor(store).audit(now_timestamp=1_000).sanitized()

    assert "DUPLICATE_TIMESTAMP" in invalid_reasons(audit)
    assert audit["invalid_candles"] == 1


def test_out_of_order_timestamp_is_invalid() -> None:
    repository = InMemoryCandleRepository()
    repository.set_series(CandleSeriesKey(active_id=76, raw_size=60), (make_candle(200), make_candle(100)))
    store = CandleStore(repository=repository)

    audit = CandleIntegrityAuditor(store).audit(now_timestamp=1_000).sanitized()

    assert "TIMESTAMP_OUT_OF_ORDER" in invalid_reasons(audit)


def test_nan_price_is_invalid() -> None:
    audit = audit_single(make_candle(100, close=math.nan))

    assert "NAN_VALUE" in invalid_reasons(audit)


def test_infinite_price_is_invalid() -> None:
    audit = audit_single(make_candle(100, high=math.inf))

    assert "INFINITE_VALUE" in invalid_reasons(audit)


def test_negative_price_is_invalid() -> None:
    audit = audit_single(make_candle(100, low=-1.0))

    assert "NEGATIVE_PRICE" in invalid_reasons(audit)


def test_audit_statistics_are_calculated_without_exposing_ohlc_per_invalid_candle() -> None:
    store = CandleStore()
    store.add(make_candle(100, close=1.2, low=1.0, high=1.4))
    store.add(make_candle(160, close=1.3, low=1.1, high=1.5))
    store.add(make_candle(220, close=2.0, low=1.1, high=1.5))

    audit = CandleIntegrityAuditor(store).audit(now_timestamp=1_000).sanitized()
    invalid_record_keys = set(audit["invalid_candle_records"][0].keys())

    assert audit["series_count"] == 1
    assert audit["total_candles"] == 3
    assert audit["valid_candles"] == 2
    assert audit["invalid_candles"] == 1
    assert audit["largest_price"] == 2.0
    assert audit["smallest_price"] == 1.0
    assert audit["largest_range"] == 0.3999999999999999
    assert audit["smallest_range"] == 0.3999999999999999
    assert invalid_record_keys == {"active_id", "raw_size", "timestamp", "reason"}


def test_multiple_series_are_audited_independently() -> None:
    store = CandleStore()
    store.add(make_candle(100, active_id=76, raw_size=60))
    store.add(make_candle(100, active_id=2298, raw_size=300))

    audit = CandleIntegrityAuditor(store).audit(now_timestamp=1_000).sanitized()
    series_keys = {(item["active_id"], item["raw_size"]) for item in audit["series"]}

    assert audit["series_count"] == 2
    assert audit["total_candles"] == 2
    assert series_keys == {(76, 60), (2298, 300)}


def test_future_timestamp_and_zero_price_are_invalid() -> None:
    audit = audit_single(make_candle(10_000, open_price=0.0), now_timestamp=1_000)

    reasons = invalid_reasons(audit)
    assert "TIMESTAMP_IN_FUTURE" in reasons
    assert "ZERO_PRICE" in reasons


def test_persistence_audit_endpoint_returns_sanitized_read_only_report() -> None:
    market_candle_persistence.cleanup(market_candle_store)
    market_candle_store.add(make_candle(100))

    response = client.get("/api/v1/market/persistence/audit")

    assert response.status_code == 200
    body = response.json()
    assert body["series_count"] == 1
    assert body["total_candles"] == 1
    assert "invalid_candle_records" in body
    assert "cookies" not in str(body).lower()
    assert "authorization" not in str(body).lower()
