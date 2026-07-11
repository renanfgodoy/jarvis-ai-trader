from dataclasses import replace

from app.market.events.models import NormalizedMarketCandle
from app.market.store import CandleStore


def make_candle(
    *,
    active_id: int | None = 76,
    raw_size: int = 60,
    start_timestamp: int = 100,
    close: float = 1.2,
    volume: float = 0,
) -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=active_id,
        symbol=None,
        raw_size=raw_size,
        timeframe=None,
        start_timestamp=start_timestamp,
        end_timestamp=start_timestamp + raw_size,
        open=1.1,
        close=close,
        low_candidate=1.0,
        high_candidate=1.3,
        volume=volume,
        source="polarium",
        source_event="candle-generated",
        source_verified=True,
        mapping_verified=False,
        mapping_notes=("sanitized fixture",),
    )


def test_add_candle() -> None:
    store = CandleStore()

    result = store.add(make_candle())

    assert result.status == "added"
    assert len(store.series(active_id=76, raw_size=60)) == 1


def test_update_existing_candle_with_same_timestamp() -> None:
    store = CandleStore()
    candle = make_candle(start_timestamp=100, close=1.2)
    updated = replace(candle, close=1.25)

    store.add(candle)
    result = store.add(updated)

    assert result.status == "updated"
    assert store.series(active_id=76, raw_size=60)[0].close == 1.25


def test_ignore_identical_duplicate() -> None:
    store = CandleStore()
    candle = make_candle(start_timestamp=100)

    store.add(candle)
    result = store.add(candle)

    assert result.status == "ignored"
    assert len(store.series(active_id=76, raw_size=60)) == 1


def test_ordering_by_start_timestamp() -> None:
    store = CandleStore()

    store.add(make_candle(start_timestamp=300))
    store.add(make_candle(start_timestamp=100))
    store.add(make_candle(start_timestamp=200))

    assert [c.start_timestamp for c in store.series(active_id=76, raw_size=60)] == [100, 200, 300]


def test_max_limit_keeps_latest_candles() -> None:
    store = CandleStore(max_candles_per_series=2)

    store.add(make_candle(start_timestamp=100))
    store.add(make_candle(start_timestamp=200))
    store.add(make_candle(start_timestamp=300))

    assert [c.start_timestamp for c in store.series(active_id=76, raw_size=60)] == [200, 300]


def test_latest_returns_last_n_candles() -> None:
    store = CandleStore()
    for timestamp in [100, 200, 300]:
        store.add(make_candle(start_timestamp=timestamp))

    latest = store.latest(active_id=76, raw_size=60, limit=2)

    assert [c.start_timestamp for c in latest] == [200, 300]


def test_separates_by_active_id() -> None:
    store = CandleStore()

    store.add(make_candle(active_id=76, start_timestamp=100))
    store.add(make_candle(active_id=2298, start_timestamp=100))

    assert len(store.series(active_id=76, raw_size=60)) == 1
    assert len(store.series(active_id=2298, raw_size=60)) == 1
    assert len(store.series_keys()) == 2


def test_separates_by_raw_size() -> None:
    store = CandleStore()

    store.add(make_candle(raw_size=60, start_timestamp=100))
    store.add(make_candle(raw_size=300, start_timestamp=100))

    assert len(store.series(active_id=76, raw_size=60)) == 1
    assert len(store.series(active_id=76, raw_size=300)) == 1
    assert len(store.series_keys()) == 2


def test_empty_collection_returns_empty_tuple() -> None:
    store = CandleStore()

    assert store.series(active_id=76, raw_size=60) == ()
    assert store.latest(active_id=76, raw_size=60, limit=5) == ()


def test_store_is_memory_only_and_can_be_cleared() -> None:
    store = CandleStore()
    store.add(make_candle())

    store.clear()

    assert store.series_keys() == ()


def test_rejects_candle_without_active_id() -> None:
    store = CandleStore()

    result = store.add(make_candle(active_id=None))

    assert result.status == "rejected"
    assert store.series_keys() == ()


def test_does_not_invent_symbol_timeframe_or_mapping_verification() -> None:
    store = CandleStore()
    candle = make_candle()

    store.add(candle)
    stored = store.series(active_id=76, raw_size=60)[0]

    assert stored.symbol is None
    assert stored.timeframe is None
    assert stored.mapping_verified is False
