from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
ROOT = Path(__file__).resolve().parents[1]


def test_vision_status_placeholder() -> None:
    response = client.get("/api/v1/vision/status")

    assert response.status_code == 200
    assert response.json()["mode"] == "VISION_FIRST"
    assert response.json()["analysis_available"] is True
    assert response.json()["provider"] == "openai"


def test_retired_broker_chart_routes_return_410() -> None:
    for path in ["/api/v1/market/chart", "/api/v1/market/chart/series", "/api/v1/market/provider-v2/status"]:
        response = client.get(path)
        assert response.status_code == 410
        assert response.json()["code"] == "BROKER_CHART_FEATURE_RETIRED"


def test_retired_broker_provider_routes_return_410() -> None:
    response = client.get("/api/v1/market/providers/iq-option/status")

    assert response.status_code == 410
    assert response.json()["code"] == "BROKER_PROVIDER_FEATURE_RETIRED"


def test_backend_lifespan_does_not_start_broker_runtime() -> None:
    source = (ROOT / "app/main.py").read_text()

    assert "polarium_cdp_live_source.start_background()" not in source
    assert "market_provider_manager.start_current()" not in source
    assert "Chrome" not in source


def test_frontend_routes_to_vision_without_broker_chart_polling() -> None:
    app_source = (ROOT / "frontend/src/App.tsx").read_text()
    navigation_source = (ROOT / "frontend/src/hooks/useAppNavigation.ts").read_text()
    sidebar_source = (ROOT / "frontend/src/components/Sidebar/index.tsx").read_text()

    assert "MarketChart" not in app_source
    assert "useRealCandles" not in app_source
    assert "MarketDataProvider" not in app_source
    assert "Friday Vision" in sidebar_source
    assert "'/market-chart' || pathname === '/analysis') return '/vision'" in navigation_source
