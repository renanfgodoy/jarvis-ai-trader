from app.models.account import AutoTradeGateRequest
from app.services.autotrade_gate import AutoTradeGateService


def test_autotrade_gate_waits_until_timeframe_and_click():
    response = AutoTradeGateService().check(
        AutoTradeGateRequest(
            timeframe=None,
            autotrade_requested=False,
            currency="BRL",
            entry_value=10,
        )
    )

    assert response.allowed is False
    assert response.status == "WAITING"
    assert response.can_analyze is False


def test_autotrade_gate_requires_demo_account():
    response = AutoTradeGateService().check(
        AutoTradeGateRequest(
            timeframe="M1",
            autotrade_requested=True,
            account_type="REAL",
            currency="BRL",
            entry_value=10,
        )
    )

    assert response.allowed is False
    assert "Conta REAL bloqueada" in " ".join(response.reasons)


def test_autotrade_gate_brl_minimum_entry():
    response = AutoTradeGateService().check(
        AutoTradeGateRequest(
            timeframe="M5",
            autotrade_requested=True,
            currency="BRL",
            entry_value=4,
        )
    )

    assert response.allowed is False
    assert response.minimum_entry == 5


def test_autotrade_gate_usd_minimum_entry():
    response = AutoTradeGateService().check(
        AutoTradeGateRequest(
            timeframe="M15",
            autotrade_requested=True,
            currency="USD",
            entry_value=0.5,
        )
    )

    assert response.allowed is False
    assert response.minimum_entry == 1


def test_autotrade_gate_allows_valid_demo_operation():
    response = AutoTradeGateService().check(
        AutoTradeGateRequest(
            symbol="GBPUSD-OTC",
            timeframe="M1",
            autotrade_requested=True,
            account_type="DEMO",
            currency="USD",
            balance=200,
            entry_value=1,
            score=91,
            risk_approved=True,
            websocket_online=True,
            execution_ready=True,
            asset_valid=True,
        )
    )

    assert response.allowed is True
    assert response.status == "READY"
    assert response.can_analyze is True
    assert response.currency_symbol == "US$"
