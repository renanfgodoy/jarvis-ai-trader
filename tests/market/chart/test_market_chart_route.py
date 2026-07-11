from fastapi.testclient import TestClient

from app.main import app
from app.market.runtime import market_candle_store

client = TestClient(app)


def test_market_chart_route_returns_empty_series_from_store() -> None:
    market_candle_store.clear()

    response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 200})

    assert response.status_code == 200
    assert response.json() == {
        "active_id": 76,
        "raw_size": 60,
        "count": 0,
        "candles": [],
    }


def test_market_chart_route_validates_required_query_params() -> None:
    response = client.get("/api/v1/market/chart")

    assert response.status_code == 422
