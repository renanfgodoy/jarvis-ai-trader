from fastapi.testclient import TestClient

from app.main import app
from app.services.confluence_engine import ConfluenceEngineService
from app.services.market_intelligence import MarketIntelligenceService

client = TestClient(app)


def test_market_intelligence_analyze_returns_explainable_score():
    response = client.get("/api/v1/intelligence/analyze?symbol=EURUSD-OTC&timeframe=M1&payout=86")

    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "EURUSD-OTC"
    assert data["timeframe"] == "M1"
    assert 0 <= data["score"] <= 100
    assert data["status"] in {"APPROVED", "WATCHLIST", "BLOCKED"}
    assert len(data["factors"]) >= 5
    assert "action" in data


def test_market_intelligence_scanner_returns_top_assets():
    response = client.get("/api/v1/intelligence/scanner/top?timeframe=M5&top=6")

    assert response.status_code == 200
    data = response.json()

    assert data["timeframe"] == "M5"
    assert data["top_limit"] == 6
    assert len(data["results"]) == 6
    assert data["assets_scanned"] >= 6


def test_market_intelligence_ranking_is_descending():
    data = client.get("/api/v1/intelligence/scanner/top?top=8").json()
    scores = [item["score"] for item in data["results"]]

    assert scores == sorted(scores, reverse=True)


def test_confluence_engine_blocks_low_payout():
    result = ConfluenceEngineService().analyze(symbol="GBPUSD-OTC", payout=60, minimum_payout=75)

    assert result.status == "BLOCKED"
    assert any("Payout" in warning for warning in result.warnings)


def test_market_intelligence_service_supports_custom_symbols():
    result = MarketIntelligenceService().scan(symbols=["EURUSD-OTC", "GBPUSD-OTC"], top=2)

    assert result.assets_scanned == 2
    assert len(result.results) == 2
    assert {item.symbol for item in result.results}.issubset({"EURUSD-OTC", "GBPUSD-OTC"})
