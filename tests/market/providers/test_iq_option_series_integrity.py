from __future__ import annotations

from app.market.chart.runtime_service import MarketChartRuntimeService
from app.market.events.models import NormalizedMarketCandle
from app.market.providers.iq_option.series_integrity import IQOptionSeriesIntegrityAnalyzer, analyze_iq_option_candles
from app.market.store import CandleStore


def candle(
    *,
    source: str = "iq_option",
    symbol: str | None = "EURUSD-OTC",
    active_id: int | None = None,
    raw_size: int = 60,
    start_timestamp: int,
    close: float = 1.12,
) -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=active_id,
        symbol=symbol,
        raw_size=raw_size,
        timeframe=None,
        start_timestamp=start_timestamp,
        end_timestamp=start_timestamp + raw_size,
        open=close,
        close=close,
        low_candidate=close - 0.001,
        high_candidate=close + 0.001,
        volume=0,
        source=source,
        source_event="test",
        source_verified=True,
        mapping_verified=True,
        mapping_notes=("test",),
    )


def test_iq_option_and_polarium_series_do_not_collide_on_same_timestamp() -> None:
    store = CandleStore(max_candles_per_series=1000)
    store.add(candle(start_timestamp=1_783_720_000, close=1.12))
    store.add(candle(source="polarium", symbol=None, active_id=76, start_timestamp=1_783_720_000, close=0.98))

    iq_series = MarketChartRuntimeService(store).get_provider_series("IQ_OPTION", "EURUSD-OTC", 60, 1000)
    polarium_series = MarketChartRuntimeService(store).get_series(76, 60, 1000)

    assert len(iq_series.candles) == 1
    assert len(polarium_series.candles) == 1
    assert iq_series.candles[0].close == 1.12
    assert polarium_series.candles[0].close == 0.98


def test_iq_option_symbols_and_timeframes_do_not_collide() -> None:
    store = CandleStore(max_candles_per_series=1000)
    store.add(candle(symbol="EURUSD-OTC", raw_size=60, start_timestamp=1_783_720_000, close=1.12))
    store.add(candle(symbol="GBPUSD-OTC", raw_size=60, start_timestamp=1_783_720_000, close=1.30))
    store.add(candle(symbol="EURUSD-OTC", raw_size=300, start_timestamp=1_783_720_000, close=1.10))

    chart = MarketChartRuntimeService(store)

    assert chart.get_provider_series("IQ_OPTION", "EURUSD-OTC", 60, 1000).candles[0].close == 1.12
    assert chart.get_provider_series("IQ_OPTION", "GBPUSD-OTC", 60, 1000).candles[0].close == 1.30
    assert chart.get_provider_series("IQ_OPTION", "EURUSD-OTC", 300, 1000).candles[0].close == 1.10


def test_duplicate_timestamp_updates_existing_iq_option_candle() -> None:
    store = CandleStore(max_candles_per_series=1000)

    first = store.add(candle(start_timestamp=1_783_720_000, close=1.12))
    second = store.add(candle(start_timestamp=1_783_720_000, close=1.13))
    series = MarketChartRuntimeService(store).get_provider_series("IQ_OPTION", "EURUSD-OTC", 60, 1000)

    assert first.status == "added"
    assert second.status == "updated"
    assert len(series.candles) == 1
    assert series.candles[0].close == 1.13


def test_integrity_report_flags_price_cluster_split_and_gap() -> None:
    candles = tuple(
        candle(start_timestamp=1_783_720_000 + index * 60, close=1.12 if index < 8 else 0.98)
        for index in range(16)
    )

    report = analyze_iq_option_candles(symbol="EURUSD-OTC", raw_size=60, candles=candles)

    assert report.integrity_status == "FAIL"
    assert "PRICE_CLUSTER_SPLIT" in report.reason_codes
    assert "EXTREME_CONSECUTIVE_GAP" in report.reason_codes
    assert report.count == 16
    assert report.distinct_providers == ("IQ_OPTION",)
    assert report.distinct_symbols == ("EURUSD-OTC",)
    assert report.distinct_raw_sizes == (60,)


def test_integrity_endpoint_payload_is_sanitized_shape() -> None:
    store = CandleStore(max_candles_per_series=1000)
    store.add(candle(start_timestamp=1_783_720_000, close=1.12))

    payload = IQOptionSeriesIntegrityAnalyzer(store).analyze(symbol="EURUSD-OTC", raw_size=60).sanitized()

    assert payload["provider"] == "IQ_OPTION"
    assert payload["symbol"] == "EURUSD-OTC"
    assert payload["raw_size"] == 60
    assert payload["count"] == 1
    assert "candles" not in payload
    assert "token" not in str(payload).lower()
    assert "password" not in str(payload).lower()
