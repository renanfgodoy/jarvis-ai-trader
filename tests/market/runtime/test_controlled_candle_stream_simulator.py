import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.market.runtime import controlled_candle_stream_simulator, market_candle_store, market_pipeline

client = TestClient(app)


@pytest.fixture(autouse=True)
def simulator_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "environment", "test")
    controlled_candle_stream_simulator.stop()
    market_candle_store.clear()
    yield
    controlled_candle_stream_simulator.stop()
    market_candle_store.clear()


def start_payload(**overrides: object) -> dict:
    payload = {
        "active_id": 76,
        "raw_size": 60,
        "interval_seconds": 60,
        "tick_seconds": 1,
        "start_timestamp": 1_783_721_940,
        "start_price": 1.162275,
        "price_step": 0.00001,
    }
    payload.update(overrides)
    return payload


def test_simulator_updates_open_candle_with_same_start_timestamp() -> None:
    response = client.post("/api/v1/runtime/simulator/start", json=start_payload())
    assert response.status_code == 200

    first_series = market_candle_store.series(active_id=76, raw_size=60)
    controlled_candle_stream_simulator.advance()
    second_series = market_candle_store.series(active_id=76, raw_size=60)

    assert len(first_series) == 1
    assert len(second_series) == 1
    assert first_series[0].start_timestamp == second_series[0].start_timestamp
    assert first_series[0].close != second_series[0].close
    assert second_series[0].low_candidate <= second_series[0].close <= second_series[0].high_candidate


def test_simulator_closes_period_and_creates_next_candle() -> None:
    response = client.post("/api/v1/runtime/simulator/start", json=start_payload(tick_seconds=30))
    assert response.status_code == 200

    controlled_candle_stream_simulator.advance()

    series = market_candle_store.series(active_id=76, raw_size=60)
    assert [candle.start_timestamp for candle in series] == [1_783_721_940, 1_783_722_000]


def test_simulator_start_and_stop_are_idempotent() -> None:
    first_start = client.post("/api/v1/runtime/simulator/start", json=start_payload())
    second_start = client.post("/api/v1/runtime/simulator/start", json=start_payload(start_timestamp=200))
    first_stop = client.post("/api/v1/runtime/simulator/stop")
    second_stop = client.post("/api/v1/runtime/simulator/stop")

    assert first_start.status_code == 200
    assert second_start.status_code == 200
    assert first_start.json()["running"] is True
    assert second_start.json()["running"] is True
    assert second_start.json()["current_start_timestamp"] == 1_783_721_940
    assert first_stop.status_code == 200
    assert second_stop.status_code == 200
    assert second_stop.json()["running"] is False


def test_simulator_is_blocked_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "environment", "production")

    start_response = client.post("/api/v1/runtime/simulator/start", json=start_payload())
    status_response = client.get("/api/v1/runtime/simulator/status")
    stop_response = client.post("/api/v1/runtime/simulator/stop")

    assert start_response.status_code == 403
    assert status_response.status_code == 403
    assert stop_response.status_code == 403
    assert market_candle_store.series(active_id=76, raw_size=60) == ()


def test_simulator_uses_shared_market_pipeline() -> None:
    assert controlled_candle_stream_simulator.pipeline is market_pipeline

    response = client.post("/api/v1/runtime/simulator/start", json=start_payload())

    assert response.status_code == 200
    assert response.json()["last_pipeline_success"] is True
    assert len(market_candle_store.series(active_id=76, raw_size=60)) == 1


def test_chart_api_receives_simulated_new_candles_without_refresh() -> None:
    client.post("/api/v1/runtime/simulator/start", json=start_payload(tick_seconds=30))

    first_chart_response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10})
    controlled_candle_stream_simulator.advance()
    second_chart_response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10})

    assert first_chart_response.status_code == 200
    assert second_chart_response.status_code == 200
    assert first_chart_response.json()["count"] == 1
    assert second_chart_response.json()["count"] == 2
    assert [item["time"] for item in second_chart_response.json()["candles"]] == [1_783_721_940, 1_783_722_000]


def test_simulator_status_identifies_controlled_development_data() -> None:
    client.post("/api/v1/runtime/simulator/start", json=start_payload())

    response = client.get("/api/v1/runtime/simulator/status")

    assert response.status_code == 200
    assert response.json()["development_only"] is True
    assert response.json()["data_classification"] == "SIMULATED / CONTROLLED DEVELOPMENT DATA"
    assert "SIMULATED / CONTROLLED DEVELOPMENT DATA" in response.json()["warning"]
