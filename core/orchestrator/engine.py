from __future__ import annotations

from core.engine import EngineDescriptor
from core.identity import IdentityEngine
from core.orchestrator.config import ExecutionConfig
from core.orchestrator.context import ExecutionContext
from core.orchestrator.events import EVENT_EXECUTION_FAILED, EVENT_EXECUTION_STARTED
from core.orchestrator.hooks import ExecutionHooks
from core.orchestrator.exceptions import PipelineException
from core.orchestrator.metadata import build_execution_metadata
from core.orchestrator.models import ExecutionRequest, ExecutionResponse
from core.orchestrator.pipeline import (
    BuildPromptStage,
    ExecuteProviderStage,
    ExecutionPipeline,
    FinalizeExecutionStage,
    NormalizeResponseStage,
    ResolveIdentityStage,
    ValidateRequestStage,
)
from core.orchestrator.validators import ExecutionValidator
from core.prompts import PromptEngine
from core.providers import ProviderEngine


class CoreOrchestrator:
    descriptor = EngineDescriptor(name="orchestrator", responsibility="Coordinates Core engines through one execution pipeline.")

    def __init__(
        self,
        identity_engine: IdentityEngine | None = None,
        prompt_engine: PromptEngine | None = None,
        provider_engine: ProviderEngine | None = None,
        config: ExecutionConfig | None = None,
        validator: ExecutionValidator | None = None,
        hooks: ExecutionHooks | None = None,
        pipeline: ExecutionPipeline | None = None,
    ) -> None:
        self.config = config or ExecutionConfig()
        self.validator = validator or ExecutionValidator(self.config)
        self.hooks = hooks or ExecutionHooks()
        self.identity_engine = identity_engine or IdentityEngine()
        self.prompt_engine = prompt_engine or PromptEngine()
        self.provider_engine = provider_engine or ProviderEngine()
        self.pipeline = pipeline or self._build_default_pipeline()

    def describe(self) -> str:
        return self.descriptor.responsibility

    def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        context = self.build_context(request)
        try:
            self.validate(context)
            context = self.execute_pipeline(context)
            return self.finalize(context)
        except Exception:
            context.add_event(EVENT_EXECUTION_FAILED, context.pipeline_stage, {"status": "FAILED"})
            context.execution_metadata = build_execution_metadata(
                request_id=request.request_id,
                module=request.module,
                pipeline_version=self.config.pipeline_version,
                status="FAILED",
                started_at=context.started_at,
                identity=context.identity_result.resolved_identity if context.identity_result else None,
                provider=context.provider_result.provider if context.provider_result else None,
                provider_version=context.provider_result.provider_version if context.provider_result else None,
            )
            raise

    def validate(self, context: ExecutionContext) -> None:
        if self.config.enable_hooks:
            self.hooks.before_validation(context)
        self.validator.validate_context(context)
        self.validator.validate_request(context.request)
        if self.config.enable_hooks:
            self.hooks.after_validation(context)

    def build_context(self, request: ExecutionRequest) -> ExecutionContext:
        context = ExecutionContext(request=request)
        if self.config.enable_events:
            context.add_event(EVENT_EXECUTION_STARTED, "created", {"module": request.module})
        return context

    def execute_pipeline(self, context: ExecutionContext) -> ExecutionContext:
        return self.pipeline.execute(context)

    def finalize(self, context: ExecutionContext) -> ExecutionResponse:
        if context.response is None:
            raise PipelineException("pipeline did not produce an execution response")
        return context.response

    def _build_default_pipeline(self) -> ExecutionPipeline:
        return ExecutionPipeline(
            (
                ValidateRequestStage(self.validator),
                ResolveIdentityStage(self.identity_engine),
                BuildPromptStage(self.prompt_engine, self.config),
                ExecuteProviderStage(self.provider_engine, self.config),
                NormalizeResponseStage(),
                FinalizeExecutionStage(self.config),
            ),
            hooks=self.hooks,
            enable_hooks=self.config.enable_hooks,
        )
