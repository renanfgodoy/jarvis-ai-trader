from core.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    name = "ollama"
    placeholder_status = "not_configured"
    placeholder_response = "Ollama placeholder is not configured. No external API was called."
    declared_capabilities = ("chat", "local", "embeddings")
