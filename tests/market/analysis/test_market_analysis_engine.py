from __future__ import annotations

import math

import pytest

from app.market.analysis import AnalysisContext, InvalidProviderData, MarketAnalysisEngine, StatisticsError
from app.market.analysis.health import MarketHealthEvaluator
from app.market.analysis.statistics import MarketStatisticsBuilder
from app.market.providers.base.models import ProviderCandle, ProviderContext, ProviderHistory, ProviderTick


def provider_context(history_state: str = "READY", connection_state: str = "online") -> ProviderContext:
    return ProviderContext(
        provider="TEST",
        asset="EURUSD_otc",
        symbol="EUR/USD OTC",
        timeframe="M1",
        period=60,
        connection_state=connection_state,  # type: ignore[arg-type]
        history_state=history_state,
        readiness="READY",
        last_price=1.3,
        history_count=2,
        timestamp=120,
        metadata={"market_type": "OTC", "provider_version": "test"},
    )


def candle(timestamp: int, open_: float, high: float, low: float, close: float) -> ProviderCandle:
    return ProviderCandle(
        provider="TEST",
        symbol="EURUSD_otc",
        period=60,
        timestamp=timestamp,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=10,
        source="fixture",
        is_closed=True,
    )


def tick(timestamp: int, price: float) -> ProviderTick:
    return ProviderTick(provider="TEST", symbol="EURUSD_otc", period=60, timestamp=timestamp, price=price, source="fixture")


def analysis_context(*, candles: tuple[ProviderCandle, ...] | None = None, ticks: tuple[ProviderTick, ...] | None = None) -> AnalysisContext:
    candles = candles if candles is not None else (candle(60, 1.0, 1.2, 0.9, 1.1), candle(120, 1.1, 1.4, 1.0, 1.3))
    return AnalysisContext(
        provider_context=provider_context(),
        history=ProviderHistory(provider="TEST", symbol="EURUSD_otc", period=60, candles=candles, history_count=len(candles), timestamp=120, source="fixture"),
        ticks=ticks if ticks is not None else (tick(130, 1.35),),
    )


def test_engine_builds_complete_market_analysis() -> None:
    engine = MarketAnalysisEngine()

    analysis = engine.analyze(analysis_context())

    assert analysis.provider == "TEST"
    assert analysis.symbol == "EURUSD_otc"
    assert analysis.market_type == "OTC"
    assert analysis.snapshot.current_price == 1.35
    assert analysis.snapshot.last_close == 1.3
    assert analysis.statistics.total_candles == 2
    assert analysis.statistics.total_ticks == 1
    assert analysis.statistics.highest_price == 1.4
    assert analysis.statistics.lowest_price == 0.9
    assert analysis.statistics.duration == 70
    assert analysis.health.status == "READY"
    assert analysis.metadata.provider_name == "TEST"
    assert analysis.metadata.provider_version == "test"
    assert analysis.analysis_version == "ai-market-analysis-v1"


def test_engine_builds_empty_analysis_without_inventing_data() -> None:
    engine = MarketAnalysisEngine()

    analysis = engine.analyze(analysis_context(candles=(), ticks=()))

    assert analysis.snapshot.current_price == 1.3
    assert analysis.statistics.average_price is None
    assert analysis.statistics.price_range is None
    assert analysis.health.status == "EMPTY"
    assert "NO_CANDLES" in analysis.health.warnings
    assert "NO_TICKS" in analysis.health.warnings


def test_statistics_builder_uses_candles_and_ticks() -> None:
    stats = MarketStatisticsBuilder().build((candle(10, 1.0, 1.5, 0.8, 1.2),), (tick(20, 1.4),))

    assert stats.total_candles == 1
    assert stats.total_ticks == 1
    assert stats.first_timestamp == 10
    assert stats.last_timestamp == 20
    assert stats.duration == 10
    assert stats.highest_price == 1.5
    assert stats.lowest_price == 0.8
    assert stats.price_range == pytest.approx(0.7)
    assert stats.average_price == pytest.approx((1.0 + 1.5 + 0.8 + 1.2 + 1.4) / 5)


def test_statistics_builder_raises_for_invalid_range() -> None:
    with pytest.raises(StatisticsError):
        MarketStatisticsBuilder().build((candle(10, 1.0, 0.8, 1.2, 1.1),), ())


def test_normalizer_sorts_candles_and_ticks() -> None:
    engine = MarketAnalysisEngine()

    analysis = engine.analyze(
        analysis_context(
            candles=(candle(120, 1.1, 1.4, 1.0, 1.3), candle(60, 1.0, 1.2, 0.9, 1.1)),
            ticks=(tick(140, 1.36), tick(130, 1.35)),
        )
    )

    assert [item.timestamp for item in analysis.candles] == [60, 120]
    assert [item.timestamp for item in analysis.ticks] == [130, 140]


def test_normalizer_rejects_provider_mismatch() -> None:
    context = analysis_context()
    bad_history = ProviderHistory(provider="OTHER", symbol="EURUSD_otc", period=60, candles=(), history_count=0, timestamp=None, source="fixture")

    with pytest.raises(InvalidProviderData):
        MarketAnalysisEngine().analyze(AnalysisContext(provider_context=context.provider_context, history=bad_history))


def test_normalizer_rejects_non_finite_prices() -> None:
    with pytest.raises(InvalidProviderData):
        MarketAnalysisEngine().analyze(analysis_context(candles=(candle(60, math.inf, 1.2, 0.9, 1.1),)))

    with pytest.raises(InvalidProviderData):
        MarketAnalysisEngine().analyze(analysis_context(ticks=(tick(60, math.nan),)))


def test_health_evaluator_reports_limited_and_error_states() -> None:
    limited_context = AnalysisContext(
        provider_context=provider_context(history_state="LIMITED"),
        history=ProviderHistory(provider="TEST", symbol="EURUSD_otc", period=60, candles=(candle(60, 1.0, 1.2, 0.9, 1.1),), history_count=1, timestamp=60, source="fixture"),
    )
    error_context = AnalysisContext(
        provider_context=provider_context(connection_state="error"),
        history=ProviderHistory(provider="TEST", symbol="EURUSD_otc", period=60, candles=(), history_count=0, timestamp=None, source="fixture"),
    )

    assert MarketHealthEvaluator().evaluate(limited_context).status == "LIMITED"
    assert MarketHealthEvaluator().evaluate(error_context).status == "ERROR"


def test_analysis_layer_does_not_import_concrete_providers() -> None:
    import pathlib

    for path in pathlib.Path("app/market/analysis").glob("*.py"):
        source = path.read_text()
        assert "app.market.providers.pocket" not in source
        assert "app.market.providers.polarium" not in source
