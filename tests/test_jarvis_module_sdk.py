from pathlib import Path

import pytest

from sdk import (
    BaseModule,
    ModuleConfig,
    ModuleLoader,
    ModuleManifest,
    ModuleMetadata,
    ModuleRegistry,
    ModuleRequest,
    ModuleResponse,
    ModuleValidator,
)
from sdk.exceptions import ModuleLoaderException, ModuleManifestException, ModuleRegistryException, ModuleValidationException


def _manifest(name: str = "documents") -> ModuleManifest:
    return ModuleManifest(
        name=name,
        display_name="Documents",
        description="Documents module test double.",
        identity="jarvis.default",
        provider="mock",
        language="pt-BR",
    )


def _module(name: str = "documents") -> BaseModule:
    return BaseModule(
        manifest=_manifest(name),
        metadata=ModuleMetadata(module=name, tags=("test",)),
    )


def test_module_manifest_request_metadata_and_config_contracts() -> None:
    manifest = _manifest()
    metadata = ModuleMetadata(module="documents", tags=("sdk",))
    request = ModuleRequest(module="documents", payload="Explique a arquitetura.")
    config = ModuleConfig()

    assert manifest.name == "documents"
    assert manifest.provider == "mock"
    assert metadata.fingerprint
    assert request.timestamp.tzinfo is not None
    assert config.enabled is True
    assert config.strict_validation is True


def test_module_validator_rejects_invalid_contracts_without_silent_fallback() -> None:
    validator = ModuleValidator()
    validator.validate_manifest(_manifest())
    validator.validate_metadata(ModuleMetadata(module="documents"))
    validator.validate_request(ModuleRequest(module="documents", payload="ok"))

    with pytest.raises(ModuleManifestException):
        validator.validate_manifest(ModuleManifest(name="", display_name="x", description="x"))
    with pytest.raises(ModuleManifestException):
        validator.validate_manifest(ModuleManifest(name="x", display_name="x", description="x", provider="openai"))
    with pytest.raises(ModuleValidationException):
        validator.validate_request(ModuleRequest(module="documents", payload=""))


def test_base_module_executes_only_through_core_orchestrator_and_returns_module_response() -> None:
    module = _module()
    module.initialize()
    response = module.execute(
        ModuleRequest(
            module="documents",
            payload="Execute pelo Module SDK.",
            metadata={"test": True},
        )
    )

    assert isinstance(response, ModuleResponse)
    assert response.status == "SUCCESS"
    assert response.module == "documents"
    assert response.provider == "mock"
    assert response.execution.provider_response.metadata["external_api_called"] is False
    assert response.execution.provider_response.metadata["module_sdk"] is True
    assert response.metadata["execution_id"] == response.execution.metadata.execution_id
    module.shutdown()
    assert module.initialized is False


def test_module_registry_registers_lists_gets_removes_and_blocks_duplicates() -> None:
    registry = ModuleRegistry()
    documents = _module("documents")
    finance = _module("finance")

    registry.register(documents, default=True)
    registry.register(finance)

    assert registry.list() == ("documents", "finance")
    assert registry.get("documents") is documents
    assert registry.exists("finance")
    assert registry.default() is documents

    with pytest.raises(ModuleRegistryException):
        registry.register(_module("documents"))
    registry.unregister("documents")
    assert registry.list() == ("finance",)
    registry.clear()
    assert registry.list() == ()


def test_module_loader_loads_validates_registers_and_initializes_modules() -> None:
    registry = ModuleRegistry()
    loader = ModuleLoader(registry=registry, config=ModuleConfig(auto_register=True, auto_initialize=True))
    loader.register_builder("documents", lambda: _module("documents"))

    module = loader.load("documents")

    assert module.initialized is True
    assert registry.get("documents") is module
    assert loader.list_builders() == ("documents",)

    with pytest.raises(ModuleLoaderException):
        loader.register_builder("documents", lambda: _module("documents"))
    with pytest.raises(ModuleLoaderException):
        loader.load("missing")


def test_module_sdk_documentation_exists() -> None:
    docs = Path("docs/JARVIS_MODULE_SDK.md").read_text(encoding="utf-8")

    assert "J.A.R.V.I.S Module SDK" in docs
    assert "ModuleManifest" in docs
    assert "ModuleRequest" in docs
    assert "ModuleResponse" in docs


def test_modules_use_sdk_and_do_not_access_engines_or_providers_directly() -> None:
    module_files = [path for path in Path("modules").rglob("*.py") if "__pycache__" not in str(path)]
    module_source = "\n".join(path.read_text(encoding="utf-8") for path in module_files)

    assert "from sdk" in Path("modules/base.py").read_text(encoding="utf-8")
    forbidden_terms = [
        "core.orchestrator",
        "core.identity",
        "core.prompts",
        "core.providers",
        "IdentityEngine",
        "PromptEngine",
        "ProviderEngine",
        "CoreOrchestrator",
        "OpenAIProvider",
        "MockProvider",
    ]
    for term in forbidden_terms:
        assert term not in module_source
