from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["app"] == "J.A.R.V.I.S AI TRADER"
    assert data["risk_profile"]["bankroll_base"] == 200.0
