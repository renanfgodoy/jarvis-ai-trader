from __future__ import annotations

from typing import Any

from core.identity import IdentityRequest
from core.orchestrator.config import ExecutionConfig
from core.orchestrator.context import ExecutionContext
from core.orchestrator.events import (
    EVENT_EXECUTION_FINISHED,
    EVENT_IDENTITY_RESOLVED,
    EVENT_PROMPT_BUILT,
    EVENT_PROVIDER_EXECUTED,
    EVENT_PROVIDER_SELECTED,
    EVENT_RESPONSE_NORMALIZED,
)
from core.orchestrator.exceptions import PipelineException, StageException
from core.orchestrator.hooks import ExecutionHooks
from core.orchestrator.metadata import build_execution_metadata
from core.orchestrator.models import ExecutionResponse
from core.orchestrator.validators import ExecutionValidator
from core.prompts import PromptRequest
from core.providers import ProviderInvocation


class BasePipelineStage:
    stage_name = "base"
    stage_version = "1.0"

    def name(self) -> str:
        return self.stage_name

    def version(self) -> str:
        return self.stage_version

    def validate(self, context: ExecutionContext) -> None:
        if context is None:
            raise StageException("execution context is required")

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        raise NotImplementedError

    def rollback(self, context: ExecutionContext) -> None:
        return None


class ValidateRequestStage(BasePipelineStage):
    stage_name = "validate_request"

    def __init__(self, validator: ExecutionValidator) -> None:
        self.validator = validator

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        self.validate(context)
        self.validator.validate_request(context.request)
        context.status = "RUNNING"
        context.pipeline_stage = self.stage_name
        return context


class ResolveIdentityStage(BasePipelineStage):
    stage_name = "resolve_identity"

    def __init__(self, identity_engine: Any) -> None:
        self.identity_engine = identity_engine

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        self.validate(context)
        request = context.request
        context.identity_result = self.identity_engine.resolve(
            IdentityRequest(
                module=request.module,
                requested_identity=request.identity,
                language=request.language,
                metadata=request.metadata,
                context={"request_id": request.request_id},
                request_id=request.request_id,
            )
        )
        context.pipeline_stage = self.stage_name
        context.add_event(EVENT_IDENTITY_RESOLVED, self.stage_name, {"identity": context.identity_result.resolved_identity})
        return context


class BuildPromptStage(BasePipelineStage):
    stage_name = "build_prompt"

    def __init__(self, prompt_engine: Any, config: ExecutionConfig) -> None:
        self.prompt_engine = prompt_engine
        self.config = config

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        self.validate(context)
        request = context.request
        identity = context.identity_result.identity_profile.identity_id if context.identity_result else None
        context.prompt_result = self.prompt_engine.build(
            PromptRequest(
                module=request.module,
                template_id=request.template_id or self.config.default_template_id,
                template_version=request.template_version or self.config.default_template_version,
                user_input=request.input,
                context={"identity": identity},
                metadata={"execution_request_id": request.request_id},
                language=request.language or self.config.default_language,
                response_format=request.response_format or self.config.default_response_format,
                request_id=request.request_id,
            )
        )
        context.pipeline_stage = self.stage_name
        context.add_event(EVENT_PROMPT_BUILT, self.stage_name, {"template_id": context.prompt_result.template_id})
        return context


class ExecuteProviderStage(BasePipelineStage):
    stage_name = "execute_provider"

    def __init__(self, provider_engine: Any, config: ExecutionConfig) -> None:
        self.provider_engine = provider_engine
        self.config = config

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        self.validate(context)
        if context.prompt_result is None:
            raise StageException("prompt_result is required before provider execution")
        provider = context.request.provider
        context.add_event(EVENT_PROVIDER_SELECTED, self.stage_name, {"provider": provider or "default"})
        context.provider_result = self.provider_engine.invoke(
            ProviderInvocation(
                prompt_package=context.prompt_result,
                provider=provider,
                required_capabilities=self.config.default_provider_capabilities,
                metadata={
                    **dict(context.request.metadata),
                    "execution_request_id": context.request.request_id,
                },
            )
        )
        context.pipeline_stage = self.stage_name
        context.add_event(EVENT_PROVIDER_EXECUTED, self.stage_name, {"provider": context.provider_result.provider})
        return context


class NormalizeResponseStage(BasePipelineStage):
    stage_name = "normalize_response"

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        self.validate(context)
        if context.provider_result is None:
            raise StageException("provider_result is required before normalization")
        context.pipeline_stage = self.stage_name
        context.add_event(EVENT_RESPONSE_NORMALIZED, self.stage_name, {"status": context.provider_result.status})
        return context


class FinalizeExecutionStage(BasePipelineStage):
    stage_name = "finalize_execution"

    def __init__(self, config: ExecutionConfig) -> None:
        self.config = config

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        self.validate(context)
        if context.identity_result is None:
            raise StageException("identity_result is required before finalization")
        if context.provider_result is None:
            raise StageException("provider_result is required before finalization")
        context.status = "SUCCESS"
        context.execution_metadata = build_execution_metadata(
            request_id=context.request.request_id,
            module=context.request.module,
            pipeline_version=self.config.pipeline_version,
            status=context.status,
            started_at=context.started_at,
            provider=context.provider_result.provider,
            provider_version=context.provider_result.provider_version,
            identity=context.identity_result.resolved_identity,
        )
        context.response = ExecutionResponse(
            request_id=context.request.request_id,
            identity=context.identity_result.resolved_identity,
            provider=context.provider_result.provider,
            provider_response=context.provider_result,
            latency=context.execution_metadata.duration or 0.0,
            status=context.status,
            metadata=context.execution_metadata,
            fingerprint=context.execution_metadata.fingerprint,
        )
        context.pipeline_stage = self.stage_name
        context.add_event(EVENT_EXECUTION_FINISHED, self.stage_name, {"status": context.status})
        return context


class ExecutionPipeline:
    def __init__(self, stages: tuple[BasePipelineStage, ...], hooks: ExecutionHooks | None = None, enable_hooks: bool = True) -> None:
        if not stages:
            raise PipelineException("pipeline requires at least one stage")
        self.stages = stages
        self.hooks = hooks or ExecutionHooks()
        self.enable_hooks = enable_hooks

    def execute(self, context: ExecutionContext) -> ExecutionContext:
        executed: list[BasePipelineStage] = []
        try:
            for stage in self.stages:
                stage.validate(context)
                self._before(stage.name(), context)
                context = stage.execute(context)
                self._after(stage.name(), context)
                executed.append(stage)
            return context
        except Exception as exc:
            context.status = "FAILED"
            context.errors.append(str(exc))
            for stage in reversed(executed):
                stage.rollback(context)
            raise

    def _before(self, stage_name: str, context: ExecutionContext) -> None:
        if not self.enable_hooks:
            return
        if stage_name == "resolve_identity":
            self.hooks.before_identity(context)
        elif stage_name == "build_prompt":
            self.hooks.before_prompt(context)
        elif stage_name == "execute_provider":
            self.hooks.before_provider(context)
        elif stage_name == "finalize_execution":
            self.hooks.before_finish(context)

    def _after(self, stage_name: str, context: ExecutionContext) -> None:
        if not self.enable_hooks:
            return
        if stage_name == "resolve_identity":
            self.hooks.after_identity(context)
        elif stage_name == "build_prompt":
            self.hooks.after_prompt(context)
        elif stage_name == "execute_provider":
            self.hooks.after_provider(context)
        elif stage_name == "finalize_execution":
            self.hooks.after_finish(context)
