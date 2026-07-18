from pathlib import Path

import pytest

from core.identity import IdentityEngine, IdentityRequest
from core.identity.builder import IdentityBuilder
from core.identity.config import IdentityConfig
from core.identity.exceptions import (
    DuplicateIdentityError,
    IdentityNotFoundError,
    IdentityVersionNotFoundError,
    InvalidIdentityProfileError,
    InvalidIdentityRequestError,
)
from core.identity.models import IdentityProfile
from core.identity.profiles import official_identity_profiles
from core.identity.registry import IdentityRegistry
from core.identity.resolver import IdentityResolver
from core.identity.validators import IdentityValidator


def test_identity_request_validates_required_module_and_mappings() -> None:
    request = IdentityRequest(module="trading", metadata={"trace": "safe"}, context={"source": "test"})

    assert request.module == "trading"
    assert request.requested_identity is None

    with pytest.raises(InvalidIdentityRequestError):
        IdentityRequest(module="")
    with pytest.raises(InvalidIdentityRequestError):
        IdentityRequest(module="trading", metadata=None)  # type: ignore[arg-type]
    with pytest.raises(InvalidIdentityRequestError):
        IdentityRequest(module="trading", context=None)  # type: ignore[arg-type]


def test_official_profiles_are_exactly_the_four_requested_profiles() -> None:
    profiles = official_identity_profiles()

    assert {profile.identity_id for profile in profiles} == {
        "jarvis.default",
        "jarvis.trading",
        "jarvis.marketing",
        "jarvis.finance",
    }
    assert {profile.version for profile in profiles} == {"1.0"}
    assert all(profile.fingerprint for profile in profiles)


def test_identity_validator_rejects_invalid_profile_and_request_values() -> None:
    validator = IdentityValidator()
    profile = official_identity_profiles()[0]

    validator.validate_profile(profile)
    validator.validate_request(IdentityRequest(module="finance", language="pt-BR"))

    with pytest.raises(InvalidIdentityProfileError):
        validator.validate_profile(IdentityProfile(**{**profile.__dict__, "identity_id": ""}))
    with pytest.raises(InvalidIdentityProfileError):
        validator.validate_profile(IdentityProfile(**{**profile.__dict__, "principles": ()}))
    with pytest.raises(InvalidIdentityRequestError):
        validator.validate_request(IdentityRequest(module="unknown"))
    with pytest.raises(InvalidIdentityRequestError):
        validator.validate_request(IdentityRequest(module="finance", language="fr-FR"))


def test_identity_registry_registers_lists_versions_and_blocks_duplicates() -> None:
    registry = IdentityRegistry()
    profile = official_identity_profiles()[0]
    registry.register(profile, default=True)

    assert registry.get("jarvis.default").identity_id == "jarvis.default"
    assert registry.get("jarvis.default", "1.0").version == "1.0"
    assert registry.list_identities() == ("jarvis.default",)
    assert registry.list_versions("jarvis.default") == ("1.0",)
    assert registry.default_version("jarvis.default") == "1.0"

    with pytest.raises(DuplicateIdentityError):
        registry.register(profile)
    with pytest.raises(IdentityNotFoundError):
        registry.get("missing")
    with pytest.raises(IdentityVersionNotFoundError):
        registry.get("jarvis.default", "9.9")


def test_resolver_uses_default_identity_without_silent_fallback_for_unknown_identity() -> None:
    engine = IdentityEngine()

    default_result = engine.resolve(IdentityRequest(module="documents", request_id="req-1"))
    assert default_result.resolved_identity == "jarvis.default"
    assert default_result.request_id == "req-1"

    trading_result = engine.resolve(IdentityRequest(module="trading", requested_identity="jarvis.trading"))
    assert trading_result.identity_profile.identity_id == "jarvis.trading"

    with pytest.raises(IdentityNotFoundError):
        engine.resolve(IdentityRequest(module="trading", requested_identity="jarvis.unknown"))


def test_resolver_applies_supported_language_without_mutating_registered_profile() -> None:
    engine = IdentityEngine()
    result = engine.resolve(IdentityRequest(module="finance", requested_identity="jarvis.finance", language="en-US"))

    assert result.identity_profile.language == "en-US"
    assert engine.registry.get("jarvis.finance").language == "pt-BR"


def test_builder_produces_identity_result_with_metadata_timestamp_and_fingerprint() -> None:
    profile = official_identity_profiles()[1]
    request = IdentityRequest(module="trading", requested_identity="jarvis.trading", metadata={"trace": "abc"}, request_id="req-x")
    result = IdentityBuilder().build(request, profile)

    assert result.request_id == "req-x"
    assert result.resolved_identity == "jarvis.trading"
    assert result.metadata["trace"] == "abc"
    assert result.metadata["resolver_version"] == "1.0"
    assert result.timestamp.tzinfo is not None
    assert len(result.fingerprint) == 64


def test_identity_result_fingerprint_is_deterministic_and_excludes_request_id_and_timestamp() -> None:
    engine = IdentityEngine()
    first = engine.resolve(IdentityRequest(module="marketing", requested_identity="jarvis.marketing", request_id="a"))
    second = engine.resolve(IdentityRequest(module="marketing", requested_identity="jarvis.marketing", request_id="b"))

    assert first.fingerprint == second.fingerprint
    assert first.request_id != second.request_id


def test_identity_engine_does_not_build_prompt_messages_or_call_provider() -> None:
    result = IdentityEngine().resolve(IdentityRequest(module="crm"))

    assert result.identity_profile.identity_id == "jarvis.default"
    assert not hasattr(result, "messages")


def test_identity_engine_architecture_has_no_forbidden_dependencies() -> None:
    identity_sources = "\n".join(path.read_text(encoding="utf-8") for path in Path("core/identity").rglob("*.py"))

    forbidden_terms = [
        "core.providers",
        "core.prompts",
        "core.vision",
        "core.memory",
        "OpenAI",
        "import requests",
        "requests.get",
        "requests.post",
        "httpx",
        "aiohttp",
        "urllib",
        "socket",
        "websocket",
    ]
    for term in forbidden_terms:
        assert term not in identity_sources


def test_modules_do_not_import_providers_or_define_personality_directly() -> None:
    forbidden_terms = ["core.providers", "OpenAIProvider", "MockProvider", "Você é um especialista"]
    for path in Path("modules").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        for term in forbidden_terms:
            assert term not in source


def test_identity_engine_documentation_exists() -> None:
    documentation = Path("docs/JARVIS_IDENTITY_ENGINE.md").read_text(encoding="utf-8")

    assert "J.A.R.V.I.S Identity Engine" in documentation
    assert "IdentityProfile" in documentation
    assert "jarvis.default@1.0" in documentation
