from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from core.prompts.models import PromptMessage, PromptRequest


@dataclass(frozen=True)
class BasePromptTemplate:
    template_id: str
    version: str
    description: str
    supported_modules: tuple[str, ...] = ("*",)
    required_fields: tuple[str, ...] = ()

    def build(self, request: PromptRequest) -> list[PromptMessage]:
        raise NotImplementedError


def format_context(context: dict[str, Any]) -> str:
    if not context:
        return "Nenhum contexto adicional informado."
    return json.dumps(context, ensure_ascii=False, sort_keys=True, indent=2, default=str)
