from __future__ import annotations

import json

from core.orchestrator.config import ExecutionConfig
from core.orchestrator.context import ExecutionContext
from core.orchestrator.exceptions import ConfigurationException, ValidationException
from core.orchestrator.models import ExecutionRequest


class ExecutionValidator:
    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self.config = config or ExecutionConfig()
        self.validate_config(self.config)

    def validate_config(self, config: ExecutionConfig) -> None:
        if not config.pipeline_version.strip():
            raise ConfigurationException("pipeline_version is required")
        if not config.default_template_id.strip():
            raise ConfigurationException("default_template_id is required")
        if config.default_response_format not in {"text", "structured"}:
            raise ConfigurationException("default_response_format must be text or structured")

    def validate_request(self, request: ExecutionRequest) -> None:
        if not request.request_id.strip():
            raise ValidationException("request_id is required")
        if not request.module.strip():
            raise ValidationException("module is required")
        if not request.input or not request.input.strip():
            raise ValidationException("input is required")
        if request.response_format not in {"text", "structured"}:
            raise ValidationException("response_format must be text or structured")
        try:
            json.dumps(request.metadata, ensure_ascii=False, sort_keys=True, default=str)
        except (TypeError, ValueError) as exc:
            raise ValidationException("metadata must be serializable") from exc

    def validate_context(self, context: ExecutionContext) -> None:
        if context.request is None:
            raise ValidationException("context request is required")
