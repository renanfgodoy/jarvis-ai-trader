from fastapi.testclient import TestClient

from app.main import app
from app.models.provider import TradingViewWebhookPayload
from app.services.provider_engine import ProviderEngineService
from app.providers.tradingview_webhook import TradingViewWebhookProvider

client = TestClient(app)


def test_list_providers_endpoint() -> None:
    response = client.get("/api/v1/providers")

    assert response.status_code == 200
    providers = response.json()
    names = {provider["name"] for provider in providers}

    assert "simulated" in names
    assert "TradingView" in names


def test_tradingview_webhook_endpoint_queues_alert() -> None:
    payload = {
        "symbol": "eurusd-otc",
        "timeframe": "M1",
        "signal": "BUY",
        "price": 1.17545,
        "strategy": "Jarvis v1",
    }

    response = client.post("/api/v1/providers/tradingview/webhook", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["received"] is True
    assert data["provider"] == "TradingView"
    assert data["status"] == "queued"
    assert data["symbol"] == "EURUSD-OTC"
    assert data["signal"] == "BUY"
    assert data["price"] == payload["price"]
    assert "Não executa ordens" in data["disclaimer"]


def test_tradingview_webhook_rejects_invalid_signal() -> None:
    payload = {
        "symbol": "EURUSD-OTC",
        "timeframe": "M1",
        "signal": "STRONG_BUY",
        "price": 1.17545,
        "strategy": "Jarvis v1",
    }

    response = client.post("/api/v1/providers/tradingview/webhook", json=payload)

    assert response.status_code == 422


def test_provider_engine_service_keeps_alert_in_memory_queue() -> None:
    provider = TradingViewWebhookProvider()
    service = ProviderEngineService(tradingview_provider=provider)
    payload = TradingViewWebhookPayload(
        symbol="EURUSD-OTC",
        timeframe="M1",
        signal="SELL",
        price=1.10123,
        strategy="Jarvis test",
    )

    response = service.receive_tradingview_webhook(payload)

    assert response.received is True
    assert response.status == "queued"
    assert provider.queued_count() == 1
