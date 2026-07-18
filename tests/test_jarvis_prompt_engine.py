from pathlib import Path

import pytest

from core.prompts import PromptEngine, PromptRequest
from core.prompts.estimator import estimate_prompt_size
from core.prompts.exceptions import (
    DuplicatePromptTemplateError,
    InvalidPromptMessageError,
    InvalidPromptRequestError,
    PromptSizeLimitExceededError,
    PromptTemplateNotFoundError,
    PromptTemplateVersionNotFoundError,
)
from core.prompts.models import PromptEngineConfig, PromptMessage
from core.prompts.registry import PromptTemplateRegistry
from core.prompts.templates import CoreSystemTemplate, GenericAnalysisTemplate, GenericStructuredResponseTemplate


def test_prompt_request_validates_required_fields_and_defaults() -> None:
    request = PromptRequest(module="trading", template_id="core.generic_analysis", user_input="Analyze this.")

    assert request.language == "pt-BR"
    assert request.response_format == "text"
    assert request.context == {}
    assert request.metadata == {}

    with pytest.raises(InvalidPromptRequestError):
        PromptRequest(module="", template_id="core.generic_analysis")
    with pytest.raises(InvalidPromptRequestError):
        PromptRequest(module="trading", template_id="")
    with pytest.raises(InvalidPromptRequestError):
        PromptRequest(module="trading", template_id="core.generic_analysis", context=None)  # type: ignore[arg-type]


def test_prompt_message_accepts_only_known_roles() -> None:
    for role in ("system", "developer", "user", "assistant"):
        assert PromptMessage(role=role, content="content").role == role

    with pytest.raises(InvalidPromptMessageError):
        PromptMessage(role="tool", content="content")
    with pytest.raises(InvalidPromptMessageError):
        PromptMessage(role="user", content=" ")


def test_prompt_template_registry_registers_finds_lists_and_rejects_duplicates() -> None:
    registry = PromptTemplateRegistry()
    registry.register(CoreSystemTemplate(), default=True)

    assert registry.get("core.system").template_id == "core.system"
    assert registry.get("core.system", "1.0").version == "1.0"
    assert registry.list_templates() == ("core.system",)
    assert registry.list_versions("core.system") == ("1.0",)
    assert registry.default_version("core.system") == "1.0"

    with pytest.raises(DuplicatePromptTemplateError):
        registry.register(CoreSystemTemplate())
    with pytest.raises(PromptTemplateNotFoundError):
        registry.get("missing")
    with pytest.raises(PromptTemplateVersionNotFoundError):
        registry.get("core.system", "9.9")


def test_prompt_engine_builds_package_with_metadata_estimate_timestamp_and_request_id() -> None:
    engine = PromptEngine()
    request = PromptRequest(
        module="trading",
        template_id="core.generic_analysis",
        user_input="Analise apenas este texto.",
        context={"source": "unit-test"},
        metadata={"trace": "safe"},
        request_id="req-123",
    )

    package = engine.build(request)

    assert package.request_id == "req-123"
    assert package.module == "trading"
    assert package.template_id == "core.generic_analysis"
    assert package.template_version == "1.0"
    assert len(package.messages) == 2
    assert package.estimated_size.character_count > 0
    assert package.estimated_size.message_count == 2
    assert package.created_at.tzinfo is not None
    assert len(package.fingerprint) == 64
    assert package.metadata["language"] == "pt-BR"
    assert package.metadata["trace"] == "safe"


def test_prompt_engine_uses_requested_template_and_version() -> None:
    engine = PromptEngine()
    package = engine.build(
        PromptRequest(
            module="documents",
            template_id="core.structured_response",
            template_version="1.0",
            user_input="Organize as informações.",
            response_format="structured",
        )
    )

    assert package.template_id == "core.structured_response"
    assert package.template_version == "1.0"
    assert [message.role for message in package.messages] == ["system", "developer", "user"]
    assert package.metadata["response_format"] == "structured"


def test_prompt_engine_sanitizes_input_without_aggressive_rewrite() -> None:
    engine = PromptEngine()
    package = engine.build(
        PromptRequest(
            module="marketing",
            template_id="core.generic_analysis",
            user_input=" Linha 1\x00   com   espaços\r\n\r\n\r\nLinha 2 ",
        )
    )

    content = package.messages[-1].content
    assert "\x00" not in content
    assert "Linha 1 com espaços" in content
    assert "\r" not in content


def test_fingerprint_is_deterministic_and_ignores_request_id_and_created_at() -> None:
    engine = PromptEngine()
    first = engine.build(PromptRequest(module="finance", template_id="core.generic_analysis", user_input="Mesmo texto.", request_id="a"))
    second = engine.build(PromptRequest(module="finance", template_id="core.generic_analysis", user_input="Mesmo texto.", request_id="b"))

    assert first.fingerprint == second.fingerprint
    assert first.request_id != second.request_id


def test_prompt_engine_rejects_size_limits_and_missing_required_template_fields() -> None:
    engine = PromptEngine(config=PromptEngineConfig(max_input_characters=5))

    with pytest.raises(PromptSizeLimitExceededError):
        engine.build(PromptRequest(module="crm", template_id="core.generic_analysis", user_input="muito grande"))

    with pytest.raises(InvalidPromptRequestError):
        PromptEngine().build(PromptRequest(module="crm", template_id="core.generic_analysis"))


def test_initial_templates_build_expected_messages() -> None:
    request = PromptRequest(module="automation", template_id="core.system", user_input="ignored")

    assert CoreSystemTemplate().build(request)[0].role == "system"
    assert len(GenericAnalysisTemplate().build(PromptRequest(module="automation", template_id="core.generic_analysis", user_input="x"))) == 2
    assert len(GenericStructuredResponseTemplate().build(PromptRequest(module="automation", template_id="core.structured_response", user_input="x"))) == 3


def test_estimator_uses_simple_documented_token_approximation() -> None:
    estimate = estimate_prompt_size((PromptMessage(role="user", content="abcd efgh"),), characters_per_token=4)

    assert estimate.character_count == 9
    assert estimate.word_count == 2
    assert estimate.estimated_tokens == 3
    assert estimate.message_count == 1


def test_trading_module_can_request_prompt_without_provider_access() -> None:
    from modules.trading.module import TradingModule

    module = TradingModule()
    engine = PromptEngine()
    package = engine.build(
        PromptRequest(
            module=module.name,
            template_id="core.generic_analysis",
            user_input="Explique os dados fornecidos sem decisão operacional.",
        )
    )

    assert package.module == "trading"
    assert package.template_id == "core.generic_analysis"


def test_prompt_engine_architecture_has_no_provider_or_network_dependency() -> None:
    prompt_sources = "\n".join(path.read_text(encoding="utf-8") for path in Path("core/prompts").rglob("*.py"))

    forbidden_terms = [
        "OpenAI",
        "core.providers",
        "requests.",
        "httpx",
        "aiohttp",
        "urllib",
        "socket",
        "websocket",
    ]
    for term in forbidden_terms:
        assert term not in prompt_sources


def test_modules_do_not_import_providers_directly_after_prompt_engine() -> None:
    for path in Path("modules").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "core.providers" not in source
        assert "OpenAIProvider" not in source
        assert "MockProvider" not in source


def test_prompt_engine_documentation_exists() -> None:
    documentation = Path("docs/JARVIS_PROMPT_ENGINE.md").read_text(encoding="utf-8")

    assert "J.A.R.V.I.S Prompt Engine" in documentation
    assert "PromptRequest" in documentation
    assert "PromptPackage" in documentation
