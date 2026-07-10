from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_polarium_diagnostics_summary():
    response = client.get("/api/v1/polarium/diagnostics/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == "0.24.0"
    assert "checks" in payload


def test_polarium_oauth_diagnostic():
    response = client.get("/api/v1/polarium/diagnostics/oauth")
    assert response.status_code == 200
    payload = response.json()
    assert payload["module"] == "oauth"
    assert any(check["name"] == "PKCE" for check in payload["checks"])


def test_polarium_stream_diagnostic_detects_balance_and_candle():
    response = client.post(
        "/api/v1/polarium/diagnostics/stream",
        json={
            "payloads": [
                {"name": "marginal-balance", "msg": {"available": "16037.53", "currency": "USD"}},
                {"name": "candle-generated", "msg": {"open": 1, "close": 2}},
                {"name": "digital-option-client-price-generated", "msg": {"price": 1.2}},
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["balance_payload_detected"] is True
    assert payload["candle_payload_detected"] is True
    assert payload["price_payload_detected"] is True


def test_polarium_stream_diagnostic_empty_is_safe():
    response = client.post("/api/v1/polarium/diagnostics/stream", json={"payloads": []})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in ["WARN", "OK"]
