from core.providers.base import BaseProvider


class GoogleProvider(BaseProvider):
    name = "google"
    placeholder_status = "not_configured"
    placeholder_response = "Google placeholder is not configured. No external API was called."
    declared_capabilities = ("chat", "vision", "json", "streaming", "embeddings")
