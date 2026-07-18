from core.providers.base import BaseProvider


class LMStudioProvider(BaseProvider):
    name = "lmstudio"
    placeholder_status = "not_configured"
    placeholder_response = "LM Studio placeholder is not configured. No external API was called."
    declared_capabilities = ("chat", "local")
