from fastapi.testclient import TestClient

from app.main import app
from app.services.polarium_oauth_lab import create_code_challenge, create_code_verifier

client = TestClient(app)


def test_pkce_verifier_and_challenge_are_generated():
    verifier = create_code_verifier()
    challenge = create_code_challenge(verifier)
    assert len(verifier) >= 43
    assert len(challenge) >= 43
    assert "=" not in verifier
    assert "=" not in challenge


def test_oauth_config_endpoint():
    response = client.get("/api/v1/polarium/oauth/config")
    assert response.status_code == 200
    payload = response.json()
    assert "configured" in payload
    assert payload["token_url"].endswith("/auth/oauth.v5/token")


def test_oauth_start_endpoint_without_credentials_is_safe():
    response = client.post("/api/v1/polarium/oauth/start", json={})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in ["MISSING_CONFIG", "READY"]
    assert payload["code_challenge_method"] == "S256"
    assert payload["code_challenge"]
    assert payload["code_verifier_preview"]


def test_oauth_exchange_dry_run_does_not_store_token():
    response = client.post(
        "/api/v1/polarium/oauth/exchange",
        json={"code": "fake-authorization-code", "dry_run": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["dry_run"] is True
    assert payload["token_stored"] is False


def test_oauth_session_endpoint():
    response = client.get("/api/v1/polarium/oauth/session")
    assert response.status_code == 200
    payload = response.json()
    assert "has_token" in payload
    assert "safety_rules" in payload
