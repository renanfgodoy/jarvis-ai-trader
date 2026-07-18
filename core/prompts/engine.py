from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from core.engine import EngineDescriptor
from core.prompts.estimator import estimate_prompt_size
from core.prompts.exceptions import PromptBuildError
from core.prompts.models import PromptEngineConfig, PromptPackage, PromptRequest
from core.prompts.registry import PromptTemplateRegistry
from core.prompts.sanitizer import sanitize_request_payload
from core.prompts.templates import CoreSystemTemplate, GenericAnalysisTemplate, GenericStructuredResponseTemplate
from core.prompts.validators import validate_messages, validate_required_fields, validate_template_support


class PromptEngine:
    descriptor = EngineDescriptor(name="prompts", responsibility="Prompt construction, context policy, and model instructions.")

    def __init__(self, registry: PromptTemplateRegistry | None = None, config: PromptEngineConfig | None = None) -> None:
        self.config = config or PromptEngineConfig()
        self.registry = registry or create_default_prompt_registry()

    def describe(self) -> str:
        return self.descriptor.responsibility

    def build(self, request: PromptRequest) -> PromptPackage:
        template_version = request.template_version or self.config.default_template_version
        user_input, context, metadata = sanitize_request_payload(
            request.user_input,
            request.context,
            request.metadata,
            self.config,
        )
        sanitized_request = replace(
            request,
            template_version=template_version,
            user_input=user_input,
            context=context,
            metadata=metadata,
        )
        template = self.registry.get(sanitized_request.template_id, sanitized_request.template_version)
        validate_template_support(sanitized_request, template.supported_modules)
        validate_required_fields(sanitized_request, template.required_fields)
        try:
            messages = tuple(template.build(sanitized_request))
        except Exception as exc:  # pragma: no cover - defensive wrapper
            raise PromptBuildError(f"template failed to build: {template.template_id}@{template.version}") from exc
        validate_messages(messages, self.config)
        estimated_size = estimate_prompt_size(messages, characters_per_token=self.config.estimated_characters_per_token)
        fingerprint = build_prompt_fingerprint(
            module=sanitized_request.module,
            template_id=template.template_id,
            template_version=template.version,
            messages=messages,
            response_format=sanitized_request.response_format,
        )
        return PromptPackage(
            request_id=sanitized_request.request_id or str(uuid4()),
            module=sanitized_request.module,
            template_id=template.template_id,
            template_version=template.version,
            messages=messages,
            metadata={
                **metadata,
                "language": sanitized_request.language,
                "response_format": sanitized_request.response_format,
            },
            estimated_size=estimated_size,
            created_at=datetime.now(timezone.utc),
            fingerprint=fingerprint,
        )


def create_default_prompt_registry() -> PromptTemplateRegistry:
    registry = PromptTemplateRegistry()
    registry.register(CoreSystemTemplate(), default=True)
    registry.register(GenericAnalysisTemplate(), default=True)
    registry.register(GenericStructuredResponseTemplate(), default=True)
    return registry


def build_prompt_fingerprint(*, module: str, template_id: str, template_version: str, messages: tuple, response_format: str) -> str:
    payload = {
        "module": module,
        "template_id": template_id,
        "template_version": template_version,
        "messages": [
            {
                "role": message.role,
                "content": message.content,
                "name": message.name,
                "metadata": dict(message.metadata),
            }
            for message in messages
        ],
        "response_format": response_format,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
