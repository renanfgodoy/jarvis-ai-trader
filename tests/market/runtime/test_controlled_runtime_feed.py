import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.market.runtime import market_candle_store

client = TestClient(app)


def candle_generated_payload(
    *,
    active_id: int = 76,
    raw_size: int = 60,
    start_timestamp: int = 1783721940,
    close: float = 1.162145,
) -> dict:
    return {
        "name": "candle-generated",
        "msg": {
            "body": {
                "active_id": active_id,
                "size": raw_size,
                "from": start_timestamp,
                "to": start_timestamp + raw_size,
                "open": 1.162275,
                "close": close,
                "min": 1.162145,
                "max": 1.162395,
                "volume": 0,
            }
        },
    }


def first_candles_payload() -> dict:
    return {
        "request_id": "80",
        "name": "first-candles",
        "status": 2000,
        "msg": {
            "body": {
                "active_id": 76,
                "candles_by_size": {
                    "60": {
                        "from": 1778475660,
                        "to": 1778475720,
                        "open": 1.201705,
                        "close": 1.201425,
                        "min": 1.201405,
                        "max": 1.201825,
                        "volume": 0,
                    },
                    "300": {
                        "from": 1757739900,
                        "to": 1757740200,
                        "open": 1.138605,
                        "close": 1.138015,
                        "min": 1.137295,
                        "max": 1.139265,
                        "volume": 0,
                    },
                },
            }
        },
    }


@pytest.fixture(autouse=True)
def runtime_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "environment", "test")
    market_candle_store.clear()


@pytest.mark.parametrize("environment", ["development", "test"])
def test_runtime_feed_is_available_in_development_and_test(monkeypatch: pytest.MonkeyPatch, environment: str) -> None:
    monkeypatch.setattr(settings, "environment", environment)

    response = client.post("/api/v1/runtime/feed", json=candle_generated_payload())

    assert response.status_code == 200
    assert response.json()["stored"] == 1


def test_runtime_feed_is_blocked_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "environment", "production")

    response = client.post("/api/v1/runtime/feed", json=candle_generated_payload())

    assert response.status_code == 403
    assert "disabled in production" in response.json()["detail"]
    assert market_candle_store.series(active_id=76, raw_size=60) == ()


def test_runtime_feed_pipeline_empty_message_is_rejected() -> None:
    response = client.post("/api/v1/runtime/feed", json={})

    assert response.status_code == 400
    assert "sanitized JSON object" in response.json()["detail"][0]


def test_runtime_feed_accepts_candle_generated() -> None:
    response = client.post("/api/v1/runtime/feed", json=candle_generated_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["event_name"] == "candle-generated"
    assert data["stored"] == 1


def test_runtime_feed_accepts_first_candles() -> None:
    response = client.post("/api/v1/runtime/feed", json=first_candles_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["event_name"] == "first-candles"
    assert data["processed"] == 2
    assert data["stored"] == 2


def test_runtime_feed_reports_duplicate_candle() -> None:
    payload = candle_generated_payload()

    client.post("/api/v1/runtime/feed", json=payload)
    response = client.post("/api/v1/runtime/feed", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["ignored"] == 1
    assert data["stored"] == 0


def test_runtime_feed_returns_structured_error_for_invalid_event() -> None:
    payload = candle_generated_payload()
    del payload["msg"]["body"]["open"]

    response = client.post("/api/v1/runtime/feed", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["errors"]


def test_runtime_feed_updates_candle_store() -> None:
    client.post("/api/v1/runtime/feed", json=candle_generated_payload())

    series = market_candle_store.series(active_id=76, raw_size=60)

    assert len(series) == 1
    assert series[0].start_timestamp == 1783721940


def test_chart_api_reflects_runtime_feed_store() -> None:
    client.post("/api/v1/runtime/feed", json=candle_generated_payload())

    response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10})

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["candles"][0]["time"] == 1783721940


def test_two_consecutive_runtime_feed_calls_preserve_store() -> None:
    client.post("/api/v1/runtime/feed", json=candle_generated_payload(start_timestamp=100))
    client.post("/api/v1/runtime/feed", json=candle_generated_payload(start_timestamp=200))

    response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10})

    assert [item["time"] for item in response.json()["candles"]] == [100, 200]


def test_runtime_feed_rejects_raw_har_payload() -> None:
    response = client.post("/api/v1/runtime/feed", json={"log": {"entries": []}})

    assert response.status_code == 400
    assert "HAR" in response.json()["detail"][0]


def test_runtime_feed_rejects_sensitive_fields() -> None:
    response = client.post("/api/v1/runtime/feed", json={"name": "candle-generated", "headers": {"Authorization": "Bearer x"}})

    assert response.status_code == 400
    assert "Sensitive" in response.json()["detail"][0]
