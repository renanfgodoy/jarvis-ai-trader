from __future__ import annotations

from app.market.browser_bridge_payload_adapter import adapt_browser_bridge_payload


def anonymized_real_candle_generated_msg_payload() -> dict:
    return {
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


def test_adapter_converts_real_candle_generated_msg_shape_to_pipeline_contract() -> None:
    converted = adapt_browser_bridge_payload("candle-generated", anonymized_real_candle_generated_msg_payload())

    assert converted["name"] == "candle-generated"
    assert converted["msg"]["body"] == {
        "active_id": 76,
        "size": 60,
        "from": 1_783_721_940,
        "to": 1_783_722_000,
        "open": 1.16227,
        "close": 1.16231,
        "min": 1.16220,
        "max": 1.16235,
        "volume": 0,
    }


def test_adapter_preserves_observed_symbol_from_real_candle_payload() -> None:
    payload = anonymized_real_candle_generated_msg_payload()
    payload["payload"]["msg"]["symbol"] = "EUR/USD OTC"

    converted = adapt_browser_bridge_payload("candle-generated", payload)

    assert converted["msg"]["body"]["symbol"] == "EUR/USD OTC"


def test_adapter_uses_observed_symbol_metadata_when_payload_has_no_symbol() -> None:
    payload = anonymized_real_candle_generated_msg_payload()
    payload["observed_symbol"] = "BTC/USD"
    payload["observed_symbol_source"] = "polarium_dom"

    converted = adapt_browser_bridge_payload("candle-generated", payload)

    assert converted["msg"]["body"]["symbol"] == "BTC/USD"


def test_adapter_converts_top_level_real_candle_generated_shape() -> None:
    payload = {
        "event_name": "candle-generated",
        "payload": {
            "name": "candle-generated",
            "active_id": 76,
            "size": 60,
            "from": 1_783_721_940,
            "to": 1_783_722_000,
            "open": 1.16227,
            "close": 1.16231,
            "min": 1.16220,
            "max": 1.16235,
        },
    }

    converted = adapt_browser_bridge_payload("candle-generated", payload)

    assert converted["msg"]["body"]["active_id"] == 76
    assert converted["msg"]["body"]["size"] == 60
    assert converted["msg"]["body"]["close"] == 1.16231


def test_adapter_supports_common_short_ohlc_aliases() -> None:
    payload = {
        "event_name": "candle-generated",
        "payload": {
            "name": "candle-generated",
            "data": {
                "activeId": 76,
                "raw_size": 60,
                "timestamp": 1_783_721_940,
                "end_timestamp": 1_783_722_000,
                "o": 1.16227,
                "c": 1.16231,
                "low": 1.16220,
                "high": 1.16235,
                "v": 12,
            },
        },
    }

    converted = adapt_browser_bridge_payload("candle-generated", payload)

    assert converted["msg"]["body"] == {
        "active_id": 76,
        "size": 60,
        "from": 1_783_721_940,
        "to": 1_783_722_000,
        "open": 1.16227,
        "close": 1.16231,
        "min": 1.16220,
        "max": 1.16235,
        "volume": 12,
    }


def test_adapter_converts_first_candles_msg_shape_without_body() -> None:
    payload = {
        "event_name": "first-candles",
        "payload": {
            "name": "first-candles",
            "msg": {
                "active_id": 76,
                "candles_by_size": {
                    "60": {
                        "from": 1_783_721_880,
                        "to": 1_783_721_940,
                        "open": 1.16210,
                        "close": 1.16220,
                        "low": 1.16200,
                        "high": 1.16230,
                    }
                },
            },
        },
    }

    converted = adapt_browser_bridge_payload("first-candles", payload)

    assert converted["msg"]["body"]["active_id"] == 76
    assert converted["msg"]["body"]["candles_by_size"]["60"]["min"] == 1.16200
    assert converted["msg"]["body"]["candles_by_size"]["60"]["max"] == 1.16230


def test_adapter_converts_real_first_candles_list_envelope_to_pipeline_contract() -> None:
    payload = {
        "event_name": "first-candles",
        "payload": {
            "name": "first-candles",
            "msg": {
                "body": {
                    "candles": [
                        {
                            "activeId": 76,
                            "rawSize": 60,
                            "timestamp": 1_783_721_880,
                            "endTimestamp": 1_783_721_940,
                            "o": 1.16210,
                            "c": 1.16220,
                            "l": 1.16200,
                            "h": 1.16230,
                            "v": 0,
                        },
                        {
                            "active_id": 76,
                            "size": 60,
                            "from": 1_783_721_940,
                            "to": 1_783_722_000,
                            "open": 1.16220,
                            "close": 1.16240,
                            "min": 1.16210,
                            "max": 1.16250,
                            "volume": 0,
                        },
                    ]
                }
            },
        },
    }

    converted = adapt_browser_bridge_payload("first-candles", payload)

    assert converted["name"] == "first-candles"
    assert converted["msg"]["body"]["candles"] == [
        {
            "from": 1_783_721_880,
            "to": 1_783_721_940,
            "open": 1.16210,
            "close": 1.16220,
            "min": 1.16200,
            "max": 1.16230,
            "active_id": 76,
            "size": 60,
            "volume": 0,
        },
        {
            "from": 1_783_721_940,
            "to": 1_783_722_000,
            "open": 1.16220,
            "close": 1.16240,
            "min": 1.16210,
            "max": 1.16250,
            "active_id": 76,
            "size": 60,
            "volume": 0,
        },
    ]


def test_adapter_supports_first_candles_data_envelope_with_top_level_defaults() -> None:
    payload = {
        "event_name": "first-candles",
        "payload": {
            "name": "first-candles",
            "data": {
                "active_id": 2298,
                "size": 300,
                "candles": [
                    {
                        "from": 1_783_721_700,
                        "to": 1_783_722_000,
                        "open": 1.2,
                        "close": 1.3,
                        "low": 1.1,
                        "high": 1.4,
                    }
                ],
            },
        },
    }

    converted = adapt_browser_bridge_payload("first-candles", payload)

    assert converted["msg"]["body"]["active_id"] == 2298
    assert converted["msg"]["body"]["size"] == 300
    assert converted["msg"]["body"]["candles"][0]["active_id"] == 2298
    assert converted["msg"]["body"]["candles"][0]["size"] == 300
    assert converted["msg"]["body"]["candles"][0]["min"] == 1.1
    assert converted["msg"]["body"]["candles"][0]["max"] == 1.4
