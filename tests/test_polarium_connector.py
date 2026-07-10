from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services import polarium_connector

client = TestClient(app)


def setup_function() -> None:
    polarium_connector.SESSION_FILE = Path(".jarvis_cache_test/polarium_session.json")
    if polarium_connector.SESSION_FILE.exists():
        polarium_connector.SESSION_FILE.unlink()


def test_polarium_status_disconnected_when_no_cache() -> None:
    response = client.get("/api/v1/polarium/status")
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is False
    assert data["status"] == "DISCONNECTED"
    assert data["demo_only"] is True
    assert data["data_source"] == "UNAVAILABLE"
    assert data["is_balance_synced"] is False


def test_polarium_login_caches_demo_session_without_password_or_fake_balance() -> None:
    response = client.post(
        "/api/v1/polarium/login",
        json={"email": "renan@example.com", "password": "senha-teste", "remember_session": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["account"]["connected"] is True
    assert data["account"]["account_mode"] == "DEMO"
    assert data["account"]["data_source"] == "UNAVAILABLE"
    assert data["account"]["sync_status"] == "NOT_SYNCED"
    assert data["account"]["is_balance_synced"] is False
    assert data["account"]["balance"] is None
    assert data["account"]["currency"] is None
    assert data["account"]["minimum_entry"] is None
    assert polarium_connector.SESSION_FILE.exists()
    cache_text = polarium_connector.SESSION_FILE.read_text(encoding="utf-8")
    assert "senha-teste" not in cache_text
    assert "10000" not in cache_text


def test_polarium_status_reads_cached_unsynced_session() -> None:
    client.post(
        "/api/v1/polarium/login",
        json={"email": "renan@example.com", "password": "senha-teste", "remember_session": True},
    )
    response = client.get("/api/v1/polarium/status")
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert data["session_cached"] is True
    assert data["email_masked"].endswith("@example.com")
    assert data["is_balance_synced"] is False


def test_polarium_sync_fails_safely_without_authorized_adapter() -> None:
    client.post(
        "/api/v1/polarium/login",
        json={"email": "renan@example.com", "password": "senha-teste", "remember_session": True},
    )
    response = client.post("/api/v1/polarium/sync")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["account"]["sync_status"] == "FAILED"
    assert data["account"]["data_source"] == "UNAVAILABLE"
    assert data["account"]["is_balance_synced"] is False
    assert data["account"]["balance"] is None
    assert "não sincronizada" in data["message"].lower()


def test_polarium_logout_removes_cache() -> None:
    client.post(
        "/api/v1/polarium/login",
        json={"email": "renan@example.com", "password": "senha-teste", "remember_session": True},
    )
    response = client.post("/api/v1/polarium/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert polarium_connector.SESSION_FILE.exists() is False
