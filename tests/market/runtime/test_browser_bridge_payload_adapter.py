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
