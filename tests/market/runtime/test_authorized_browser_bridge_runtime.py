from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.market.runtime import authorized_browser_bridge_runtime, controlled_candle_stream_simulator, market_candle_store

client = TestClient(app)

BRIDGE_HEADERS = {
    "Content-Type": "application/json",
    "X-Friday-Trade-Bridge": "POLARIUM_AUTHORIZED_BROWSER",
}


def setup_function() -> None:
    controlled_candle_stream_simulator.stop()
    authorized_browser_bridge_runtime.reset()
    market_candle_store.clear()


def teardown_function() -> None:
    controlled_candle_stream_simulator.stop()
    authorized_browser_bridge_runtime.reset()
    market_candle_store.clear()


def candle_generated_payload(**overrides):
    body = {
        "active_id": 76,
        "size": 60,
        "from": 1_783_721_940,
        "to": 1_783_722_000,
        "open": 1.16227,
        "close": 1.16231,
        "min": 1.1622,
        "max": 1.16235,
        "volume": 0,
    }
    body.update(overrides)
    return {
        "event_name": "candle-generated",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "payload": {"name": "candle-generated", "msg": {"body": body}},
    }


def first_candles_payload():
    return {
        "event_name": "first-candles",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "payload": {
            "name": "first-candles",
            "msg": {
                "body": {
                    "active_id": 76,
                    "candles_by_size": {
                        "60": {
                            "from": 1_783_721_880,
                            "to": 1_783_721_940,
                            "open": 1.1621,
                            "close": 1.1622,
                            "min": 1.162,
                            "max": 1.1623,
                            "volume": 0,
                        }
                    },
                }
            },
        },
    }


def post_bridge(payload):
    return client.post("/api/v1/polarium/browser-bridge/message", json=payload, headers=BRIDGE_HEADERS)


def test_bridge_accepts_candle_generated_and_updates_chart_api() -> None:
    response = post_bridge(candle_generated_payload())

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["stored"] == 1

    chart = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60})
    assert chart.status_code == 200
    assert chart.json()["count"] == 1
    assert chart.json()["candles"][0]["close"] == 1.16231


def test_bridge_adapts_real_candle_generated_msg_shape_to_pipeline_and_chart_api() -> None:
    response = post_bridge(
        {
            "event_name": "candle-generated",
            "source": "POLARIUM_AUTHORIZED_BROWSER",
            "payload": {
                "name": "candle-generated",
                "msg": {
                    "active_id": 76,
                    "size": 60,
                    "id": 123456789,
                    "from": 1_783_721_940,
                    "to": 1_783_722_000,
                    "open": 1.16227,
                    "close": 1.16231,
                    "min": 1.16220,
                    "max": 1.16235,
                    "volume": 0,
                    "phase": "T",
                },
            },
        }
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["pipeline_success"] is True

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    assert status["pipeline_success_count"] == 1
    assert status["active_ids_seen"] == [76]
    assert status["raw_sizes_seen"] == [60]

    chart = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60})
    assert chart.status_code == 200
    assert chart.json()["count"] == 1
    assert chart.json()["candles"][0]["close"] == 1.16231


def test_bridge_status_traces_full_pipeline_path_for_real_payload_shape() -> None:
    response = post_bridge(
        {
            "event_name": "candle-generated",
            "source": "POLARIUM_AUTHORIZED_BROWSER",
            "payload": {
                "name": "candle-generated",
                "msg": {
                    "active_id": 76,
                    "size": 60,
                    "from": 1_783_721_940,
                    "to": 1_783_722_000,
                    "open": 1.16227,
                    "close": 1.16231,
                    "min": 1.16220,
                    "max": 1.16235,
                },
            },
        }
    )
    assert response.status_code == 200

    trace = client.get("/api/v1/polarium/browser-bridge/status").json()["last_trace"]

    assert trace["event_received"]["event_name"] == "candle-generated"
    assert trace["adapter_accepted"] is True
    assert trace["payload_converted"]["msg"]["body"]["active_id"] == 76
    assert trace["pipeline_input"]["msg"]["body"]["size"] == 60
    assert trace["pipeline_result"]["success"] is True
    assert trace["pipeline_result"]["stored"] == 1
    assert trace["rejection_reason"] is None
    assert trace["candle_store"]["received_candles"] == 1
    assert trace["candle_store"]["saved_candles"][0]["series_count_after"] == 1
    assert trace["chart_api_probe"]["count"] == 1
    assert trace["chart_api_probe"]["latest"]["close"] == 1.16231
    assert trace["payload_comparison"]["sent_to_pipeline"]["msg"]["body"]["from"] == 1_783_721_940
    assert trace["payload_comparison"]["saved"][0]["close"] == 1.16231


def test_bridge_status_traces_pipeline_rejection_reason() -> None:
    response = post_bridge({"event_name": "candles-generated", "payload": {"name": "candles-generated", "msg": {"body": {"active_id": 76}}}})
    assert response.status_code == 200

    trace = client.get("/api/v1/polarium/browser-bridge/status").json()["last_trace"]

    assert trace["event_received"]["event_name"] == "candles-generated"
    assert trace["adapter_accepted"] is True
    assert trace["pipeline_result"]["success"] is False
    assert trace["pipeline_result"]["route_status"] == "unsupported"
    assert trace["rejection_reason"] in {"event_not_parsed", "unsupported_event", "PIPELINE_REJECTED"}
    assert trace["candle_store"]["received_candles"] == 0
    assert trace["chart_api_probe"] is None


def test_bridge_accepts_first_candles() -> None:
    response = post_bridge(first_candles_payload())

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["stored"] == 1


def test_bridge_accepts_timesync_without_writing_to_store() -> None:
    response = post_bridge({"event_name": "timeSync", "payload": {"name": "timeSync", "msg": 123}})

    assert response.status_code == 200
    assert response.json()["pipeline_success"] is None
    assert market_candle_store.series(76, 60) == ()


def test_bridge_accepts_allowlisted_candles_generated_without_parser_contract() -> None:
    response = post_bridge({"event_name": "candles-generated", "payload": {"name": "candles-generated", "msg": {"body": {"active_id": 76}}}})

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["pipeline_success"] is False
    assert response.json()["error_code"] == "PIPELINE_REJECTED"


def test_bridge_requires_local_header() -> None:
    response = client.post("/api/v1/polarium/browser-bridge/message", json=candle_generated_payload())

    assert response.status_code == 403


def test_bridge_rejects_authenticate_and_authenticated_events() -> None:
    for event_name in ["authenticate", "authenticated"]:
        response = post_bridge({"event_name": event_name, "payload": {"name": event_name}})
        assert response.status_code == 400
        assert response.json()["detail"]["error_code"] == "EVENT_BLOCKED"


def test_bridge_rejects_sensitive_nested_fields() -> None:
    sensitive_payloads = [
        {"event_name": "candle-generated", "payload": {"name": "candle-generated", "msg": {"body": {"token": "value"}}}},
        {"event_name": "candle-generated", "payload": {"name": "candle-generated", "msg": {"body": {"cookie": "value"}}}},
        {"event_name": "candle-generated", "payload": {"name": "candle-generated", "msg": {"body": {"Authorization": "value"}}}},
        {"event_name": "candle-generated", "payload": {"name": "candle-generated", "msg": {"body": {"note": "Bearer value"}}}},
        {"event_name": "candle-generated", "payload": {"name": "candle-generated", "msg": {"body": {"ssid": "value"}}}},
    ]

    for payload in sensitive_payloads:
        response = post_bridge(payload)
        assert response.status_code == 400
        assert response.json()["detail"]["error_code"] == "SENSITIVE_FIELD_REJECTED"


def test_bridge_rejects_account_execution_and_unlisted_events() -> None:
    for event_name in ["balances", "portfolio", "orders", "execution", "digital-option-client-price-generated"]:
        response = post_bridge({"event_name": event_name, "payload": {"name": event_name}})
        assert response.status_code == 400


def test_bridge_rejects_large_payload() -> None:
    response = post_bridge({"event_name": "timeSync", "payload": {"name": "timeSync", "blob": "x" * 70_000}})

    assert response.status_code == 413
    assert response.json()["detail"]["error_code"] == "PAYLOAD_TOO_LARGE"


def test_bridge_status_is_sanitized() -> None:
    post_bridge(candle_generated_payload())

    response = client.get("/api/v1/polarium/browser-bridge/status")

    assert response.status_code == 200
    data = response.json()
    assert data["bridge_active"] is True
    assert data["source"] == "POLARIUM_AUTHORIZED_BROWSER"
    assert data["data_classification"] == "POLARIUM AUTHORIZED BROWSER LIVE"
    serialized = str(data).lower()
    for marker in ["token", "cookie", "authorization", "bearer", "ssid", "password", "headers", "'har':", '"har":']:
        assert marker not in serialized


def test_bridge_stops_simulator_before_accepting_real_message() -> None:
    start = client.post("/api/v1/runtime/simulator/start")
    assert start.status_code == 200
    assert start.json()["running"] is True

    response = post_bridge(candle_generated_payload(from_=1_783_722_000))

    assert response.status_code == 200
    assert controlled_candle_stream_simulator.is_running is False


def test_simulator_is_blocked_when_bridge_is_active() -> None:
    response = post_bridge(candle_generated_payload())
    assert response.status_code == 200

    simulator = client.post("/api/v1/runtime/simulator/start")

    assert simulator.status_code == 409
