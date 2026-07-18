from pathlib import Path

import pytest

from core.prompts import PromptEngine, PromptRequest
from core.providers import (
    AnthropicProvider,
    FallbackPolicy,
    GoogleProvider,
    GroqProvider,
    LMStudioProvider,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
    ProviderCapabilityRegistry,
    ProviderConfig,
    ProviderEngine,
    ProviderFactory,
    ProviderInvocation,
    ProviderRegistry,
    RetryPolicy,
)
from core.providers.base import BaseProvider
from core.providers.errors import (
    DuplicateProviderError,
    InvalidProviderConfigError,
    ProviderCapabilityError,
    ProviderNotFoundError,
)
from core.providers.models import ProviderHealth
from core.providers.validators import ProviderValidator


def _prompt_package():
    return PromptEngine().build(
        PromptRequest(
            module="documents",
            template_id="core.generic_analysis",
            user_input="Organize esta solicitação sem chamar provider real.",
            request_id="prompt-1",
        )
    )


def test_provider_factory_registers_creates_lists_and_preserves_legacy_methods() -> None:
    factory = ProviderFactory()
    factory.register("mock", MockProvider)
    factory.register_builder("openai", OpenAIProvider)

    assert factory.list() == ("mock", "openai")
    assert factory.list_builders() == ("mock", "openai")
    assert factory.has_builder("mock")
    assert factory.create("mock").name == "mock"

    with pytest.raises(DuplicateProviderError):
        factory.register("mock", MockProvider)
    with pytest.raises(ProviderNotFoundError):
        factory.create("missing")


def test_provider_registry_registers_active_provider_versions_and_blocks_duplicates() -> None:
    registry = ProviderRegistry()
    registry.register(OpenAIProvider(), default=True, active=True)

    assert registry.get("openai").name == "openai"
    assert registry.list() == ("openai",)
    assert registry.list_versions("openai") == ("1.0",)
    assert registry.default_version("openai") == "1.0"
    assert registry.active().name == "openai"

    with pytest.raises(DuplicateProviderError):
        registry.register(OpenAIProvider())
    with pytest.raises(ProviderNotFoundError):
        registry.get("missing")


def test_placeholder_providers_declare_expected_capabilities_without_external_api() -> None:
    providers = [
        OpenAIProvider(),
        AnthropicProvider(),
        GoogleProvider(),
        GroqProvider(),
        OllamaProvider(),
        LMStudioProvider(),
    ]

    assert {provider.name for provider in providers} == {"openai", "anthropic", "google", "groq", "ollama", "lmstudio"}
    assert "vision" in OpenAIProvider().capabilities()
    assert "tool_use" in AnthropicProvider().capabilities()
    assert "local" in OllamaProvider().capabilities()

    for provider in providers:
        response = provider.invoke(_prompt_package())
        assert response.status == "not_configured"
        assert response.metadata["external_api_called"] is False


def test_capability_registry_validates_explicit_capabilities_only() -> None:
    capabilities = ProviderCapabilityRegistry()
    capabilities.register("openai", OpenAIProvider().capabilities())

    assert capabilities.supports("openai", "chat")
    assert capabilities.supports("openai", "vision")
    with pytest.raises(ProviderCapabilityError):
        capabilities.validate("openai", ("unsupported",))


def test_provider_validator_checks_config_provider_and_response() -> None:
    validator = ProviderValidator()
    validator.validate_config(ProviderConfig())
    validator.validate_provider(OpenAIProvider())
    validator.validate_response(OpenAIProvider().invoke(_prompt_package()))

    with pytest.raises(InvalidProviderConfigError):
        validator.validate_config(ProviderConfig(default_provider=""))
    with pytest.raises(InvalidProviderConfigError):
        validator.validate_config(ProviderConfig(retry_attempts=0))


def test_provider_engine_invokes_placeholder_and_normalizes_response() -> None:
    engine = ProviderEngine(config=ProviderConfig(default_provider="openai"))
    response = engine.invoke(ProviderInvocation(prompt_package=_prompt_package(), required_capabilities=("chat",)))

    assert response.provider == "openai"
    assert response.provider_version == "1.0"
    assert response.request_id == "prompt-1"
    assert response.status == "not_configured"
    assert response.latency >= 0
    assert response.usage.total_units > 0
    assert len(response.fingerprint) == 64
    assert response.metadata["external_api_called"] is False


def test_provider_engine_validates_capabilities_before_invocation() -> None:
    engine = ProviderEngine(config=ProviderConfig(default_provider="groq"))

    with pytest.raises(ProviderCapabilityError):
        engine.invoke(ProviderInvocation(prompt_package=_prompt_package(), required_capabilities=("vision",)))


def test_retry_policy_is_bounded() -> None:
    policy = RetryPolicy(enabled=True, max_attempts=2, recoverable_errors=(TimeoutError,))

    assert policy.should_retry(1, TimeoutError())
    assert not policy.should_retry(2, TimeoutError())
    assert not policy.should_retry(1, ValueError())
    assert not RetryPolicy(enabled=False).should_retry(1, TimeoutError())


def test_fallback_policy_is_optional_and_distinct() -> None:
    assert FallbackPolicy(enabled=False, fallback_provider="mock").next_provider("openai") is None
    assert FallbackPolicy(enabled=True, fallback_provider="openai").next_provider("openai") is None
    assert FallbackPolicy(enabled=True, fallback_provider="mock").next_provider("openai") == "mock"


def test_provider_engine_uses_fallback_when_primary_fails() -> None:
    class FailingProvider(BaseProvider):
        name = "failing"

        def invoke(self, prompt_package, *, request_id=None, metadata=None):
            raise TimeoutError("simulated timeout")

    registry = ProviderRegistry()
    registry.register(FailingProvider(), active=True)
    registry.register(MockProvider())
    capabilities = ProviderCapabilityRegistry()
    capabilities.register("failing", ("chat",))
    capabilities.register("mock", ("chat",))

    engine = ProviderEngine(
        registry=registry,
        capability_registry=capabilities,
        config=ProviderConfig(default_provider="failing", fallback_provider="mock"),
        fallback_policy=FallbackPolicy(enabled=True, fallback_provider="mock"),
    )

    response = engine.invoke(ProviderInvocation(prompt_package=_prompt_package(), required_capabilities=("chat",)))

    assert response.provider == "mock"
    assert response.status == "placeholder"
    assert response.metadata["fallback_used"] is True


def test_provider_health_contract_supports_known_statuses() -> None:
    health = ProviderHealth(provider="openai", status="UNKNOWN", detail="placeholder")

    assert health.provider == "openai"
    assert health.status == "UNKNOWN"
    assert health.checked_at.tzinfo is not None


def test_provider_engine_architecture_keeps_modules_identity_prompt_and_vision_out_of_providers() -> None:
    modules_source = "\n".join(path.read_text(encoding="utf-8") for path in Path("modules").rglob("*.py"))
    identity_source = "\n".join(path.read_text(encoding="utf-8") for path in Path("core/identity").rglob("*.py"))
    prompt_source = "\n".join(path.read_text(encoding="utf-8") for path in Path("core/prompts").rglob("*.py"))
    vision_source = "\n".join(path.read_text(encoding="utf-8") for path in Path("core/vision").rglob("*.py"))

    assert "core.providers" not in modules_source
    assert "core.providers" not in identity_source
    assert "core.providers" not in prompt_source
    assert "core.providers" not in vision_source


def test_provider_placeholders_do_not_import_network_clients_or_api_sdks() -> None:
    provider_source = "\n".join(path.read_text(encoding="utf-8") for path in Path("core/providers").rglob("*.py"))

    forbidden_terms = [
        "import requests",
        "requests.get",
        "requests.post",
        "httpx",
        "aiohttp",
        "urllib.request",
        "openai.",
        "anthropic.",
        "google.generativeai",
        "socketio",
        "websocket",
    ]
    for term in forbidden_terms:
        assert term not in provider_source


def test_provider_engine_documentation_exists() -> None:
    documentation = Path("docs/JARVIS_PROVIDER_ENGINE.md").read_text(encoding="utf-8")

    assert "J.A.R.V.I.S Provider Engine" in documentation
    assert "ProviderResponse" in documentation
    assert "openai" in documentation
