from __future__ import annotations

from typing import Protocol

from core.prompts.models import PromptMessage, PromptRequest


class PromptTemplate(Protocol):
    template_id: str
    version: str
    description: str
    supported_modules: tuple[str, ...]
    required_fields: tuple[str, ...]

    def build(self, request: PromptRequest) -> list[PromptMessage]:
        ...
