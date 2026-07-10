from app.market.events.router import route_market_event


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


def test_first_candles_valid_collection_is_normalized() -> None:
    result = route_market_event(first_candles_payload())

    assert result.status == "parsed"
    assert result.metadata.event_name == "first-candles"
    assert result.metadata.request_id == "80"
    assert len(result.candles) == 2
    assert [candle.raw_size for candle in result.candles] == [60, 300]
    assert all(candle.active_id == 76 for candle in result.candles)
    assert all(candle.symbol is None for candle in result.candles)
    assert all(candle.timeframe is None for candle in result.candles)
    assert all(candle.mapping_verified is False for candle in result.candles)


def test_first_candles_with_one_invalid_item_returns_valid_candles_and_error() -> None:
    payload = first_candles_payload()
    del payload["msg"]["body"]["candles_by_size"]["300"]["close"]

    result = route_market_event(payload)

    assert result.status == "parsed"
    assert len(result.candles) == 1
    assert result.candles[0].raw_size == 60
    assert len(result.errors) == 1
    assert result.errors[0].code == "missing_field"
    assert result.errors[0].path == "$.msg.body.candles_by_size.300.close"


def test_first_candles_without_body_returns_structured_error() -> None:
    result = route_market_event({"name": "first-candles"})

    assert result.status == "invalid"
    assert result.candles == ()
    assert result.errors[0].code == "missing_body"


def test_first_candles_does_not_invent_active_id_when_absent() -> None:
    payload = first_candles_payload()
    del payload["msg"]["body"]["active_id"]

    result = route_market_event(payload)

    assert result.status == "parsed"
    assert all(candle.active_id is None for candle in result.candles)
