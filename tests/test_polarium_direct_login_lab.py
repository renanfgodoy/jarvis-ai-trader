from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_polarium_direct_config_exists():
    response = client.get("/api/v1/polarium/direct/config")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "safety_rules" in data


def test_polarium_direct_probe_dry_run_safe():
    response = client.post("/api/v1/polarium/direct/probe", json={"dry_run": True, "force_demo": True})
    assert response.status_code == 200
    data = response.json()
    assert data["dry_run"] is True
    assert data["status"] in {"DRY_RUN", "MISSING_CONFIG"}
    assert data["token_stored"] is False


def test_polarium_direct_session_shape():
    response = client.get("/api/v1/polarium/direct/session")
    assert response.status_code == 200
    data = response.json()
    assert "has_session" in data
    assert "message" in data
