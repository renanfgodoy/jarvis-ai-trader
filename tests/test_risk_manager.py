from fastapi.testclient import TestClient

from app.main import app
from app.models.risk import RiskCheckRequest
from app.services.risk_manager import RiskManagerService

client = TestClient(app)


def test_risk_manager_approves_safe_context() -> None:
    response = RiskManagerService().check(RiskCheckRequest(bankroll=200, daily_wins=0, daily_losses=0, gale_used=0))

    assert response.allowed is True
    assert response.decision == "APPROVED"
    assert response.recommended_entry == 10.0
    assert response.max_entry_allowed == 10.0
    assert response.risk_score < 70


def test_risk_manager_blocks_after_two_losses() -> None:
    response = RiskManagerService().check(RiskCheckRequest(bankroll=200, daily_losses=2))

    assert response.allowed is False
    assert response.decision == "BLOCKED"
    assert response.risk_level == "CRITICAL"
    assert any("Stop loss" in reason for reason in response.reasons)


def test_risk_manager_blocks_after_three_wins() -> None:
    response = RiskManagerService().check(RiskCheckRequest(bankroll=200, daily_wins=3))

    assert response.allowed is False
    assert response.decision == "BLOCKED"
    assert any("Stop win" in reason for reason in response.reasons)


def test_risk_manager_blocks_entry_above_five_percent() -> None:
    response = RiskManagerService().check(RiskCheckRequest(bankroll=200, entry_value=20))

    assert response.allowed is False
    assert response.max_entry_allowed == 10.0
    assert any("5%" in reason for reason in response.reasons)


def test_risk_manager_endpoint_returns_valid_payload() -> None:
    response = client.get("/api/v1/risk/check?bankroll=200&daily_wins=0&daily_losses=0&gale_used=0")

    assert response.status_code == 200
    data = response.json()
    assert data["allowed"] is True
    assert data["decision"] == "APPROVED"
    assert data["bankroll"] == 200.0
    assert data["recommended_entry"] == 10.0
    assert "Primeiro proteger a banca" in data["official_rule"]
