from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from core.prompts.exceptions import InvalidPromptMessageError, InvalidPromptRequestError


SerializableMapping = Mapping[str, Any]


@dataclass(frozen=True)
class PromptEngineConfig:
    default_language: str = "pt-BR"
    max_input_characters: int = 20_000
    max_context_characters: int = 40_000
    max_total_characters: int = 80_000
    default_template_version: str = "1.0"
    estimated_characters_per_token: int = 4


@dataclass(frozen=True)
class PromptRequest:
    module: str
    template_id: str
    template_version: str | None = None
    user_input: str | None = None
    context: SerializableMapping = field(default_factory=dict)
    metadata: SerializableMapping = field(default_factory=dict)
    language: str = "pt-BR"
    response_format: str = "text"
    request_id: str | None = None

    def __post_init__(self) -> None:
        if not self.module or not self.module.strip():
            raise InvalidPromptRequestError("module is required")
        if not self.template_id or not self.template_id.strip():
            raise InvalidPromptRequestError("template_id is required")
        if self.context is None or not isinstance(self.context, Mapping):
            raise InvalidPromptRequestError("context must be a mapping")
        if self.metadata is None or not isinstance(self.metadata, Mapping):
            raise InvalidPromptRequestError("metadata must be a mapping")
        if not self.language or not self.language.strip():
            raise InvalidPromptRequestError("language is required")
        if self.response_format not in {"text", "structured"}:
            raise InvalidPromptRequestError("response_format must be text or structured")


@dataclass(frozen=True)
class PromptMessage:
    role: str
    content: str
    name: str | None = None
    metadata: SerializableMapping = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.role not in {"system", "developer", "user", "assistant"}:
            raise InvalidPromptMessageError(f"unsupported role: {self.role}")
        if not isinstance(self.content, str) or not self.content.strip():
            raise InvalidPromptMessageError("content is required")
        if self.metadata is None or not isinstance(self.metadata, Mapping):
            raise InvalidPromptMessageError("metadata must be a mapping")


@dataclass(frozen=True)
class PromptSizeEstimate:
    character_count: int
    word_count: int
    estimated_tokens: int
    message_count: int


@dataclass(frozen=True)
class PromptPackage:
    request_id: str
    module: str
    template_id: str
    template_version: str
    messages: tuple[PromptMessage, ...]
    metadata: SerializableMapping
    estimated_size: PromptSizeEstimate
    created_at: datetime
    fingerprint: str

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            object.__setattr__(self, "created_at", self.created_at.replace(tzinfo=timezone.utc))
