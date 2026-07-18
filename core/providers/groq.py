from core.providers.base import BaseProvider


class GroqProvider(BaseProvider):
    name = "groq"
    placeholder_status = "not_configured"
    placeholder_response = "Groq placeholder is not configured. No external API was called."
    declared_capabilities = ("chat", "streaming")
