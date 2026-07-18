from fastapi.testclient import TestClient

from app.main import app
from app.market.events.models import NormalizedMarketCandle
from app.market.runtime import chart_bucket_consistency_diagnostic, market_candle_store

client = TestClient(app)


def setup_function() -> None:
    market_candle_store.clear()
    chart_bucket_consistency_diagnostic.clear()


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


def test_market_chart_route_returns_empty_series_from_store() -> None:
    response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 200})

    assert response.status_code == 200
    assert response.json() == {
        "provider": "POLARIUM",
        "active_id": 76,
        "symbol": None,
        "raw_size": 60,
        "count": 0,
        "candles": [],
    }


def test_market_chart_route_validates_required_query_params() -> None:
    response = client.get("/api/v1/market/chart")

    assert response.status_code == 422


def test_market_chart_series_route_returns_available_store_series() -> None:
    market_candle_store.add(make_candle(100, active_id=76, raw_size=60, symbol="EUR/USD OTC"))
    market_candle_store.add(make_candle(200, active_id=76, raw_size=60))
    market_candle_store.add(make_candle(300, active_id=2298, raw_size=300, symbol="BTC/USD"))

    response = client.get("/api/v1/market/chart/series")

    assert response.status_code == 200
    assert response.json() == {
        "series": [
            {"provider": "POLARIUM", "active_id": 76, "symbol": "EUR/USD OTC", "raw_size": 60, "count": 2, "latest_time": 200},
            {"provider": "POLARIUM", "active_id": 2298, "symbol": "BTC/USD", "raw_size": 300, "count": 1, "latest_time": 300},
        ]
    }


def test_market_chart_route_returns_observed_symbol_for_selected_series() -> None:
    market_candle_store.add(make_candle(100, active_id=76, raw_size=60, symbol="EUR/USD OTC"))

    response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 200})

    assert response.status_code == 200
    assert response.json()["symbol"] == "EUR/USD OTC"


def test_market_chart_route_preserves_explicit_active_id_and_raw_size() -> None:
    market_candle_store.add(make_candle(100, active_id=76, raw_size=300, symbol="EURUSD-OTC"))
    market_candle_store.add(make_candle(200, active_id=1857, raw_size=300, symbol="XAUUSD-OTC"))
    market_candle_store.add(make_candle(300, active_id=2298, raw_size=300, symbol="USDBRL-OTC"))

    for active_id, expected_time in [(76, 100), (1857, 200), (2298, 300)]:
        response = client.get("/api/v1/market/chart", params={"active_id": active_id, "raw_size": 300, "limit": 200})

        assert response.status_code == 200
        payload = response.json()
        assert payload["active_id"] == active_id
        assert payload["raw_size"] == 300
        assert payload["count"] == 1
        assert payload["candles"][0]["time"] == expected_time


def test_market_chart_route_reports_missing_bucket_without_reusing_previous_series() -> None:
    market_candle_store.add(make_candle(100, active_id=76, raw_size=300, symbol="EURUSD-OTC"))

    response = client.get("/api/v1/market/chart", params={"active_id": 1857, "raw_size": 300, "limit": 200})

    assert response.status_code == 200
    assert response.json() == {
        "provider": "POLARIUM",
        "active_id": 1857,
        "symbol": None,
        "raw_size": 300,
        "count": 0,
        "candles": [],
    }
    records = chart_bucket_consistency_diagnostic.records()
    assert any(record.event == "CHART_BUCKET_MISSING" and record.store_key == "POLARIUM:1857:300" for record in records)


def test_market_chart_route_diagnostic_response_matches_requested_bucket() -> None:
    market_candle_store.add(make_candle(100, active_id=1857, raw_size=300, symbol="XAUUSD-OTC"))

    response = client.get("/api/v1/market/chart", params={"active_id": 1857, "raw_size": 300, "limit": 200})

    assert response.status_code == 200
    response_records = [record for record in chart_bucket_consistency_diagnostic.records() if record.event == "CHART_RESPONSE_CREATED"]
    latest = response_records[-1]
    assert latest.active_id_requested == 1857
    assert latest.raw_size_requested == 300
    assert latest.store_key == "POLARIUM:1857:300"
    assert latest.response_active_id == 1857
    assert latest.response_raw_size == 300
    assert latest.response_count == 1
    assert latest.first_timestamp == 100
    assert latest.last_timestamp == 100
