from __future__ import annotations

import pytest

from app.market.providers.manager import (
    POCKET_CHART_UNSAFE_CONFIGURATION,
    ProviderManager,
    ProviderManagerConfig,
)


def test_provider_manager_does_not_start_pocket_by_default(tmp_path) -> None:
    manager = ProviderManager(ProviderManagerConfig(), diagnostics_path=tmp_path)

    manager.initialize()
    manager.start_current()

    status = manager.status()
    assert status.enabled is False
    assert status.current_provider == "POLARIUM"
    assert status.registered_providers == ()
    assert status.running_providers == ()


def test_provider_manager_blocks_unsafe_pocket_chart_configuration(tmp_path) -> None:
    manager = ProviderManager(
        ProviderManagerConfig(provider_v2_enabled=True, current_provider="POCKET", pocket_chart_integration_enabled=True),
        diagnostics_path=tmp_path,
    )

    manager.initialize()

    with pytest.raises(RuntimeError, match=POCKET_CHART_UNSAFE_CONFIGURATION):
        manager.start_current()

    assert manager.status().last_error_code == POCKET_CHART_UNSAFE_CONFIGURATION
    assert (tmp_path / "pocket_chart_integration_report.json").exists()


def test_provider_manager_registers_pocket_without_auto_starting(tmp_path) -> None:
    manager = ProviderManager(
        ProviderManagerConfig(provider_v2_enabled=True, current_provider="POCKET"),
        diagnostics_path=tmp_path,
    )

    manager.initialize()

    assert manager.registry.exists("POCKET") is True
    assert manager.current_provider() is manager.registry.get("POCKET")
    assert manager.status().provider_running is False
