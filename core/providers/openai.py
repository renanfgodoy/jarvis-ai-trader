from __future__ import annotations

from core.providers.base import BaseProvider
from shared.contracts import ProviderRequest, ProviderResponse


class OpenAIProvider(BaseProvider):
    name = "openai"
    placeholder_status = "not_configured"
    placeholder_response = "OpenAI placeholder is not configured. No external API was called."
    declared_capabilities = ("chat", "vision", "json", "streaming", "tool_calling", "embeddings")

    def execute(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(provider=self.name, status="not_configured", payload={"operation": request.operation})
