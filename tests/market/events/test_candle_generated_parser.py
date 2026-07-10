from app.market.events.router import route_market_event


def candle_generated_payload() -> dict:
    return {
        "name": "candle-generated",
        "msg": {
            "body": {
                "active_id": 76,
                "size": 60,
                "from": 1783721940,
                "to": 1783722000,
                "open": 1.162275,
                "close": 1.162145,
                "min": 1.162145,
                "max": 1.162395,
                "volume": 0,
            }
        },
    }


def test_candle_generated_valid_event_is_normalized() -> None:
    result = route_market_event(candle_generated_payload())

    assert result.status == "parsed"
    assert result.metadata.event_name == "candle-generated"
    assert len(result.candles) == 1

    candle = result.candles[0]
    assert candle.active_id == 76
    assert candle.raw_size == 60
    assert candle.start_timestamp == 1783721940
    assert candle.end_timestamp == 1783722000
    assert candle.open == 1.162275
    assert candle.close == 1.162145
    assert candle.low_candidate == 1.162145
    assert candle.high_candidate == 1.162395
    assert candle.volume == 0
    assert candle.symbol is None
    assert candle.timeframe is None
    assert candle.mapping_verified is False


def test_candle_generated_missing_required_field_returns_error() -> None:
    payload = candle_generated_payload()
    del payload["msg"]["body"]["open"]

    result = route_market_event(payload)

    assert result.status == "invalid"
    assert result.candles == ()
    assert result.errors[0].code == "missing_field"
    assert result.errors[0].path == "$.msg.body.open"


def test_candle_generated_invalid_numeric_type_returns_error() -> None:
    payload = candle_generated_payload()
    payload["msg"]["body"]["open"] = "1.162275"

    result = route_market_event(payload)

    assert result.status == "invalid"
    assert result.candles == ()
    assert result.errors[0].code == "invalid_number"


def test_candle_generated_preserves_volume_without_visual_timeframe() -> None:
    payload = candle_generated_payload()
    payload["msg"]["body"]["volume"] = 12.5

    result = route_market_event(payload)

    candle = result.candles[0]
    assert candle.volume == 12.5
    assert candle.timeframe is None
