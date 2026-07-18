from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureFlags:
    mock: bool = True
    openai: bool = False
    gemini: bool = False
    anthropic: bool = False
    ollama: bool = False
    lmstudio: bool = False
    azure: bool = False

    def enabled(self, provider: str) -> bool:
        normalized = provider.strip().lower()
        if not normalized:
            return False
        if not hasattr(self, normalized):
            return True
        return bool(getattr(self, normalized))

    def enabled_providers(self) -> tuple[str, ...]:
        return tuple(provider for provider, enabled in self.as_dict().items() if enabled)

    def as_dict(self) -> dict[str, bool]:
        return {
            "mock": self.mock,
            "openai": self.openai,
            "gemini": self.gemini,
            "anthropic": self.anthropic,
            "ollama": self.ollama,
            "lmstudio": self.lmstudio,
            "azure": self.azure,
        }
