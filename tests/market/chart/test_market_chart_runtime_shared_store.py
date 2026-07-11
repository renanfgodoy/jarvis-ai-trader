from fastapi.testclient import TestClient

from app.main import app
from app.market.runtime import market_candle_store, market_chart_runtime_service, market_pipeline

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


def setup_function() -> None:
    market_candle_store.clear()


def test_pipeline_and_chart_runtime_share_the_same_store() -> None:
    assert market_pipeline.candle_store is market_candle_store

    result = market_pipeline.process(candle_generated_payload())
    series = market_chart_runtime_service.get_series(active_id=76, raw_size=60, limit=10)

    assert result.stored == 1
    assert len(series.candles) == 1
    assert series.candles[0].time == 1783721940


def test_write_then_read_through_http_route_uses_shared_store() -> None:
    market_pipeline.process(candle_generated_payload())

    response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["candles"][0]["time"] == 1783721940


def test_two_consecutive_reads_preserve_series() -> None:
    market_pipeline.process(candle_generated_payload())

    first = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10}).json()
    second = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10}).json()

    assert first == second
    assert second["count"] == 1


def test_shared_store_keeps_series_isolated_by_active_id_and_raw_size() -> None:
    market_pipeline.process(candle_generated_payload(active_id=76, raw_size=60, start_timestamp=100))
    market_pipeline.process(candle_generated_payload(active_id=2298, raw_size=60, start_timestamp=200))
    market_pipeline.process(candle_generated_payload(active_id=76, raw_size=300, start_timestamp=300))

    series_76_60 = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10}).json()
    series_2298_60 = client.get("/api/v1/market/chart", params={"active_id": 2298, "raw_size": 60, "limit": 10}).json()
    series_76_300 = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 300, "limit": 10}).json()

    assert [item["time"] for item in series_76_60["candles"]] == [100]
    assert [item["time"] for item in series_2298_60["candles"]] == [200]
    assert [item["time"] for item in series_76_300["candles"]] == [300]
