from app.market.events.router import route_market_event


def test_event_without_name_returns_invalid_result() -> None:
    result = route_market_event({"msg": {"body": {}}})

    assert result.status == "invalid"
    assert result.metadata.event_name is None
    assert result.errors[0].code == "missing_event_name"


def test_unknown_event_returns_unsupported_result() -> None:
    result = route_market_event({"name": "unknown-market-event", "msg": {"body": {}}})

    assert result.status == "unsupported"
    assert result.metadata.event_name == "unknown-market-event"
    assert result.errors[0].code == "unsupported_event"


def test_known_non_candle_event_is_controlled_unsupported() -> None:
    result = route_market_event({"name": "timeSync"})

    assert result.status == "unsupported"
    assert result.metadata.event_name == "timeSync"
    assert result.errors[0].code == "event_not_parsed"


def test_nested_send_message_event_name_is_detected() -> None:
    result = route_market_event(
        {
            "request_id": "80",
            "name": "sendMessage",
            "msg": {"name": "get-first-candles", "body": {"active_id": 76}},
        }
    )

    assert result.status == "unsupported"
    assert result.metadata.event_name == "get-first-candles"
    assert result.metadata.request_id == "80"


def test_payload_without_msg_returns_invalid_result_for_candle_event() -> None:
    result = route_market_event({"name": "candle-generated"})

    assert result.status == "invalid"
    assert result.errors[0].code == "missing_body"
