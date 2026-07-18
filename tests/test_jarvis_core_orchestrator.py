from pathlib import Path

import pytest

from core.orchestrator import CoreOrchestrator, ExecutionConfig, ExecutionContext, ExecutionPipeline, ExecutionRequest
from core.orchestrator.events import (
    EVENT_EXECUTION_FINISHED,
    EVENT_IDENTITY_RESOLVED,
    EVENT_PROMPT_BUILT,
    EVENT_PROVIDER_EXECUTED,
    EVENT_PROVIDER_SELECTED,
    EVENT_RESPONSE_NORMALIZED,
)
from core.orchestrator.exceptions import ConfigurationException, PipelineException, ValidationException
from core.orchestrator.hooks import ExecutionHooks
from core.orchestrator.metadata import build_execution_metadata
from core.orchestrator.models import ExecutionResponse
from core.orchestrator.pipeline import BasePipelineStage
from core.orchestrator.validators import ExecutionValidator


def _request(**overrides) -> ExecutionRequest:
    data = {
        "request_id": "exec-1",
        "module": "documents",
        "input": "Organize esta solicitação sem chamar API externa.",
        "identity": "jarvis.default",
        "provider": "mock",
        "language": "pt-BR",
        "metadata": {"trace": "safe"},
    }
    data.update(overrides)
    return ExecutionRequest(**data)


def test_core_orchestrator_executes_full_local_pipeline() -> None:
    response = CoreOrchestrator().execute(_request())

    assert isinstance(response, ExecutionResponse)
    assert response.request_id == "exec-1"
    assert response.identity == "jarvis.default"
    assert response.provider == "mock"
    assert response.status == "SUCCESS"
    assert response.provider_response.metadata["external_api_called"] is False
    assert response.metadata.module == "documents"
    assert response.metadata.pipeline_version == "1.0"
    assert len(response.fingerprint) == 64


def test_execution_context_is_ephemeral_and_collects_events() -> None:
    orchestrator = CoreOrchestrator()
    context = orchestrator.build_context(_request())

    assert isinstance(context, ExecutionContext)
    assert context.status == "PENDING"
    assert context.events[0].name == "ExecutionStarted"
    assert context.response is None


def test_execution_pipeline_runs_stages_in_order_and_sets_events() -> None:
    orchestrator = CoreOrchestrator()
    context = orchestrator.execute_pipeline(orchestrator.build_context(_request()))
    event_names = [event.name for event in context.events]

    assert event_names.index(EVENT_IDENTITY_RESOLVED) < event_names.index(EVENT_PROMPT_BUILT)
    assert event_names.index(EVENT_PROVIDER_SELECTED) < event_names.index(EVENT_PROVIDER_EXECUTED)
    assert EVENT_RESPONSE_NORMALIZED in event_names
    assert EVENT_EXECUTION_FINISHED in event_names
    assert context.pipeline_stage == "finalize_execution"


def test_execution_validator_rejects_invalid_request_and_config() -> None:
    validator = ExecutionValidator()
    validator.validate_request(_request())

    with pytest.raises(ValidationException):
        validator.validate_request(_request(request_id=""))
    with pytest.raises(ValidationException):
        validator.validate_request(_request(input=""))
    with pytest.raises(ValidationException):
        validator.validate_request(_request(response_format="xml"))
    with pytest.raises(ConfigurationException):
        ExecutionValidator(ExecutionConfig(pipeline_version=""))


def test_execution_metadata_has_status_duration_and_fingerprint() -> None:
    metadata = build_execution_metadata(
        request_id="exec-1",
        module="documents",
        pipeline_version="1.0",
        status="SUCCESS",
        started_at=_request().created_at,
        provider="mock",
        provider_version="1.0",
        identity="jarvis.default",
    )

    assert metadata.execution_id
    assert metadata.status == "SUCCESS"
    assert metadata.duration is not None
    assert len(metadata.fingerprint) == 64


def test_execution_hooks_are_called_without_side_effects() -> None:
    calls: list[str] = []

    class RecordingHooks(ExecutionHooks):
        def before_identity(self, context) -> None:
            calls.append("before_identity")

        def after_identity(self, context) -> None:
            calls.append("after_identity")

        def before_prompt(self, context) -> None:
            calls.append("before_prompt")

        def after_prompt(self, context) -> None:
            calls.append("after_prompt")

        def before_provider(self, context) -> None:
            calls.append("before_provider")

        def after_provider(self, context) -> None:
            calls.append("after_provider")

    CoreOrchestrator(hooks=RecordingHooks()).execute(_request())

    assert calls == [
        "before_identity",
        "after_identity",
        "before_prompt",
        "after_prompt",
        "before_provider",
        "after_provider",
    ]


def test_execution_pipeline_requires_stages_and_rolls_back_on_failure() -> None:
    with pytest.raises(PipelineException):
        ExecutionPipeline(())

    rolled_back: list[str] = []

    class GoodStage(BasePipelineStage):
        stage_name = "good"

        def execute(self, context):
            return context

        def rollback(self, context) -> None:
            rolled_back.append("good")

    class BadStage(BasePipelineStage):
        stage_name = "bad"

        def execute(self, context):
            raise RuntimeError("boom")

    pipeline = ExecutionPipeline((GoodStage(), BadStage()))

    with pytest.raises(RuntimeError):
        pipeline.execute(ExecutionContext(request=_request()))

    assert rolled_back == ["good"]


def test_orchestrator_does_not_return_internal_prompt_or_identity_objects() -> None:
    response = CoreOrchestrator().execute(_request())

    assert isinstance(response, ExecutionResponse)
    assert not hasattr(response, "prompt_result")
    assert not hasattr(response, "identity_result")


def test_modules_do_not_access_engines_directly() -> None:
    module_source = "\n".join(path.read_text(encoding="utf-8") for path in Path("modules").rglob("*.py"))
    forbidden_terms = [
        "core.orchestrator",
        "core.identity",
        "core.prompts",
        "core.providers",
        "IdentityEngine",
        "PromptEngine",
        "ProviderEngine",
        "CoreOrchestrator",
    ]
    for term in forbidden_terms:
        assert term not in module_source


def test_only_orchestrator_imports_all_three_core_engines() -> None:
    core_files = [path for path in Path("core").rglob("*.py") if "__pycache__" not in str(path)]
    files_with_all_engines = []
    for path in core_files:
        source = path.read_text(encoding="utf-8")
        if "IdentityEngine" in source and "PromptEngine" in source and "ProviderEngine" in source:
            files_with_all_engines.append(path.as_posix())

    assert files_with_all_engines == ["core/orchestrator/engine.py"]


def test_core_orchestrator_documentation_exists() -> None:
    documentation = Path("docs/JARVIS_CORE_ORCHESTRATOR.md").read_text(encoding="utf-8")

    assert "J.A.R.V.I.S Core Orchestrator" in documentation
    assert "ExecutionRequest" in documentation
    assert "ExecutionResponse" in documentation
