from __future__ import annotations

from uuid import uuid4

from core.orchestrator import CoreOrchestrator, ExecutionRequest
from sdk.config import ModuleConfig
from sdk.manifest import ModuleManifest
from sdk.metadata import ModuleMetadata
from sdk.models import ModuleRequest, ModuleResponse
from sdk.validators import ModuleValidator


class BaseModule:
    def __init__(
        self,
        manifest: ModuleManifest,
        metadata: ModuleMetadata | None = None,
        orchestrator: CoreOrchestrator | None = None,
        config: ModuleConfig | None = None,
        validator: ModuleValidator | None = None,
    ) -> None:
        self._manifest = manifest
        self._metadata = metadata or ModuleMetadata(module=manifest.name, version=manifest.version)
        self._orchestrator = orchestrator or CoreOrchestrator()
        self._config = config or ModuleConfig()
        self._validator = validator or ModuleValidator()
        self._initialized = False
        self._validator.validate_config(self._config)
        self._validator.validate_manifest(self._manifest)
        self._validator.validate_metadata(self._metadata)

    def initialize(self) -> None:
        self._initialized = True

    def validate(self, request: ModuleRequest) -> None:
        self._validator.validate_request(request)

    def execute(self, request: ModuleRequest) -> ModuleResponse:
        self.validate(request)
        execution = self._orchestrator.execute(
            ExecutionRequest(
                request_id=request.request_id or f"{self._manifest.name}-{uuid4().hex}",
                module=request.module,
                input=request.payload,
                identity=request.identity or self._manifest.identity,
                provider=request.provider or self._manifest.provider,
                language=request.language or self._manifest.language,
                metadata={
                    **dict(request.metadata),
                    "module_sdk": True,
                    "module_manifest": self._manifest.name,
                },
            )
        )
        response = ModuleResponse(
            status=execution.status,
            module=self._manifest.name,
            identity=execution.identity,
            provider=execution.provider,
            execution=execution,
            response=execution.provider_response.response,
            latency=execution.latency,
            metadata={
                "request_id": execution.request_id,
                "execution_id": execution.metadata.execution_id,
                "fingerprint": execution.fingerprint,
            },
        )
        self._validator.validate_response(response)
        return response

    def shutdown(self) -> None:
        self._initialized = False

    def metadata(self) -> ModuleMetadata:
        return self._metadata

    def manifest(self) -> ModuleManifest:
        return self._manifest

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def name(self) -> str:
        return self._manifest.name
