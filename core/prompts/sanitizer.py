from __future__ import annotations

import json
import re
from typing import Any, Mapping

from core.prompts.exceptions import InvalidPromptRequestError, PromptSizeLimitExceededError
from core.prompts.models import PromptEngineConfig


_SPACE_RE = re.compile(r"[ \t]+")
_NEWLINE_RE = re.compile(r"\n{3,}")


def sanitize_text(value: str | None, *, max_characters: int, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise InvalidPromptRequestError(f"{field_name} must be a string")
    sanitized = value.replace("\x00", "")
    sanitized = sanitized.replace("\r\n", "\n").replace("\r", "\n")
    sanitized = "\n".join(_SPACE_RE.sub(" ", line).strip() for line in sanitized.split("\n"))
    sanitized = _NEWLINE_RE.sub("\n\n", sanitized).strip()
    if len(sanitized) > max_characters:
        raise PromptSizeLimitExceededError(f"{field_name} exceeds {max_characters} characters")
    return sanitized


def ensure_serializable_mapping(value: Mapping[str, Any], *, field_name: str, max_characters: int) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise InvalidPromptRequestError(f"{field_name} must be a mapping")
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except (TypeError, ValueError) as exc:
        raise InvalidPromptRequestError(f"{field_name} must be serializable") from exc
    if len(encoded) > max_characters:
        raise PromptSizeLimitExceededError(f"{field_name} exceeds {max_characters} characters")
    return dict(value)


def sanitize_request_payload(
    user_input: str | None,
    context: Mapping[str, Any],
    metadata: Mapping[str, Any],
    config: PromptEngineConfig,
) -> tuple[str | None, dict[str, Any], dict[str, Any]]:
    return (
        sanitize_text(user_input, max_characters=config.max_input_characters, field_name="user_input"),
        ensure_serializable_mapping(context, field_name="context", max_characters=config.max_context_characters),
        ensure_serializable_mapping(metadata, field_name="metadata", max_characters=config.max_context_characters),
    )
