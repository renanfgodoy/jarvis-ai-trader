from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK_SOURCE = ROOT / "frontend/src/hooks/useRealCandles.ts"
MARKET_CHART_SOURCE = ROOT / "frontend/src/pages/MarketChart.tsx"


def test_provider_v2_status_and_neutral_chart_params_are_used() -> None:
    source = HOOK_SOURCE.read_text()

    assert "/market/provider-v2/status" in source
    assert "provider: 'POCKET'" in source
    assert "symbol: selectedSymbol" in source
    assert "period: String(selectedPeriod)" in source
    assert "PROVIDER_V2_ACTIVE_KEY_MISMATCH" in source


def test_market_chart_displays_pocket_read_only_without_cross_provider_label() -> None:
    source = MARKET_CHART_SOURCE.read_text()

    assert "pocketProviderActive" in source
    assert "Provider: Pocket — Read Only" in source
    assert "selectedChartSource: ChartBindingSelectedSource = pocketProviderActive" in source
    assert "POLARIUM_BASELINE_MODE" in source
