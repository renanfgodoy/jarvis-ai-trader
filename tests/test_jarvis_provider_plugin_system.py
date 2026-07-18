from pathlib import Path

import pytest

from core.prompts import PromptEngine, PromptRequest
from core.providers import (
    BaseProvider,
    MockProvider,
    ProviderEngine,
    ProviderInvocation,
    ProviderLoader,
    ProviderManifest,
    ProviderMetadata,
    ProviderRegistry,
    ProviderRequest,
)
from core.providers.errors import ProviderNotFoundError
from core.providers.factory import ProviderFactory


def _prompt_package():
    return PromptEngine().build(
        PromptRequest(
            module="documents",
            template_id="core.generic_analysis",
            user_input="Teste o Provider Plugin System sem API externa.",
            request_id="provider-plugin-1",
        )
    )


def test_provider_plugin_contracts_are_typed_and_sanitized() -> None:
    request = ProviderRequest(
        identity="jarvis.default",
        prompt="Analise sem chamar API externa.",
        language="pt-BR",
        temperature=0,
        top_p=1,
        max_tokens=128,
        metadata={"source": "test"},
    )
    manifest = ProviderManifest(
        provider="mock",
        version="1.0",
        supported_models=("mock",),
        capabilities=("chat",),
        status="READY",
    )
    metadata = ProviderMetadata(fingerprint="abc", build="test", runtime="local")

    assert request.identity == "jarvis.default"
    assert request.timestamp.tzinfo is not None
    assert manifest.provider == "mock"
    assert metadata.runtime == "local"


def test_base_provider_plugin_lifecycle_manifest_metadata_and_response() -> None:
    provider = BaseProvider()

    assert provider.manifest().provider == "base"
    assert provider.initialized is False
    provider.initialize()
    assert provider.initialized is True
    assert provider.metadata().fingerprint

    response = provider.invoke(_prompt_package())

    assert response.provider == "base"
    assert response.content == response.response
    assert response.model == "mock"
    assert response.finish_reason == "stop"
    assert response.metadata["external_api_called"] is False

    provider.shutdown()
    assert provider.initialized is False


def test_provider_registry_registers_removes_defaults_and_health() -> None:
    registry = ProviderRegistry()
    registry.register(MockProvider(), default=True, active=True)

    assert registry.list() == ("mock",)
    assert registry.default().name == "mock"
    assert registry.default("mock").name == "mock"
    assert registry.health()["mock"].provider == "mock"
    assert registry.get("mock").initialized is True

    registry.remove("mock")

    assert registry.list() == ()
    with pytest.raises(ProviderNotFoundError):
        registry.default("mock")


def test_provider_loader_discovers_autoloads_and_uses_factory_only() -> None:
    factory = ProviderFactory()
    factory.register_builder("mock", MockProvider)
    loader = ProviderLoader(factory=factory)

    assert loader.discover() == ("mock",)

    registry = loader.autoload(default_provider="mock")

    assert registry.active().name == "mock"
    assert registry.get("mock").initialized is True


def test_mock_provider_is_migrated_to_plugin_package_without_behavior_change() -> None:
    provider = MockProvider()

    assert provider.manifest().provider == "mock"
    assert provider.manifest().supported_models == ("mock", "mock-trading")
    assert provider.capabilities() == ("chat", "json")

    response = provider.invoke(_prompt_package())

    assert response.provider == "mock"
    assert response.status == "placeholder"
    assert response.metadata["external_api_called"] is False


def test_provider_engine_routes_every_provider_through_registry_metadata() -> None:
    engine = ProviderEngine()
    response = engine.invoke(ProviderInvocation(prompt_package=_prompt_package(), provider="mock"))

    assert response.provider == "mock"
    assert response.metadata["active_provider"] == "mock"
    assert "mock" in response.metadata["provider_registry"]
    assert response.metadata["provider_health"] in {"UNKNOWN", "ONLINE", "OFFLINE", "DEGRADED", "LIMITED", "RATE_LIMITED"}
    assert response.metadata["provider_model"] == "mock"
    assert response.metadata["provider_capabilities"] == ("chat", "json")


def test_provider_plugin_system_documentation_exists() -> None:
    documentation = Path("docs/JARVIS_PROVIDER_SYSTEM.md").read_text(encoding="utf-8")

    assert "Provider Plugin System" in documentation
    assert "ProviderRegistry" in documentation
    assert "ProviderLoader" in documentation
    assert "MockProvider" in documentation
