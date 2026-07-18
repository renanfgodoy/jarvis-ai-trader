from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_core_demo_executes_through_orchestrator_with_mock_provider() -> None:
    response = client.post(
        "/api/v1/core/demo/execute",
        json={
            "module": "documents",
            "identity": "jarvis.default",
            "provider": "mock",
            "language": "pt-BR",
            "message": "Execute a demo sem API externa.",
            "metadata": {"test": True},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["identity"] == "jarvis.default"
    assert data["provider"] == "mock"
    assert data["provider_response"]["metadata"]["external_api_called"] is False
    assert data["provider_response"]["metadata"]["developer_console"] is True
    assert data["metadata"]["module"] == "documents"
    assert data["metadata"]["pipeline_version"] == "1.0"
    assert "identity_result" not in data
    assert "prompt_result" not in data
    assert "execution_context" not in data


def test_core_demo_blocks_real_provider_selection() -> None:
    response = client.post(
        "/api/v1/core/demo/execute",
        json={
            "module": "documents",
            "identity": "jarvis.default",
            "provider": "openai",
            "language": "pt-BR",
            "message": "Tente usar provider real.",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "CORE_DEMO_ONLY_MOCK_PROVIDER_ALLOWED"


def test_core_demo_executes_trading_module_through_sdk() -> None:
    response = client.post(
        "/api/v1/core/demo/execute",
        json={
            "module": "trading",
            "identity": "jarvis.trading",
            "provider": "mock",
            "language": "pt-BR",
            "message": "Avalie sem operar.",
            "market": "OTC",
            "symbol": "EURUSD",
            "timeframe": "M1",
            "strategy": "Trend",
            "metadata": {"test": True},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["decision"] == "OBSERVE"
    assert data["confidence"] == 72
    assert data["execution"]["module"] == "trading"
    assert data["execution"]["provider"] == "mock"
    assert data["execution"]["execution"]["provider_response"]["metadata"]["module_sdk"] is True
    assert data["execution"]["execution"]["provider_response"]["metadata"]["external_api_called"] is False
