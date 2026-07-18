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
        "diagnostic": {
            "event_name": "first-candles",
            "direction": "server_to_client",
            "top_level_type": "object",
            "top_level_keys": ["name", "msg"],
            "msg_type": "object",
            "msg_keys": ["body"],
            "body_type": "object",
            "body_keys": ["active_id", "candles_by_size"],
            "candidate_collection_path": "msg.body.candles_by_size",
            "candidate_collection_length": 1,
            "received_at": 100,
            "relay_ready_at": 90,
            "websocket_created_at": 80,
        },
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


def first_candles_multi_timeframe_snapshot_without_active_id(count: int = 19):
    sizes = [1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000]
    return {
        "event_name": "first-candles",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "diagnostic": {
            "event_name": "first-candles",
            "direction": "server_to_client",
            "top_level_type": "object",
            "top_level_keys": ["request_id", "name", "msg", "status"],
            "msg_type": "object",
            "msg_keys": ["candles_by_size"],
            "body_type": "null",
            "body_keys": [],
            "candidate_collection_path": "msg.candles_by_size",
            "candidate_collection_length": count,
            "received_at": 100,
            "relay_ready_at": 90,
            "websocket_created_at": 80,
        },
        "discovery": {
            "direction": "server_to_client",
            "event_name": "first-candles",
            "request_ref": "request-1",
            "request_id_present": True,
            "top_level_keys": ["request_id", "name", "msg", "status"],
            "msg_keys": ["candles_by_size"],
            "body_keys": [],
            "collection_path": "msg.candles_by_size",
            "collection_length": count,
            "distinct_timestamps": count,
            "distinct_raw_sizes": count,
            "distinct_active_ids": 0,
            "historical_series_confirmed": False,
        },
        "payload": {
            "name": "first-candles",
            "status": 2000,
            "msg": {
                "candles_by_size": {
                    str(size): {
                        "from": 1_783_720_000 + index,
                        "to": 1_783_720_060 + index,
                        "open": 1.1,
                        "close": 1.2,
                        "min": 1.0,
                        "max": 1.3,
                    }
                    for index, size in enumerate(sizes[:count])
                }
            },
        },
    }


def historical_series_candidate_payload(count: int = 100):
    return {
        "event_name": "candles",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "discovery": {
            "direction": "server_to_client",
            "event_name": "candles",
            "request_ref": "request-3",
            "request_id_present": True,
            "top_level_keys": ["name", "msg"],
            "msg_keys": ["active_id", "size", "candles"],
            "body_keys": [],
            "collection_path": "msg.candles",
            "collection_length": count,
            "distinct_timestamps": count,
            "distinct_raw_sizes": 1,
            "distinct_active_ids": 1,
            "historical_series_confirmed": True,
        },
        "payload": {"name": "candles", "msg": {"active_id": 76, "size": 60}},
    }


def candles_generated_array_payload(count: int = 100):
    return {
        "event_name": "candles-generated",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "candles_generated_diagnostic": {
            "seen_main": 1,
            "relayed": 1,
            "top_level_type": "object",
            "top_level_keys": ["name", "msg"],
            "msg_type": "object",
            "msg_keys": ["result"],
            "body_type": "null",
            "body_keys": [],
            "nested_array_paths": ["msg.result.candles"],
            "nested_object_paths": ["msg", "msg.result"],
            "candidate_collection_path": "msg.result.candles",
            "candidate_collection_type": "array",
            "candidate_collection_length": count,
            "distinct_timestamps": count,
            "distinct_raw_sizes": 1,
            "distinct_active_ids": 1,
            "request_ref": "request-7",
            "direction": "server_to_client",
            "received_at": 123,
            "historical_series_confirmed": True,
        },
        "payload": {
            "name": "candles-generated",
            "msg": {
                "result": {
                    "active_id": 76,
                    "size": 60,
                    "candles": [
                        {
                            "from": 1_783_720_000 + index * 60,
                            "to": 1_783_720_060 + index * 60,
                            "open": 1.1,
                            "close": 1.2,
                            "min": 1.0,
                            "max": 1.3,
                        }
                        for index in range(count)
                    ],
                }
            },
        },
    }


def candles_generated_indexed_payload(count: int = 20):
    return {
        "event_name": "candles-generated",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "payload": {
            "name": "candles-generated",
            "msg": {
                "data": {
                    "active_id": 76,
                    "size": 60,
                    "items": {
                        str(1_783_720_000 + index * 60): {
                            "from": 1_783_720_000 + index * 60,
                            "to": 1_783_720_060 + index * 60,
                            "open": 1.1,
                            "close": 1.2,
                        }
                        for index in range(count)
                    },
                }
            },
        },
    }


def outbound_send_message_payload(**body_overrides):
    body = {
        "name": "get-candles",
        "active_id": 76,
        "size": 60,
        "count": 100,
        "from": 1_783_720_000,
        "to": 1_783_726_000,
        "limit": 100,
    }
    body.update(body_overrides)
    numeric_fields = sorted(key for key, value in body.items() if isinstance(value, (int, float)) and not isinstance(value, bool))
    string_fields = sorted(key for key, value in body.items() if isinstance(value, str))
    return {
        "event_name": "sendMessage",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "outbound_candle_request_diagnostic": {
            "seen_main": 1,
            "relayed": 1,
            "event_name": "sendMessage",
            "inner_event_name": "get-candles",
            "direction": "client_to_server",
            "top_level_type": "object",
            "top_level_keys": ["name", "msg"],
            "msg_type": "object",
            "msg_keys": ["body"],
            "body_type": "object",
            "body_keys": list(body.keys()),
            "has_active_id": "active_id" in body,
            "has_size": "size" in body,
            "has_count": "count" in body,
            "has_from": "from" in body,
            "has_to": "to" in body,
            "has_limit": "limit" in body,
            "has_offset": "offset" in body,
            "has_chunk_size": "chunk_size" in body or "chunkSize" in body,
            "numeric_field_names": numeric_fields,
            "string_field_names": string_fields,
            "array_paths": [],
            "object_paths": ["msg", "msg.body"],
            "request_ref": "request-9",
            "correlation_status": "CONFIRMED_BY_REQUEST_ID",
            "received_at": 456,
        },
        "payload": {"name": "sendMessage", "msg": {"body": body}},
    }


def historical_transport_payload(
    *,
    transport: str = "fetch_response",
    timestamp_count: int = 20,
    active_id_count: int = 1,
    raw_size_count: int = 1,
    method: str = "GET",
    host: str = "trade.polariumbroker.com",
    path: str = "/api/candles/:id",
    status_code: int | None = 200,
    content_type: str | None = "application/json",
    last_error_code: str | None = None,
):
    return {
        "event_name": "historical-transport-discovery",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "payload": {"name": "historical-transport-discovery"},
        "historical_transport_discovery": {
            "fetch_requests_seen": 1 if transport == "fetch_request" else 0,
            "fetch_responses_seen": 1 if transport == "fetch_response" else 0,
            "xhr_requests_seen": 1 if transport == "xhr_request" else 0,
            "xhr_responses_seen": 1 if transport == "xhr_response" else 0,
            "websocket_candidates_seen": 1 if transport == "websocket" else 0,
            "last_transport": transport,
            "last_method": method,
            "last_url_host": host,
            "last_url_path_sanitized": path,
            "last_status_code": status_code,
            "last_content_type": content_type,
            "candidate_collection_path": "data.candles",
            "candidate_collection_type": "array",
            "candidate_collection_length": timestamp_count,
            "distinct_timestamps": timestamp_count,
            "distinct_raw_sizes": raw_size_count,
            "distinct_active_ids": active_id_count,
            "historical_request_ref": "request-1",
            "page_bridge_installed_at": 10,
            "fetch_interceptor_installed_at": 20,
            "xhr_interceptor_installed_at": 30,
            "websocket_created_at": 40,
            "first_historical_candidate_at": 50,
            "last_error_code": last_error_code,
            "top_level_type": "object",
            "top_level_keys": ["data", "meta"],
            "nested_array_paths": ["data.candles"],
            "nested_object_paths": ["data"],
        },
    }


def runtime_store_discovery_payload(**overrides):
    discovery = {
        "scan_started_at": 10,
        "scan_completed_at": 30,
        "scan_duration_ms": 20,
        "window_globals_scanned": 40,
        "react_nodes_scanned": 12,
        "redux_candidates": 1,
        "mobx_candidates": 1,
        "zustand_candidates": 1,
        "chart_engine_candidates": 1,
        "datafeed_candidates": 1,
        "storage_candidates": 2,
        "worker_candidates": 1,
        "candidate_found": True,
        "candidate_type": "chart_engine",
        "candidate_ref": "runtime_candidate_1",
        "candidate_path": "window.chart.cache.series",
        "candidate_collection_type": "array",
        "candidate_collection_length": 20,
        "candidate_distinct_timestamps": 20,
        "candidate_distinct_raw_sizes": 1,
        "candidate_distinct_active_ids": 1,
        "candidate_readable_passively": True,
        "last_error_code": None,
    }
    discovery.update(overrides)
    return {
        "event_name": "runtime-store-discovery",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "payload": {"name": "runtime-store-discovery"},
        "runtime_store_discovery": discovery,
        "runtime_store_candidates": [
            {
                "candidate_ref": "runtime_candidate_1",
                "source_type": "chart_engine",
                "name_sanitized": "chartCache",
                "path_sanitized": "window.chart.cache.series",
                "object_type": "object",
                "top_level_keys": ["series", "active_id", "size"],
                "method_names": ["setData", "update"],
                "array_paths": ["series.candles"],
                "object_paths": ["series"],
                "collection_length": 20,
                "distinct_timestamps": 20,
                "distinct_raw_sizes": 1,
                "distinct_active_ids": 1,
                "readable_passively": True,
                "occurrences": 1,
            }
        ],
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

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    assert status["symbol_found"] is False
    assert status["symbol_source"] is None


def test_bridge_status_exposes_sanitized_latency_audit_for_pipeline_event() -> None:
    response = post_bridge(candle_generated_payload())

    assert response.status_code == 200

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    latest = status["latency_audit"]["latest"]
    segments = status["latency_audit"]["segments"]
    trace = status["last_trace"]

    assert status["latency_audit"]["sample_count"] == 1
    assert latest["event_name"] == "candle-generated"
    assert latest["pipeline_processed"] is True
    assert latest["backend_total_ms"] >= 0
    assert segments["backend_total_ms"]["p50_ms"] is not None
    assert "t0_event_received_ms" in trace["latency_timeline"]
    assert "runtime_to_store_ms" in trace["latency_segments_ms"]
    assert "token" not in str(status["latency_audit"]).lower()
    assert "cookie" not in str(status["latency_audit"]).lower()


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


def test_bridge_preserves_observed_symbol_through_pipeline_store_and_chart_api() -> None:
    payload = candle_generated_payload(symbol="EUR/USD OTC")

    response = post_bridge(payload)
    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    chart = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60})

    assert response.status_code == 200
    assert response.json()["pipeline_success"] is True
    assert status["symbol_found"] is True
    assert status["symbol_source"] == "polarium_observed_payload"
    assert status["current_symbol"] == "EUR/USD OTC"
    assert chart.status_code == 200
    assert chart.json()["symbol"] == "EUR/USD OTC"


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


def test_first_candles_historical_diagnostic_tracks_each_stage() -> None:
    response = post_bridge(first_candles_payload())
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_diagnostic"]

    assert diagnostic["first_candles_seen_main"] == 1
    assert diagnostic["first_candles_relayed"] == 1
    assert diagnostic["first_candles_received_backend"] == 1
    assert diagnostic["first_candles_adapter_accepted"] == 1
    assert diagnostic["first_candles_parsed"] == 1
    assert diagnostic["first_candles_stored"] == 1
    assert diagnostic["first_candles_collection_count"] == 1
    assert diagnostic["first_candles_last_error_code"] is None


def test_first_candles_historical_diagnostic_is_sanitized_without_payload_contents() -> None:
    response = post_bridge(first_candles_payload())
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_diagnostic"]
    serialized = str(diagnostic).lower()

    assert diagnostic["candidate_collection_path"] == "msg.body.candles_by_size"
    assert diagnostic["candidate_collection_length"] == 1
    for forbidden in ["1.162", "token", "cookie", "authorization", "bearer", "ssid", "headers", "har"]:
        assert forbidden not in serialized


def test_first_candles_historical_diagnostic_preserves_temporal_order_metadata() -> None:
    post_bridge(first_candles_payload())

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_diagnostic"]

    assert diagnostic["websocket_created_at"] == 80
    assert diagnostic["relay_ready_at"] == 90
    assert diagnostic["received_at"] == 100
    assert diagnostic["websocket_created_at"] < diagnostic["relay_ready_at"] < diagnostic["received_at"]


def test_first_candles_large_collection_exposes_only_length() -> None:
    payload = first_candles_payload()
    payload["diagnostic"]["candidate_collection_path"] = "msg.body.candles"
    payload["diagnostic"]["candidate_collection_length"] = 200
    payload["diagnostic"]["body_keys"] = ["active_id", "size", "candles"]
    payload["payload"]["msg"]["body"] = {
        "active_id": 76,
        "size": 60,
        "candles": [
            {
                "from": 1_783_720_000 + index * 60,
                "to": 1_783_720_060 + index * 60,
                "open": 1.1,
                "close": 1.2,
                "min": 1.0,
                "max": 1.3,
            }
            for index in range(200)
        ],
    }

    response = post_bridge(payload)
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_diagnostic"]
    assert diagnostic["candidate_collection_length"] == 200
    assert "candles" in diagnostic["body_keys"]
    assert "open" not in diagnostic


def test_first_candles_relayed_but_rejected_by_adapter_path_is_reported() -> None:
    payload = first_candles_payload()
    payload["payload"] = {"name": "first-candles", "msg": {"body": {"unexpected": True}}}
    payload["diagnostic"]["candidate_collection_path"] = None
    payload["diagnostic"]["candidate_collection_length"] = None

    response = post_bridge(payload)
    assert response.status_code == 200

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    diagnostic = status["historical_diagnostic"]

    assert diagnostic["first_candles_relayed"] == 1
    assert diagnostic["first_candles_adapter_accepted"] == 1
    assert diagnostic["first_candles_parsed"] == 0
    assert diagnostic["first_candles_stored"] == 0
    assert diagnostic["first_candles_last_error_code"] == "missing_candles_collection"


def test_first_candles_diagnostic_does_not_store_time_sync_or_unknown_frames() -> None:
    unknown = post_bridge({"event_name": "unknown-frame", "payload": {"name": "unknown-frame"}})
    assert unknown.status_code == 400

    timesync = post_bridge({"event_name": "timeSync", "payload": {"name": "timeSync", "msg": 123}})
    assert timesync.status_code == 200

    assert market_candle_store.series(76, 60) == ()


def test_candles_by_size_snapshot_is_not_classified_as_historical_series() -> None:
    response = post_bridge(first_candles_multi_timeframe_snapshot_without_active_id())

    assert response.status_code == 200
    assert response.json()["pipeline_success"] is False
    assert response.json()["stored"] == 0

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    diagnostic = status["historical_diagnostic"]
    discovery = status["historical_series_discovery"]

    assert diagnostic["parsed_count"] == 19
    assert diagnostic["valid_count"] == 19
    assert diagnostic["rejected_count"] == 19
    assert diagnostic["stored_count"] == 0
    assert diagnostic["route_status"] == "parsed"
    assert diagnostic["pipeline_success"] is False
    assert diagnostic["first_candles_last_error_code"] == "Candle requires provider-native active_id or symbol to be stored."
    assert diagnostic["distinct_active_ids"] == []
    assert diagnostic["distinct_raw_sizes"] == [1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000]
    assert discovery["last_collection_path"] == "msg.candles_by_size"
    assert discovery["last_collection_length"] == 19
    assert discovery["last_distinct_raw_sizes"] == 19
    assert discovery["historical_series_confirmed"] is False


def test_single_raw_size_collection_with_100_timestamps_is_classified_as_historical_candidate_without_store_write() -> None:
    response = post_bridge(historical_series_candidate_payload(100))

    assert response.status_code == 200
    assert response.json()["pipeline_success"] is None
    assert market_candle_store.series(76, 60) == ()

    discovery = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_series_discovery"]

    assert discovery["candidate_responses_seen"] == 1
    assert discovery["last_response_event_name"] == "candles"
    assert discovery["last_collection_path"] == "msg.candles"
    assert discovery["last_collection_length"] == 100
    assert discovery["last_distinct_timestamps"] == 100
    assert discovery["last_distinct_raw_sizes"] == 1
    assert discovery["last_distinct_active_ids"] == 1
    assert discovery["historical_series_confirmed"] is True
    assert discovery["historical_series_event_name"] == "candles"
    assert discovery["historical_series_request_ref"] == "request-3"


def test_historical_request_response_correlation_uses_sanitized_request_ref() -> None:
    request = post_bridge(
        {
            "event_name": "get-first-candles",
            "source": "POLARIUM_AUTHORIZED_BROWSER",
            "discovery": {
                "direction": "client_to_server",
                "event_name": "get-first-candles",
                "request_ref": "request-3",
                "request_id_present": True,
                "top_level_keys": ["name", "msg"],
                "msg_keys": ["active_id", "size", "count"],
                "body_keys": [],
                "collection_path": None,
                "collection_length": None,
                "distinct_timestamps": 0,
                "distinct_raw_sizes": 1,
                "distinct_active_ids": 1,
                "historical_series_confirmed": False,
            },
            "payload": {"name": "get-first-candles", "msg": {"active_id": 76, "size": 60, "count": 100}},
        }
    )
    response = post_bridge(historical_series_candidate_payload(100))

    assert request.status_code == 200
    assert response.status_code == 200

    discovery = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_series_discovery"]
    serialized = str(discovery).lower()

    assert discovery["candidate_requests_seen"] == 1
    assert discovery["candidate_responses_seen"] == 1
    assert discovery["last_request_event_name"] == "get-first-candles"
    assert discovery["historical_series_request_ref"] == "request-3"
    assert "raw-request-id" not in serialized


def test_historical_series_discovery_exposes_no_ohlc_or_sensitive_markers() -> None:
    response = post_bridge(historical_series_candidate_payload(100))
    assert response.status_code == 200

    discovery = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_series_discovery"]
    serialized = str(discovery).lower()

    for forbidden in ["open", "close", "min", "max", "1.1", "1.2", "token", "cookie", "authorization", "bearer", "ssid", "headers", "har"]:
        assert forbidden not in serialized


def test_candles_generated_diagnostic_discovers_nested_array_collection() -> None:
    response = post_bridge(candles_generated_array_payload(100))
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["candles_generated_diagnostic"]

    assert diagnostic["seen_main"] == 1
    assert diagnostic["relayed"] == 1
    assert diagnostic["received_backend"] == 1
    assert diagnostic["top_level_type"] == "object"
    assert diagnostic["top_level_keys"] == ["name", "msg"]
    assert diagnostic["msg_type"] == "object"
    assert diagnostic["msg_keys"] == ["result"]
    assert "msg.result.candles" in diagnostic["nested_array_paths"]
    assert diagnostic["candidate_collection_path"] == "msg.result.candles"
    assert diagnostic["candidate_collection_type"] == "array"
    assert diagnostic["candidate_collection_length"] == 100
    assert diagnostic["distinct_timestamps"] == 100
    assert diagnostic["distinct_raw_sizes"] == 1
    assert diagnostic["distinct_active_ids"] == 1
    assert diagnostic["request_ref"] == "request-7"
    assert diagnostic["historical_series_confirmed"] is True


def test_candles_generated_diagnostic_discovers_indexed_object_collection() -> None:
    response = post_bridge(candles_generated_indexed_payload(20))
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["candles_generated_diagnostic"]

    assert "msg.data.items" in diagnostic["nested_object_paths"]
    assert diagnostic["candidate_collection_path"] == "msg.data.items"
    assert diagnostic["candidate_collection_type"] == "object_indexed_by_raw_size"
    assert diagnostic["candidate_collection_length"] == 20
    assert diagnostic["distinct_timestamps"] == 20
    assert diagnostic["historical_series_confirmed"] is True


def test_candles_generated_diagnostic_respects_depth_limit() -> None:
    payload = {
        "event_name": "candles-generated",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "payload": {
            "name": "candles-generated",
            "msg": {"a": {"b": {"c": {"candles": [{"from": 1, "open": 1.0}]}}}},
        },
    }

    response = post_bridge(payload)
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["candles_generated_diagnostic"]

    assert all(path.count(".") <= 6 for path in diagnostic["nested_array_paths"] + diagnostic["nested_object_paths"])


def test_candles_generated_diagnostic_exposes_no_ohlc_request_id_or_sensitive_markers() -> None:
    response = post_bridge(candles_generated_array_payload(100))
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["candles_generated_diagnostic"]
    serialized = str(diagnostic).lower()

    for forbidden in ["open", "close", "min", "max", "1.1", "1.2", "request_id", "raw-request", "token", "cookie", "authorization", "bearer", "ssid", "headers", "har"]:
        assert forbidden not in serialized


def test_candles_generated_multi_timeframe_collection_is_not_confirmed_as_history() -> None:
    payload = candles_generated_indexed_payload(19)
    payload["payload"]["msg"]["data"]["items"] = {
        str(size): {"from": 1_783_720_000 + index, "open": 1.1, "size": size}
        for index, size in enumerate([1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000])
    }

    response = post_bridge(payload)
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["candles_generated_diagnostic"]

    assert diagnostic["candidate_collection_type"] == "object_indexed_by_raw_size"
    assert diagnostic["candidate_collection_length"] == 19
    assert diagnostic["distinct_raw_sizes"] == 19
    assert diagnostic["historical_series_confirmed"] is False


def test_candles_generated_msg_candles_is_recognized_as_raw_size_map_not_history() -> None:
    payload = {
        "event_name": "candles-generated",
        "source": "POLARIUM_AUTHORIZED_BROWSER",
        "payload": {
            "name": "candles-generated",
            "msg": {
                "active_id": 76,
                "at": 1_783_720_000,
                "ask": 1.2,
                "bid": 1.1,
                "value": 1.15,
                "phase": "T",
                "candles": {
                    "1": {"from": 1_783_720_000, "open": 1.1},
                    "5": {"from": 1_783_720_000, "open": 1.1},
                    "60": {"from": 1_783_720_000, "open": 1.1},
                    "300": {"from": 1_783_720_000, "open": 1.1},
                },
            },
        },
    }

    response = post_bridge(payload)
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["candles_generated_diagnostic"]

    assert diagnostic["candidate_collection_path"] == "msg.candles"
    assert diagnostic["candidate_collection_type"] == "object_indexed_by_raw_size"
    assert diagnostic["candidate_collection_length"] == 4
    assert diagnostic["distinct_raw_sizes"] == 4
    assert diagnostic["distinct_active_ids"] == 1
    assert diagnostic["historical_series_confirmed"] is False


def test_outbound_send_message_structure_is_recorded_without_values() -> None:
    response = post_bridge(outbound_send_message_payload())
    assert response.status_code == 200
    assert response.json()["pipeline_success"] is None

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["outbound_candle_request_diagnostic"]
    serialized = str(diagnostic).lower()

    assert diagnostic["seen_main"] == 1
    assert diagnostic["relayed"] == 1
    assert diagnostic["event_name"] == "sendMessage"
    assert diagnostic["inner_event_name"] == "get-candles"
    assert diagnostic["direction"] == "client_to_server"
    assert diagnostic["top_level_keys"] == ["name", "msg"]
    assert diagnostic["msg_keys"] == ["body"]
    assert diagnostic["body_keys"] == ["name", "active_id", "size", "count", "from", "to", "limit"]
    assert diagnostic["has_active_id"] is True
    assert diagnostic["has_size"] is True
    assert diagnostic["has_count"] is True
    assert diagnostic["has_from"] is True
    assert diagnostic["has_to"] is True
    assert diagnostic["has_limit"] is True
    assert diagnostic["request_ref"] == "request-9"
    assert "76" not in serialized
    assert "178372" not in serialized


def test_outbound_request_with_offset_and_chunk_size_is_detected() -> None:
    response = post_bridge(outbound_send_message_payload(offset=200, chunk_size=50, limit=50))
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["outbound_candle_request_diagnostic"]

    assert diagnostic["has_offset"] is True
    assert diagnostic["has_chunk_size"] is True
    assert "offset" in diagnostic["numeric_field_names"]
    assert "chunk_size" in diagnostic["numeric_field_names"]


def test_outbound_request_shapes_are_fingerprinted_and_limited_without_payload_values() -> None:
    for index in range(10):
        response = post_bridge(outbound_send_message_payload(name=f"shape-{index}", extra_field=index))
        assert response.status_code == 200

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    shapes = status["outbound_request_shapes"]
    serialized = str(shapes).lower()

    assert len(shapes) <= 8
    assert shapes[0]["shape_ref"] == "request_shape_1"
    assert shapes[0]["occurrences"] >= 1
    assert "76" not in serialized
    assert "178372" not in serialized


def test_outbound_correlation_by_request_ref_is_recorded_when_response_arrives() -> None:
    request = post_bridge(outbound_send_message_payload())
    response = post_bridge(candles_generated_array_payload(100))

    assert request.status_code == 200
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["outbound_candle_request_diagnostic"]

    assert diagnostic["correlation_status"] == "CONFIRMED_BY_REQUEST_ID"
    assert diagnostic["request_ref"] == "request-9"
    assert diagnostic["correlated_response_event_name"] in {None, "candles-generated"}


def test_outbound_structural_fallback_marks_temporal_candidate_without_request_ref() -> None:
    payload = {"event_name": "sendMessage", "source": "POLARIUM_AUTHORIZED_BROWSER", "payload": {"name": "sendMessage", "msg": {"body": {"method": "load-more", "limit": 50}}}}
    response = post_bridge(payload)
    assert response.status_code == 200

    diagnostic = client.get("/api/v1/polarium/browser-bridge/status").json()["outbound_candle_request_diagnostic"]

    assert diagnostic["inner_event_name"] == "load-more"
    assert diagnostic["has_limit"] is True
    assert diagnostic["correlation_status"] == "TEMPORAL_CANDIDATE"
    assert diagnostic["request_ref"] is None


def test_outbound_diagnostic_exposes_no_request_id_active_id_or_credentials() -> None:
    response = post_bridge(outbound_send_message_payload())
    assert response.status_code == 200

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    serialized = str(status["outbound_candle_request_diagnostic"]).lower()

    for forbidden in ["raw-request-id", "raw-request", "76", "token", "cookie", "authorization", "bearer", "ssid", "headers", "har"]:
        assert forbidden not in serialized


def test_historical_transport_discovery_tracks_fetch_and_xhr_without_store_write() -> None:
    for transport in ["fetch_request", "fetch_response", "xhr_request", "xhr_response"]:
        response = post_bridge(historical_transport_payload(transport=transport, timestamp_count=20))
        assert response.status_code == 200
        assert response.json()["accepted"] is True
        assert response.json()["pipeline_success"] is None

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    discovery = status["historical_transport_discovery"]

    assert discovery["fetch_requests_seen"] == 1
    assert discovery["fetch_responses_seen"] == 1
    assert discovery["xhr_requests_seen"] == 1
    assert discovery["xhr_responses_seen"] == 1
    assert discovery["historical_candidate_found"] is True
    assert discovery["historical_quality"] == "USEFUL"
    assert discovery["candidate_collection_path"] == "data.candles"
    assert market_candle_store.series(76, 60) == ()


def test_historical_transport_discovery_classifies_short_useful_and_broad_candidates() -> None:
    expectations = [(2, "SHORT"), (20, "USEFUL"), (100, "BROAD")]

    for count, quality in expectations:
        authorized_browser_bridge_runtime.reset()
        response = post_bridge(historical_transport_payload(timestamp_count=count))
        assert response.status_code == 200

        discovery = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_transport_discovery"]
        assert discovery["historical_candidate_found"] is True
        assert discovery["historical_quality"] == quality


def test_historical_transport_discovery_rejects_multi_active_or_multi_timeframe_as_confirmation() -> None:
    response = post_bridge(historical_transport_payload(timestamp_count=100, active_id_count=2, raw_size_count=1))
    assert response.status_code == 200
    discovery = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_transport_discovery"]
    assert discovery["historical_candidate_found"] is False
    assert discovery["historical_quality"] is None

    authorized_browser_bridge_runtime.reset()
    response = post_bridge(historical_transport_payload(timestamp_count=100, active_id_count=1, raw_size_count=2))
    assert response.status_code == 200
    discovery = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_transport_discovery"]
    assert discovery["historical_candidate_found"] is False
    assert discovery["historical_quality"] is None


def test_historical_transport_shapes_are_sanitized_and_limited() -> None:
    for index in range(10):
        response = post_bridge(historical_transport_payload(timestamp_count=2 + index, path=f"/api/candles/{index}/private?token=hidden"))
        assert response.status_code == 200

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    shapes = status["historical_transport_shapes"]
    serialized = str({"discovery": status["historical_transport_discovery"], "shapes": shapes}).lower()

    assert len(shapes) <= 8
    assert shapes[0]["shape_ref"] == "transport_shape_1"
    assert shapes[0]["top_level_type"] == "object"
    assert shapes[0]["top_level_keys"] == ["data", "meta"]
    assert shapes[0]["nested_array_paths"] == ["data.candles"]
    for forbidden in ["open", "close", "min", "max", "token", "cookie", "authorization", "bearer", "ssid", "headers", "har", "?"]:
        assert forbidden not in serialized


def test_historical_transport_discovery_records_parse_failure_safely() -> None:
    response = post_bridge(historical_transport_payload(transport="xhr_response", timestamp_count=0, last_error_code="TRANSPORT_PARSE_FAILED"))

    assert response.status_code == 200
    discovery = client.get("/api/v1/polarium/browser-bridge/status").json()["historical_transport_discovery"]

    assert discovery["last_error_code"] == "TRANSPORT_PARSE_FAILED"
    assert discovery["historical_candidate_found"] is False
    assert market_candle_store.series(76, 60) == ()


def test_runtime_store_discovery_records_sanitized_candidate_without_pipeline_or_store_write() -> None:
    response = post_bridge(runtime_store_discovery_payload())

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["pipeline_success"] is None
    assert market_candle_store.series(76, 60) == ()

    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    discovery = status["runtime_store_discovery"]
    candidates = status["runtime_store_candidates"]

    assert discovery["candidate_found"] is True
    assert discovery["candidate_type"] == "chart_engine"
    assert discovery["candidate_ref"] == "runtime_candidate_1"
    assert discovery["candidate_quality"] == "USEFUL"
    assert discovery["candidate_distinct_timestamps"] == 20
    assert discovery["candidate_distinct_raw_sizes"] == 1
    assert discovery["candidate_distinct_active_ids"] == 1
    assert candidates[0]["candidate_ref"] == "runtime_candidate_1"
    assert candidates[0]["quality"] == "USEFUL"


def test_runtime_store_discovery_does_not_confirm_multi_series_candidate() -> None:
    response = post_bridge(
        runtime_store_discovery_payload(
            candidate_distinct_timestamps=100,
            candidate_distinct_raw_sizes=2,
            candidate_distinct_active_ids=1,
        )
    )

    assert response.status_code == 200
    discovery = client.get("/api/v1/polarium/browser-bridge/status").json()["runtime_store_discovery"]

    assert discovery["candidate_found"] is False
    assert discovery["candidate_distinct_raw_sizes"] == 2
    assert discovery["candidate_quality"] is None


def test_runtime_store_candidates_are_limited_and_sanitized() -> None:
    payload = runtime_store_discovery_payload(candidate_distinct_timestamps=2)
    payload["runtime_store_candidates"] = [
        {
            "candidate_ref": f"runtime_candidate_{index + 1}",
            "source_type": "window_global",
            "name_sanitized": f"candidate_{index}",
            "path_sanitized": f"window.candidate_{index}",
            "object_type": "object",
            "top_level_keys": ["candles", "open", "close"],
            "method_names": ["getState", "dispatch"],
            "array_paths": ["candles"],
            "object_paths": ["state"],
            "collection_length": index + 2,
            "distinct_timestamps": index + 2,
            "distinct_raw_sizes": 1,
            "distinct_active_ids": 1,
            "readable_passively": True,
        }
        for index in range(20)
    ]

    response = post_bridge(payload)

    assert response.status_code == 200
    status = client.get("/api/v1/polarium/browser-bridge/status").json()
    serialized = str(status["runtime_store_candidates"]).lower()

    assert len(status["runtime_store_candidates"]) <= 12
    assert "open" not in serialized
    assert "close" not in serialized
    assert "token" not in serialized
    assert "cookie" not in serialized
    assert "authorization" not in serialized
    assert "bearer" not in serialized
    assert "ssid" not in serialized


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
