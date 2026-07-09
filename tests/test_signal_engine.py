from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
import pytest

from app.indicators.atr import calculate_atr
from app.indicators.ema import calculate_ema
from app.indicators.rsi import calculate_rsi
from app.indicators.signal_engine import SignalEngineService
from app.main import app
from app.models.candle import Candle

client = TestClient(app)


def _build_trending_candles(direction: str = "up", limit: int = 50) -> list[Candle]:
    candles: list[Candle] = []
    base = 1.1000
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=limit)

    for index in range(limit):
        step = 0.00008 if direction == "up" else -0.00008
        open_price = base + (index * step)
        close_price = open_price + (0.00005 if direction == "up" else -0.00005)
        high_price = max(open_price, close_price) + 0.00012
        low_price = min(open_price, close_price) - 0.00012
        candles.append(
            Candle(
                symbol="EURUSD-OTC",
                timeframe="M1",
                timestamp=timestamp + timedelta(minutes=index),
                open=round(open_price, 5),
                high=round(high_price, 5),
                low=round(low_price, 5),
                close=round(close_price, 5),
                volume=100 + index,
            )
        )
    return candles


def test_calculate_ema_returns_float() -> None:
    values = [float(value) for value in range(1, 31)]

    ema = calculate_ema(values, 9)

    assert isinstance(ema, float)
    assert ema > 0


def test_calculate_rsi_in_expected_range() -> None:
    values = [1.1000, 1.1005, 1.1002, 1.1008, 1.1010, 1.1007, 1.1012, 1.1015,
              1.1011, 1.1018, 1.1020, 1.1016, 1.1022, 1.1025, 1.1028, 1.1024]

    rsi = calculate_rsi(values, 14)

    assert 0 <= rsi <= 100


def test_calculate_atr_returns_positive_value() -> None:
    candles = _build_trending_candles(limit=30)

    atr = calculate_atr(candles, 14)

    assert atr > 0


def test_signal_engine_detects_buy_trend() -> None:
    candles = _build_trending_candles(direction="up", limit=50)

    result = SignalEngineService().analyze_candles(candles, symbol="EURUSD-OTC", timeframe="M1")

    assert result.symbol == "EURUSD-OTC"
    assert result.trend in {"BUY", "NEUTRAL"}
    assert 0 <= result.strength <= 100
    assert result.ema9 > 0
    assert result.ema21 > 0
    assert result.rsi14 >= 0
    assert result.atr14 > 0


def test_signal_engine_endpoint() -> None:
    response = client.get("/api/v1/signal/analyze?symbol=EURUSD-OTC&timeframe=M1&limit=50")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "EURUSD-OTC"
    assert data["timeframe"] == "M1"
    assert data["candles_analyzed"] == 50
    assert "ema9" in data
    assert "ema21" in data
    assert "rsi14" in data
    assert "atr14" in data
    assert data["trend"] in ["BUY", "SELL", "NEUTRAL"]
    assert 0 <= data["strength"] <= 100


def test_signal_engine_requires_enough_candles() -> None:
    candles = _build_trending_candles(limit=10)

    with pytest.raises(ValueError):
        SignalEngineService().analyze_candles(candles, symbol="EURUSD-OTC", timeframe="M1")
