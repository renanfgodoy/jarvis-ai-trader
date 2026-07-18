from app.market.events.models import NormalizedMarketCandle
from app.market.chart import CandleChartService
from app.market.store import CandleStore


def make_candle(start_timestamp: int, *, active_id: int | None = 76, symbol: str | None = None, raw_size: int = 60, source: str = "polarium") -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=active_id,
        symbol=symbol,
        raw_size=raw_size,
        timeframe=None,
        start_timestamp=start_timestamp,
        end_timestamp=start_timestamp + raw_size,
        open=1.1 + start_timestamp / 100000,
        close=1.2 + start_timestamp / 100000,
        low_candidate=1.0 + start_timestamp / 100000,
        high_candidate=1.3 + start_timestamp / 100000,
        volume=0,
        source=source,
        source_event="candle-generated",
        source_verified=True,
        mapping_verified=False,
        mapping_notes=("sanitized fixture",),
    )


def test_chart_service_returns_empty_series() -> None:
    service = CandleChartService(CandleStore())

    series = service.get_chart_series(active_id=76, raw_size=60, limit=50)

    assert series.active_id == 76
    assert series.raw_size == 60
    assert series.candles == ()


def test_chart_service_transforms_single_candle() -> None:
    store = CandleStore()
    store.add(make_candle(100))
    service = CandleChartService(store)

    series = service.get_chart_series(active_id=76, raw_size=60, limit=50)

    assert len(series.candles) == 1
    candle = series.candles[0]
    assert candle.time == 100
    assert candle.open == 1.101
    assert candle.high == 1.301
    assert candle.low == 1.001
    assert candle.close == 1.2009999999999998


def test_chart_service_transforms_multiple_candles() -> None:
    store = CandleStore()
    store.add(make_candle(100))
    store.add(make_candle(200))
    service = CandleChartService(store)

    series = service.get_chart_series(active_id=76, raw_size=60, limit=50)

    assert [candle.time for candle in series.candles] == [100, 200]


def test_chart_service_preserves_store_ordering() -> None:
    store = CandleStore()
    store.add(make_candle(300))
    store.add(make_candle(100))
    store.add(make_candle(200))
    service = CandleChartService(store)

    series = service.get_chart_series(active_id=76, raw_size=60, limit=50)

    assert [candle.time for candle in series.candles] == [100, 200, 300]


def test_chart_service_uses_requested_limit() -> None:
    store = CandleStore()
    store.add(make_candle(100))
    store.add(make_candle(200))
    store.add(make_candle(300))
    service = CandleChartService(store)

    series = service.get_chart_series(active_id=76, raw_size=60, limit=2)

    assert [candle.time for candle in series.candles] == [200, 300]


def test_chart_service_does_not_return_iq_option_series_as_polarium_active_id() -> None:
    store = CandleStore()
    store.add(make_candle(100, active_id=None, symbol="EURUSD-OTC", source="iq_option"))
    service = CandleChartService(store)

    polarium = service.get_chart_series(active_id=76, raw_size=60, limit=50)
    iq_series = service.get_available_series()

    assert polarium.candles == ()
    assert any(summary.provider == "IQ_OPTION" and summary.symbol == "EURUSD-OTC" for summary in iq_series)
