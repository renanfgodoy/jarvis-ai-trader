from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "frontend/src/App.tsx"
NAVIGATION = ROOT / "frontend/src/hooks/useAppNavigation.ts"
SIDEBAR = ROOT / "frontend/src/components/Sidebar/index.tsx"
CORE_DEMO = ROOT / "frontend/src/pages/CoreDemo.tsx"
DEMO_SERVICE = ROOT / "frontend/src/services/demoService.ts"
USE_EXECUTION = ROOT / "frontend/src/hooks/useExecution.ts"
COMPONENTS_DIR = ROOT / "frontend/src/components/core-demo"
DOCS = ROOT / "docs/FRIDAY_CORE_DEMO.md"


def test_core_demo_route_and_navigation_are_registered() -> None:
    app = APP.read_text()
    navigation = NAVIGATION.read_text()
    sidebar = SIDEBAR.read_text()

    assert "CoreDemo" in app
    assert "route === '/developer/core-demo'" in app
    assert "'/developer/core-demo'" in navigation
    assert "Developer Console" in sidebar


def test_demo_service_calls_internal_core_demo_endpoint_only() -> None:
    source = DEMO_SERVICE.read_text()

    assert "/core/demo/execute" in source
    assert "provider: 'mock'" in source
    assert "openai" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "VITE_OPENAI_API_KEY" not in source


def test_use_execution_blocks_duplicate_execution_and_tracks_pipeline() -> None:
    source = USE_EXECUTION.read_text()

    assert "if (loading) return" in source
    assert "PipelineStep" in source
    assert "Validation" in source
    assert "Identity" in source
    assert "Prompt" in source
    assert "Provider" in source
    assert "Response" in source
    assert "AbortController" in source


def test_core_demo_components_consume_execution_response_contract() -> None:
    for name in [
        "ExecutionForm.tsx",
        "ExecutionPanel.tsx",
        "PipelineViewer.tsx",
        "DebugPanel.tsx",
        "ResponseCard.tsx",
        "StatusBadge.tsx",
        "SystemStatusCards.tsx",
        "ExecutionStatsCards.tsx",
        "ExecutionHistory.tsx",
        "ExecutionError.tsx",
        "ProviderConfigurationPanel.tsx",
        "ProviderHealthPanel.tsx",
    ]:
        assert (COMPONENTS_DIR / name).exists()

    page = CORE_DEMO.read_text()
    response_card = (COMPONENTS_DIR / "ResponseCard.tsx").read_text()
    debug_panel = (COMPONENTS_DIR / "DebugPanel.tsx").read_text()

    assert "useExecution" in page
    assert "ExecutionResponse" in response_card
    assert "ExecutionResponse" in debug_panel
    assert "IdentityResult" not in page + response_card + debug_panel
    assert "PromptResult" not in page + response_card + debug_panel
    assert "ExecutionContext" not in page + response_card + debug_panel
    assert "Provider Registry" in debug_panel
    assert "Provider Ativo" in debug_panel
    assert "Provider Health" in debug_panel
    assert "Model" in debug_panel
    assert "Capabilities" in debug_panel
    assert "ProviderConfigurationPanel" in debug_panel
    assert "ProviderHealthPanel" in debug_panel
    assert "Provider Configuration" in (COMPONENTS_DIR / "ProviderConfigurationPanel.tsx").read_text()
    assert "Feature Flags" in (COMPONENTS_DIR / "ProviderConfigurationPanel.tsx").read_text()


def test_developer_console_supports_trading_module_controls() -> None:
    form = (COMPONENTS_DIR / "ExecutionForm.tsx").read_text()
    types = (ROOT / "frontend/src/types/coreDemo.ts").read_text()
    response_card = (COMPONENTS_DIR / "ResponseCard.tsx").read_text()

    for term in ["Trading", "OTC", "Forex", "Crypto", "Trend", "Price Action", "Support Resistance", "SMC", "ICT"]:
        assert term in form
    assert "TradingResponse" in types
    assert "decision" in response_card
    assert "confidence" in response_card


def test_rc1_validation_ui_shows_final_success_report_history_and_latency() -> None:
    page = CORE_DEMO.read_text()
    hook = USE_EXECUTION.read_text()
    panel = (COMPONENTS_DIR / "ExecutionPanel.tsx").read_text()
    response_card = (COMPONENTS_DIR / "ResponseCard.tsx").read_text()
    pipeline = (COMPONENTS_DIR / "PipelineViewer.tsx").read_text()
    stats = (COMPONENTS_DIR / "ExecutionStatsCards.tsx").read_text()
    history = (COMPONENTS_DIR / "ExecutionHistory.tsx").read_text()
    status_cards = (COMPONENTS_DIR / "SystemStatusCards.tsx").read_text()

    assert "completePipeline" in hook
    assert "status: 'SUCCESS'" in hook
    assert "setHistory" in hook
    assert ".slice(0, 5)" in hook
    assert "SystemStatusCards" in page
    assert "ExecutionStatsCards" in page
    assert "ExecutionHistory" in panel
    assert "J.A.R.V.I.S Trading Report" in response_card
    for term in ["Mercado", "Ativo", "Timeframe", "Estrategia", "Trend", "Risk", "Confidence", "Decision", "Execution ID", "Request ID", "Fingerprint"]:
        assert term in response_card
    assert "Final {finalStatus}" in pipeline
    assert "Tempo Medio" in stats
    assert "latencyClassification" in stats
    assert "Ultimas Execucoes" in history
    assert "latency < 0.05" in hook
    assert "latency < 0.15" in hook
    assert "latency < 0.5" in hook
    assert "status: 'ERROR'" in hook
    for term in ["Core", "SDK", "Trading Module", "Identity Engine", "Prompt Engine", "Provider Engine", "Pipeline"]:
        assert term in status_cards
    assert "'WAITING' | 'RUNNING' | 'SUCCESS' | 'ERROR'" in (ROOT / "frontend/src/types/coreDemo.ts").read_text()


def test_core_demo_documentation_exists() -> None:
    docs = DOCS.read_text()

    assert "Friday Core Demo" in docs
    assert "CoreOrchestrator" in docs
    assert "MockProvider" in docs
    assert "ExecutionResponse" in docs
    assert "Release Candidate 1" in docs
    assert "Execution History" in docs
