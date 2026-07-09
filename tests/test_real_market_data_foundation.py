from fastapi.testclient import TestClient

from app.main import app
from app.providers.manager import ProviderManager
from app.services.market_reader import MarketReaderService

client = TestClient(app)


def test_market_assets_endpoint_returns_asset_metadata() -> None:
    response = client.get("/api/v1/market/assets")

    assert response.status_code == 200
    data = response.json()

    assert data["provider"] == "simulated"
    assert data["data_quality"] == "SIMULATED"
    assert data["simulated"] is True
    assert data["total_assets"] >= 12
    assert data["open_assets"] >= 12
    assert data["assets"][0]["payout"] >= 0
    assert data["assets"][0]["status"] == "OPEN"


def test_provider_assets_endpoint_matches_market_assets() -> None:
    market = client.get("/api/v1/market/assets").json()
    provider = client.get("/api/v1/providers/assets").json()

    assert provider["total_assets"] == market["total_assets"]
    assert provider["data_quality"] == market["data_quality"]


def test_provider_manager_exposes_assets_with_payout() -> None:
    assets = ProviderManager().get_assets()

    assert len(assets) >= 12
    assert all(asset.payout > 0 for asset in assets)
    assert all(asset.data_quality == "SIMULATED" for asset in assets)


def test_market_reader_assets_response_has_open_assets() -> None:
    response = MarketReaderService().get_assets_response()

    assert response.total_assets >= 12
    assert response.open_assets == response.total_assets
    assert response.simulated is True


def test_scanner_results_include_payout_and_data_quality() -> None:
    data = client.get("/api/v1/scanner/top-assets?top=3").json()

    assert len(data["results"]) == 3
    assert data["data_quality"] == "SIMULATED"
    assert data["simulated"] is True
    for item in data["results"]:
        assert "payout" in item
        assert "data_quality" in item
        assert item["market_status"] == "OPEN"
