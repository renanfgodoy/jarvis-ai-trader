from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from app.api.routes import market_chart
from app.main import app
from app.market.chart.models import ChartCandle
from app.market.chart.provider_service import ProviderChartReadiness, ProviderChartSeries, ProviderChartSeriesSummary


client = TestClient(app)


@dataclass
class FakeStatus:
    current_provider: str = "POCKET"


class FakeProviderManager:
    def __init__(self) -> None:
        self.diagnostics: dict | None = None

    def status(self) -> FakeStatus:
        return FakeStatus()

    def write_diagnostics(self, payload: dict) -> None:
        self.diagnostics = payload


class FakeProviderChartService:
    def get_available_series(self, *, provider_name: str | None = None):
        return (
            ProviderChartSeriesSummary(
                provider="POCKET",
                symbol="EURUSD_otc",
                period=300,
                timeframe="M5",
                count=1,
                latest_time=1_700_000_000,
                readiness="READY",
            ),
        )

    def get_series(self, *, provider_name: str | None, symbol: str | None, period: int | None, limit: int):
        return ProviderChartSeries(
            provider="POCKET",
            symbol=symbol or "EURUSD_otc",
            period=period or 300,
            timeframe="M5",
            readiness=ProviderChartReadiness("READY", 55, 50, False, None),
            candles=(ChartCandle(1_700_000_000, 1.0, 1.2, 0.9, 1.1),),
        )


def test_provider_v2_chart_route_uses_neutral_provider_params(monkeypatch) -> None:
    fake_manager = FakeProviderManager()
    monkeypatch.setattr(market_chart.settings, "market_provider_v2_enabled", True)
    monkeypatch.setattr(market_chart, "market_provider_manager", fake_manager)
    monkeypatch.setattr(market_chart, "market_chart_provider_service", FakeProviderChartService())

    response = client.get(
        "/api/v1/market/chart",
        params={"provider": "POCKET", "symbol": "EURUSD_otc", "period": 300, "limit": 200},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "POCKET"
    assert payload["active_id"] is None
    assert payload["symbol"] == "EURUSD_otc"
    assert payload["period"] == 300
    assert payload["readiness"]["state"] == "READY"
    assert payload["candles"][0]["timestamp"] == 1_700_000_000
    assert fake_manager.diagnostics["frontend_active_key"] == "POCKET:EURUSD_otc:300"


def test_provider_v2_series_route_lists_provider_keys(monkeypatch) -> None:
    monkeypatch.setattr(market_chart.settings, "market_provider_v2_enabled", True)
    monkeypatch.setattr(market_chart, "market_provider_manager", FakeProviderManager())
    monkeypatch.setattr(market_chart, "market_chart_provider_service", FakeProviderChartService())

    response = client.get("/api/v1/market/chart/series")

    assert response.status_code == 200
    assert response.json()["series"] == [
        {
            "provider": "POCKET",
            "active_id": None,
            "symbol": "EURUSD_otc",
            "raw_size": 300,
            "period": 300,
            "timeframe": "M5",
            "count": 1,
            "latest_time": 1_700_000_000,
            "readiness": "READY",
        }
    ]
