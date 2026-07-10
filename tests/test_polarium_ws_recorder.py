from app.models.polarium_ws_recorder import WsFrameInput
from app.services.polarium_ws_recorder import PolariumWsRecorderService


def test_ws_recorder_detects_balance_candle_and_price_frames():
    raw = """
    {"name":"sendMessage","request_id":"1","msg":{"name":"subscribeMessage","body":{"name":"marginal-balance"}}}
    {"request_id":"1","name":"marginal-balance","msg":{"available":"16037.53","currency":"USD"}}
    {"name":"candle-generated","microserviceName":"quotes","msg":{"active_id":1,"open":1,"close":2}}
    {"name":"digital-option-client-price-generated","microserviceName":"trading-settings","msg":{"active_id":1,"price":86}}
    """
    result = PolariumWsRecorderService().analyze_frames(WsFrameInput(raw=raw))
    assert result.parsed_messages == 4
    assert result.balance_candidates
    assert result.candle_candidates
    assert result.price_candidates
    assert result.status == "OK"
