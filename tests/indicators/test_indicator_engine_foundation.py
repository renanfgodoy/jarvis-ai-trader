from typing import Any

import pytest

from app.indicators import BaseIndicator, IndicatorEngine, IndicatorRegistry, IndicatorRequest, IndicatorValue
from app.indicators.errors import IndicatorAlreadyRegisteredError, IndicatorNotFoundError
from app.market.events.models import NormalizedMarketCandle
from app.market.store import CandleStore


class TestCandleCountIndicator(BaseIndicator):
    name = "test-candle-count"
    min_candles = 2

    def calculate(
        self,
        candles: tuple[NormalizedMarketCandle, ...],
        parameters: dict[str, Any] | None = None,
    ) -> IndicatorValue:
        return IndicatorValue(
            name=self.name,
            value=len(candles),
            metadata={
                "first_timestamp": candles[0].start_timestamp,
                "last_timestamp": candles[-1].start_timestamp,
                "parameters": parameters or {},
            },
        )


def make_candle(start_timestamp: int, *, active_id: int = 76, raw_size: int = 60) -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=active_id,
        symbol=None,
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


def build_engine_with_store() -> tuple[IndicatorEngine, CandleStore]:
    store = CandleStore()
    registry = IndicatorRegistry()
    registry.register(TestCandleCountIndicator())
    return IndicatorEngine(candle_store=store, registry=registry), store


def test_registry_registers_and_lists_indicator() -> None:
    registry = IndicatorRegistry()

    registry.register(TestCandleCountIndicator())

    assert registry.names() == ("test-candle-count",)
    assert registry.get("TEST-CANDLE-COUNT").name == "test-candle-count"


def test_registry_rejects_duplicate_indicator_name() -> None:
    registry = IndicatorRegistry()
    registry.register(TestCandleCountIndicator())

    with pytest.raises(IndicatorAlreadyRegisteredError):
        registry.register(TestCandleCountIndicator())


def test_registry_raises_for_unknown_indicator() -> None:
    registry = IndicatorRegistry()

    with pytest.raises(IndicatorNotFoundError):
        registry.get("missing")


def test_engine_runs_test_indicator_against_candle_store() -> None:
    engine, store = build_engine_with_store()
    store.add(make_candle(100))
    store.add(make_candle(200))
    store.add(make_candle(300))

    result = engine.run(IndicatorRequest(name="test-candle-count", active_id=76, raw_size=60, limit=2))

    assert result.success is True
    assert result.candles_used == 2
    assert result.value is not None
    assert result.value.value == 2
    assert result.value.metadata["first_timestamp"] == 200
    assert result.value.metadata["last_timestamp"] == 300


def test_engine_returns_error_for_unknown_indicator() -> None:
    engine, store = build_engine_with_store()
    store.add(make_candle(100))
    store.add(make_candle(200))

    result = engine.run(IndicatorRequest(name="missing", active_id=76, raw_size=60, limit=2))

    assert result.success is False
    assert result.value is None
    assert result.errors


def test_engine_returns_error_for_insufficient_candles() -> None:
    engine, store = build_engine_with_store()
    store.add(make_candle(100))

    result = engine.run(IndicatorRequest(name="test-candle-count", active_id=76, raw_size=60, limit=2))

    assert result.success is False
    assert result.candles_used == 0
    assert "requires 2 candle" in result.errors[0]


def test_engine_uses_active_id_and_raw_size_series_only() -> None:
    engine, store = build_engine_with_store()
    store.add(make_candle(100, active_id=76, raw_size=60))
    store.add(make_candle(200, active_id=76, raw_size=60))
    store.add(make_candle(300, active_id=2298, raw_size=60))
    store.add(make_candle(400, active_id=76, raw_size=300))

    result = engine.run(IndicatorRequest(name="test-candle-count", active_id=76, raw_size=60, limit=10))

    assert result.success is True
    assert result.value is not None
    assert result.value.value == 2


def test_engine_rejects_invalid_request_limit() -> None:
    engine, _store = build_engine_with_store()

    result = engine.run(IndicatorRequest(name="test-candle-count", active_id=76, raw_size=60, limit=0))

    assert result.success is False
    assert "limit" in result.errors[0]


def test_test_indicator_does_not_invent_symbol_or_timeframe() -> None:
    engine, store = build_engine_with_store()
    store.add(make_candle(100))
    store.add(make_candle(200))

    result = engine.run(IndicatorRequest(name="test-candle-count", active_id=76, raw_size=60, limit=2))
    candles = store.series(active_id=76, raw_size=60)

    assert result.success is True
    assert all(candle.symbol is None for candle in candles)
    assert all(candle.timeframe is None for candle in candles)
    assert all(candle.mapping_verified is False for candle in candles)
