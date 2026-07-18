from core.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    placeholder_status = "not_configured"
    placeholder_response = "Anthropic placeholder is not configured. No external API was called."
    declared_capabilities = ("chat", "vision", "streaming", "tool_use")
