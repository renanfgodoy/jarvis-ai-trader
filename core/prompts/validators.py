from __future__ import annotations

from core.prompts.exceptions import InvalidPromptRequestError, PromptSizeLimitExceededError
from core.prompts.models import PromptEngineConfig, PromptMessage, PromptRequest


def validate_template_support(request: PromptRequest, supported_modules: tuple[str, ...]) -> None:
    if supported_modules and "*" not in supported_modules and request.module not in supported_modules:
        raise InvalidPromptRequestError(f"template does not support module: {request.module}")


def validate_required_fields(request: PromptRequest, required_fields: tuple[str, ...]) -> None:
    for field_name in required_fields:
        value = getattr(request, field_name, None)
        if value is None:
            raise InvalidPromptRequestError(f"{field_name} is required")
        if isinstance(value, str) and not value.strip():
            raise InvalidPromptRequestError(f"{field_name} is required")


def validate_messages(messages: tuple[PromptMessage, ...], config: PromptEngineConfig) -> None:
    if not messages:
        raise InvalidPromptRequestError("template produced no messages")
    total = sum(len(message.content) for message in messages)
    if total > config.max_total_characters:
        raise PromptSizeLimitExceededError(f"prompt exceeds {config.max_total_characters} characters")
