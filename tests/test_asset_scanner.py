from fastapi.testclient import TestClient

from app.main import app
from app.services.asset_scanner import AssetScannerService

client = TestClient(app)


def test_asset_scanner_returns_top_12_assets():
    response = client.get("/api/v1/scanner/top-assets")

    assert response.status_code == 200
    data = response.json()

    assert data["timeframe"] == "M1"
    assert data["assets_scanned"] >= 12
    assert data["top_limit"] == 12
    assert len(data["results"]) == 12
    assert data["results"][0]["rank"] == 1
    assert 0 <= data["results"][0]["score"] <= 100


def test_asset_scanner_ranking_is_descending():
    data = client.get("/api/v1/scanner/top-assets").json()
    scores = [item["score"] for item in data["results"]]

    assert scores == sorted(scores, reverse=True)


def test_asset_scanner_supports_custom_top_limit():
    response = client.get("/api/v1/scanner/top-assets?top=5")

    assert response.status_code == 200
    data = response.json()

    assert data["top_limit"] == 5
    assert len(data["results"]) == 5


def test_asset_scanner_service_supports_custom_symbols():
    result = AssetScannerService().scan(symbols=["EURUSD-OTC", "GBPUSD-OTC", "EURUSD-OTC"], top=2)

    assert result.assets_scanned == 2
    assert len(result.results) == 2
    assert {item.symbol for item in result.results}.issubset({"EURUSD-OTC", "GBPUSD-OTC"})
