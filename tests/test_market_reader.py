from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.models.candle import Candle
from app.services.market_reader import MarketReaderService

client = TestClient(app)


def test_market_reader_returns_candles() -> None:
    service = MarketReaderService()

    candles = service.get_candles(symbol="eurusd-otc", timeframe="M1", limit=10)

    assert len(candles) == 10
    assert all(isinstance(candle, Candle) for candle in candles)
    assert candles[-1].symbol == "EURUSD-OTC"


def test_market_snapshot_endpoint() -> None:
    response = client.get("/api/v1/market/snapshot?symbol=EURUSD-OTC&timeframe=M1&limit=5")

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "simulated"
    assert data["symbol"] == "EURUSD-OTC"
    assert data["timeframe"] == "M1"
    assert data["candles_count"] == 5
    assert "last_candle" in data


def test_market_candles_endpoint() -> None:
    response = client.get("/api/v1/market/candles?symbol=GBPUSD-OTC&timeframe=M1&limit=3")

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "simulated"
    assert data["symbol"] == "GBPUSD-OTC"
    assert data["count"] == 3
    assert len(data["candles"]) == 3
    assert "Dados simulados" in data["disclaimer"]


def test_invalid_limit_in_service() -> None:
    service = MarketReaderService()

    with pytest.raises(ValueError):
        service.get_candles(symbol="EURUSD-OTC", timeframe="M1", limit=0)
