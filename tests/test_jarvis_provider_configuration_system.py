from pathlib import Path

import pytest

from core.prompts import PromptEngine, PromptRequest
from core.providers import (
    FeatureFlags,
    MockProvider,
    ProviderConfiguration,
    ProviderEngine,
    ProviderHealthManager,
    ProviderInvocation,
    ProviderRegistry,
    ProviderResolver,
    ProviderSettings,
)
from core.providers.errors import ProviderNotFoundError


def _prompt_package():
    return PromptEngine().build(
        PromptRequest(
            module="documents",
            template_id="core.generic_analysis",
            user_input="Valide Provider Configuration sem API externa.",
            request_id="provider-config-1",
        )
    )


def test_provider_configuration_defaults_to_mock_only() -> None:
    configuration = ProviderConfiguration()

    assert configuration.default_provider == "mock"
    assert configuration.settings.enabled_providers == ("mock",)
    assert configuration.settings.fallback_enabled is True
    assert configuration.feature_flags.mock is True
    assert configuration.feature_flags.openai is False
    assert configuration.feature_flags.gemini is False
    assert configuration.environment.normalized_name == "development"


def test_provider_configuration_reads_environment_without_enabling_real_providers_by_default() -> None:
    configuration = ProviderConfiguration.from_environment(
        {
            "FRIDAY_PROVIDER_DEFAULT": "mock",
            "FRIDAY_PROVIDER_OPENAI_ENABLED": "false",
            "FRIDAY_PROVIDER_FALLBACK_ENABLED": "true",
            "FRIDAY_PROVIDER_PRIORITY": "mock,openai",
            "FRIDAY_ENVIRONMENT": "test",
        }
    )

    assert configuration.settings.default_provider == "mock"
    assert configuration.settings.provider_priority == ("mock", "openai")
    assert configuration.feature_flags.openai is False
    assert configuration.environment.normalized_name == "test"


def test_feature_flags_enable_only_mock_by_default() -> None:
    flags = FeatureFlags()

    assert flags.enabled("mock")
    assert not flags.enabled("openai")
    assert not flags.enabled("gemini")
    assert flags.enabled_providers() == ("mock",)


def test_provider_resolver_uses_default_priority_and_registry() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider(), default=True, active=True)
    resolver = ProviderResolver(registry=registry)

    resolution = resolver.resolve()

    assert resolution.selected_provider == "mock"
    assert resolution.reason == "DEFAULT"
    assert resolution.fallback_used is False


def test_provider_resolver_falls_back_when_requested_provider_is_disabled() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider(), default=True, active=True)
    resolver = ProviderResolver(registry=registry)

    resolution = resolver.resolve("openai")

    assert resolution.requested_provider == "openai"
    assert resolution.selected_provider == "mock"
    assert resolution.reason == "FALLBACK"
    assert resolution.fallback_used is True


def test_provider_resolver_blocks_when_no_provider_is_available() -> None:
    configuration = ProviderConfiguration(settings=ProviderSettings(enabled_providers=("mock",), fallback_enabled=False))
    resolver = ProviderResolver(configuration=configuration, registry=ProviderRegistry())

    with pytest.raises(ProviderNotFoundError):
        resolver.resolve("openai")


def test_provider_health_manager_tracks_request_count_latency_and_errors() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider(), default=True, active=True)
    manager = ProviderHealthManager(registry=registry)

    manager.record_execution("mock", 0.1)
    state = manager.record_execution("mock", 0.3)

    assert state.status == "ONLINE"
    assert state.request_count == 2
    assert state.latency_average == pytest.approx(0.2)
    assert state.last_error is None

    error_state = manager.record_execution("mock", 0.0, error=TimeoutError())

    assert error_state.status == "DEGRADED"
    assert error_state.last_error == "TimeoutError"


def test_provider_engine_uses_configuration_layer_and_keeps_mock_as_default_provider() -> None:
    response = ProviderEngine().invoke(ProviderInvocation(prompt_package=_prompt_package()))

    configuration = response.metadata["provider_configuration"]
    feature_flags = response.metadata["provider_feature_flags"]

    assert response.provider == "mock"
    assert response.metadata["active_provider"] == "mock"
    assert configuration["default_provider"] == "mock"
    assert configuration["fallback_enabled"] is True
    assert feature_flags["mock"] is True
    assert feature_flags["openai"] is False
    assert response.metadata["provider_fallback_enabled"] is True
    assert response.metadata["provider_health_summary"]["mock"]["request_count"] == 1


def test_provider_configuration_documentation_exists() -> None:
    documentation = Path("docs/JARVIS_PROVIDER_CONFIGURATION.md").read_text(encoding="utf-8")

    assert "Provider Configuration System" in documentation
    assert "ProviderResolver" in documentation
    assert "FeatureFlags" in documentation
    assert "ProviderHealthManager" in documentation
