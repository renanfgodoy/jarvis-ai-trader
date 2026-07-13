from app.market.chart.runtime_service import MarketChartRuntimeService
from app.market.events.models import NormalizedMarketCandle
from app.market.store import CandleStore


def make_candle(start_timestamp: int, *, active_id: int = 76, raw_size: int = 60, symbol: str | None = None) -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=active_id,
        symbol=symbol,
        raw_size=raw_size,
        timeframe=None,
        start_timestamp=start_timestamp,
        end_timestamp=start_timestamp + raw_size,
        open=1.1,
        close=1.2,
        low_candidate=1.0,
        high_candidate=1.3,
        volume=0,
        source="polarium",
        source_event="candle-generated",
        source_verified=True,
        mapping_verified=False,
        mapping_notes=("sanitized fixture",),
    )


def test_runtime_service_returns_empty_store_series() -> None:
    service = MarketChartRuntimeService(CandleStore())

    series = service.get_series(active_id=76, raw_size=60, limit=100)

    assert series.candles == ()


def test_runtime_service_returns_existing_series() -> None:
    store = CandleStore()
    store.add(make_candle(100))
    service = MarketChartRuntimeService(store)

    series = service.get_series(active_id=76, raw_size=60, limit=100)

    assert len(series.candles) == 1
    assert series.candles[0].time == 100
    assert series.symbol is None


def test_runtime_service_respects_limit() -> None:
    store = CandleStore()
    store.add(make_candle(100))
    store.add(make_candle(200))
    store.add(make_candle(300))
    service = MarketChartRuntimeService(store)

    series = service.get_series(active_id=76, raw_size=60, limit=2)

    assert [candle.time for candle in series.candles] == [200, 300]


def test_runtime_service_returns_empty_for_unknown_active_id() -> None:
    store = CandleStore()
    store.add(make_candle(100, active_id=76))
    service = MarketChartRuntimeService(store)

    series = service.get_series(active_id=2298, raw_size=60, limit=100)

    assert series.candles == ()


def test_runtime_service_returns_empty_for_unknown_raw_size() -> None:
    store = CandleStore()
    store.add(make_candle(100, raw_size=60))
    service = MarketChartRuntimeService(store)

    series = service.get_series(active_id=76, raw_size=300, limit=100)

    assert series.candles == ()


def test_runtime_service_lists_available_series_metadata() -> None:
    store = CandleStore()
    store.add(make_candle(100, active_id=76, raw_size=60, symbol="EUR/USD OTC"))
    store.add(make_candle(200, active_id=76, raw_size=60))
    store.add(make_candle(300, active_id=2298, raw_size=300, symbol="BTC/USD"))
    service = MarketChartRuntimeService(store)

    summaries = service.get_available_series()

    assert [(item.active_id, item.symbol, item.raw_size, item.count, item.latest_time) for item in summaries] == [
        (76, "EUR/USD OTC", 60, 2, 200),
        (2298, "BTC/USD", 300, 1, 300),
    ]


def test_runtime_service_updates_symbol_when_selected_asset_changes() -> None:
    store = CandleStore()
    store.add(make_candle(100, active_id=76, raw_size=60, symbol="EUR/USD OTC"))
    store.add(make_candle(100, active_id=2298, raw_size=60, symbol="BTC/USD"))
    service = MarketChartRuntimeService(store)

    eurusd = service.get_series(active_id=76, raw_size=60, limit=100)
    btcusd = service.get_series(active_id=2298, raw_size=60, limit=100)

    assert eurusd.symbol == "EUR/USD OTC"
    assert btcusd.symbol == "BTC/USD"
