from app.models.polarium_session_inspector import HarInspectRequest
from app.services.polarium_session_inspector import PolariumSessionInspectorService


def test_har_inspector_detects_oauth_and_websocket():
    har = {
        "log": {
            "entries": [
                {"request": {"method": "GET", "url": "https://api.trade.polariumbroker.com/auth/oauth.v5/authorize?client_id=123&redirect_uri=http://localhost/cb&scope=full%20offline_access", "headers": []}, "response": {"status": 302, "headers": []}},
                {"request": {"method": "GET", "url": "http://localhost/cb?code=abc&state=xyz", "headers": []}, "response": {"status": 200, "headers": []}},
                {"request": {"method": "POST", "url": "https://api.trade.polariumbroker.com/auth/oauth.v5/token", "headers": [], "postData": {"text": '{"grant_type":"authorization_code","client_id":"123","code_verifier":"secret"}'}}, "response": {"status": 200, "headers": []}},
                {"request": {"method": "GET", "url": "wss://ws.trade.polariumbroker.com/echo/websocket", "headers": [{"name": "Origin", "value": "https://trade.polariumbroker.com"}]}, "response": {"status": 101, "headers": []}},
            ]
        }
    }
    result = PolariumSessionInspectorService().inspect_har(HarInspectRequest(har=har))
    assert result.oauth_authorize_found is True
    assert result.oauth_token_found is True
    assert result.websocket_found is True
    assert result.status == "OK"
