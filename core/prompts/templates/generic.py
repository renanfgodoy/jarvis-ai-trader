from __future__ import annotations

from core.prompts.models import PromptMessage, PromptRequest
from core.prompts.templates.base import BasePromptTemplate, format_context


class GenericAnalysisTemplate(BasePromptTemplate):
    def __init__(self) -> None:
        super().__init__(
            template_id="core.generic_analysis",
            version="1.0",
            description="Generic non-domain-specific analysis prompt.",
            supported_modules=("*",),
            required_fields=("user_input",),
        )

    def build(self, request: PromptRequest) -> list[PromptMessage]:
        return [
            PromptMessage(
                role="system",
                content=(
                    "Você está operando dentro da Friday AI Platform. "
                    "Analise somente as informações fornecidas. "
                    "Não invente fatos, dados externos ou conclusões fora do contexto."
                ),
                metadata={"template": self.template_id},
            ),
            PromptMessage(
                role="user",
                content=(
                    f"Solicitação do módulo: {request.module}\n"
                    f"Idioma: {request.language}\n\n"
                    f"Entrada:\n{request.user_input}\n\n"
                    f"Contexto:\n{format_context(dict(request.context))}"
                ),
                metadata={"response_format": request.response_format},
            ),
        ]


class GenericStructuredResponseTemplate(BasePromptTemplate):
    def __init__(self) -> None:
        super().__init__(
            template_id="core.structured_response",
            version="1.0",
            description="Generic request for structured textual output.",
            supported_modules=("*",),
            required_fields=("user_input",),
        )

    def build(self, request: PromptRequest) -> list[PromptMessage]:
        return [
            PromptMessage(
                role="system",
                content=(
                    "Você está operando dentro da Friday AI Platform. "
                    "Produza uma resposta estruturada, conservadora e rastreável. "
                    "Use apenas os campos e contexto fornecidos pelo módulo."
                ),
                metadata={"template": self.template_id},
            ),
            PromptMessage(
                role="developer",
                content=(
                    "Formato esperado: resposta estruturada em seções textuais. "
                    "Não use JSON Schema avançado nesta versão."
                ),
                metadata={"response_format": "structured"},
            ),
            PromptMessage(
                role="user",
                content=(
                    f"Solicitação:\n{request.user_input}\n\n"
                    f"Contexto:\n{format_context(dict(request.context))}"
                ),
                metadata={"module": request.module},
            ),
        ]
