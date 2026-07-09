from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_execution_status_is_demo_only():
    response = client.get("/api/v1/execution/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert data["demo_only"] is True
    assert data["live_trading_enabled"] is False
    assert data["account_type"] == "DEMO"


def test_demo_execution_is_simulated_when_risk_is_approved():
    payload = {
        "symbol": "EURUSD-OTC",
        "timeframe": "M1",
        "signal": "BUY",
        "bankroll": 200,
        "entry_value": 10,
        "daily_wins": 0,
        "daily_losses": 0,
        "gale_used": 0,
        "payout": 80,
        "expiration_minutes": 1,
        "mode": "DEMO",
    }
    response = client.post("/api/v1/execution/demo/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert data["status"] == "SIMULATED"
    assert data["action"] == "SIMULATED_BUY_ORDER"
    assert data["account_type"] == "DEMO"


def test_demo_execution_is_blocked_after_stop_loss():
    payload = {
        "symbol": "EURUSD-OTC",
        "timeframe": "M1",
        "signal": "SELL",
        "bankroll": 200,
        "entry_value": 10,
        "daily_wins": 0,
        "daily_losses": 2,
        "gale_used": 0,
        "payout": 80,
        "expiration_minutes": 1,
        "mode": "DEMO",
    }
    response = client.post("/api/v1/execution/demo/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is False
    assert data["status"] == "BLOCKED"
    assert data["action"] == "NO_EXECUTION"


def test_demo_execution_blocks_entry_above_risk_limit():
    payload = {
        "symbol": "EURUSD-OTC",
        "timeframe": "M1",
        "signal": "BUY",
        "bankroll": 200,
        "entry_value": 50,
        "daily_wins": 0,
        "daily_losses": 0,
        "gale_used": 0,
        "payout": 80,
        "expiration_minutes": 1,
        "mode": "DEMO",
    }
    response = client.post("/api/v1/execution/demo/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is False
    assert data["risk_decision"] == "BLOCKED"
