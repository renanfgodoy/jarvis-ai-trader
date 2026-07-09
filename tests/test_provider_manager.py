from fastapi.testclient import TestClient

from app.main import app
from app.providers.manager import ProviderManager
from app.providers.simulated import SimulatedMarketDataProvider
from app.services.asset_scanner import AssetScannerService
from app.services.market_reader import MarketReaderService

client = TestClient(app)


def test_provider_manager_current_endpoint_returns_simulated_provider() -> None:
    response = client.get("/api/v1/providers/current")

    assert response.status_code == 200
    data = response.json()

    assert data["provider"] == "simulated"
    assert data["connected"] is True
    assert data["status"] == "active"
    assert data["supportsRealtime"] is False
    assert data["supportsTrading"] is False


def test_provider_manager_list_endpoint_includes_future_providers() -> None:
    response = client.get("/api/v1/providers/list")

    assert response.status_code == 200
    data = response.json()
    names = {provider["name"] for provider in data}

    assert "simulated" in names
    assert "tradingview" in names
    assert "quadcode" in names
    assert any(provider["active"] for provider in data)


def test_provider_manager_returns_active_provider_instance() -> None:
    manager = ProviderManager()
    provider = manager.get_active_provider()

    assert isinstance(provider, SimulatedMarketDataProvider)
    assert provider.name == "simulated"
    assert len(manager.get_symbols()) >= 12


def test_market_reader_uses_provider_manager_symbols() -> None:
    reader = MarketReaderService(provider_manager=ProviderManager())
    symbols = reader.get_symbols()

    assert "EURUSD-OTC" in symbols
    assert "BTCUSD-OTC" in symbols
    assert len(symbols) >= 12


def test_scanner_uses_provider_symbols_when_no_custom_symbols() -> None:
    result = AssetScannerService().scan(top=12)

    assert result.assets_scanned >= 12
    assert len(result.results) == 12
