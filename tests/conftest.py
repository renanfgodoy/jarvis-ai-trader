from __future__ import annotations

from pathlib import Path


ARCHIVED_BROKER_TEST_FILES = {
    "tests/api/test_iq_option_realtime_stream_route.py",
    "tests/connector/polarium/live_session/test_authorized_session_runtime_foundation.py",
    "tests/market/chart/test_market_chart_route.py",
    "tests/market/chart/test_market_chart_runtime_shared_store.py",
    "tests/market/chart/test_provider_v2_chart_route.py",
    "tests/market/persistence/test_candle_integrity_audit.py",
    "tests/market/persistence/test_local_candle_persistence.py",
    "tests/market/providers/test_iq_option_read_only_provider.py",
    "tests/market/runtime/test_authorized_browser_bridge_runtime.py",
    "tests/market/runtime/test_controlled_candle_stream_simulator.py",
    "tests/market/runtime/test_controlled_runtime_feed.py",
    "tests/test_ai_decision.py",
    "tests/test_asset_scanner.py",
    "tests/test_autotrade_gate.py",
    "tests/test_execution_engine.py",
    "tests/test_live_market_engine.py",
    "tests/test_live_workspace.py",
    "tests/test_market_intelligence.py",
    "tests/test_market_reader.py",
    "tests/test_polarium_connector.py",
    "tests/test_polarium_diagnostics.py",
    "tests/test_polarium_direct_login_lab.py",
    "tests/test_polarium_oauth_lab.py",
    "tests/test_provider_engine.py",
    "tests/test_provider_manager.py",
    "tests/test_quadcode_demo.py",
    "tests/test_real_market_data_foundation.py",
    "tests/test_signal_engine.py",
}


def pytest_ignore_collect(collection_path: Path, config) -> bool:  # type: ignore[no-untyped-def]
    path = Path(collection_path).as_posix()
    for archived_path in ARCHIVED_BROKER_TEST_FILES:
        if path.endswith(archived_path):
            return True
    return False
