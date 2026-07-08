from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.models.candle import Candle
from app.services.ai_decision import AIDecisionEngine

client = TestClient(app)


def _make_candle(index: int, open_price: float, close_price: float) -> Candle:
    return Candle(
        symbol="EURUSD-OTC",
        timeframe="M1",
        timestamp=datetime.now(timezone.utc) + timedelta(minutes=index),
        open=open_price,
        high=max(open_price, close_price) + 0.00020,
        low=min(open_price, close_price) - 0.00020,
        close=close_price,
        volume=500,
    )


def test_ai_decision_endpoint_returns_valid_structure() -> None:
    response = client.get("/api/v1/ai/decision?symbol=EURUSD-OTC&timeframe=M1&limit=20")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "EURUSD-OTC"
    assert data["timeframe"] == "M1"
    assert data["signal"] in ["BUY", "SELL", "WAIT"]
    assert 0 <= data["confidence"] <= 100
    assert "Não é recomendação financeira" in data["disclaimer"]


def test_ai_decision_detects_buy_context_with_bullish_candles() -> None:
    candles = [
        _make_candle(1, 1.1000, 1.1004),
        _make_candle(2, 1.1004, 1.1008),
        _make_candle(3, 1.1008, 1.1012),
        _make_candle(4, 1.1012, 1.1016),
        _make_candle(5, 1.1016, 1.1020),
    ]
    decision = AIDecisionEngine().analyze_candles(candles=candles, symbol="eurusd-otc", timeframe="M1")

    assert decision.signal == "BUY"
    assert decision.trend == "UP"
    assert decision.confidence >= 55
    assert decision.symbol == "EURUSD-OTC"


def test_ai_decision_detects_sell_context_with_bearish_candles() -> None:
    candles = [
        _make_candle(1, 1.1020, 1.1016),
        _make_candle(2, 1.1016, 1.1012),
        _make_candle(3, 1.1012, 1.1008),
        _make_candle(4, 1.1008, 1.1004),
        _make_candle(5, 1.1004, 1.1000),
    ]
    decision = AIDecisionEngine().analyze_candles(candles=candles, symbol="eurusd-otc", timeframe="M1")

    assert decision.signal == "SELL"
    assert decision.trend == "DOWN"
    assert decision.confidence >= 55


def test_ai_decision_waits_when_market_has_no_clear_direction() -> None:
    candles = [
        _make_candle(1, 1.1000, 1.1001),
        _make_candle(2, 1.1001, 1.1000),
        _make_candle(3, 1.1000, 1.1001),
        _make_candle(4, 1.1001, 1.1000),
        _make_candle(5, 1.1000, 1.1001),
    ]
    decision = AIDecisionEngine().analyze_candles(candles=candles, symbol="eurusd-otc", timeframe="M1")

    assert decision.signal == "WAIT"
    assert decision.grade in ["C", "NO_TRADE"]
    assert decision.warnings
