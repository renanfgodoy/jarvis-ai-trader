from __future__ import annotations

from core.prompts.models import PromptMessage, PromptRequest
from core.prompts.templates.base import BasePromptTemplate


class CoreSystemTemplate(BasePromptTemplate):
    def __init__(self) -> None:
        super().__init__(
            template_id="core.system",
            version="1.0",
            description="Neutral Friday AI Platform system instruction.",
            supported_modules=("*",),
        )

    def build(self, request: PromptRequest) -> list[PromptMessage]:
        return [
            PromptMessage(
                role="system",
                content=(
                    "Você é o J.A.R.V.I.S Core da Friday AI Platform. "
                    "Responda de forma clara, segura e estruturada. "
                    f"Idioma preferencial: {request.language}."
                ),
                metadata={"template": self.template_id},
            )
        ]
