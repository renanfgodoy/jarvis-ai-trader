from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProviderSettings:
    default_provider: str = "mock"
    enabled_providers: tuple[str, ...] = ("mock",)
    provider_priority: tuple[str, ...] = ("mock",)
    fallback_provider: str = "mock"
    fallback_enabled: bool = True
    health_check_enabled: bool = True
    debug: bool = True

    def __post_init__(self) -> None:
        default_provider = self.default_provider.strip().lower()
        fallback_provider = self.fallback_provider.strip().lower()
        enabled = _normalize_sequence(self.enabled_providers)
        priority = _normalize_sequence(self.provider_priority)
        if not default_provider:
            raise ValueError("default provider is required")
        if not fallback_provider:
            raise ValueError("fallback provider is required")
        if not enabled:
            raise ValueError("at least one enabled provider is required")
        if default_provider not in enabled:
            enabled = (default_provider, *tuple(provider for provider in enabled if provider != default_provider))
        if fallback_provider not in enabled:
            enabled = (*enabled, fallback_provider)
        if not priority:
            priority = enabled
        object.__setattr__(self, "default_provider", default_provider)
        object.__setattr__(self, "fallback_provider", fallback_provider)
        object.__setattr__(self, "enabled_providers", enabled)
        object.__setattr__(self, "provider_priority", priority)

    def as_dict(self) -> dict[str, object]:
        return {
            "default_provider": self.default_provider,
            "enabled_providers": self.enabled_providers,
            "provider_priority": self.provider_priority,
            "fallback_provider": self.fallback_provider,
            "fallback_enabled": self.fallback_enabled,
            "health_check_enabled": self.health_check_enabled,
            "debug": self.debug,
        }


def _normalize_sequence(values: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        provider = value.strip().lower()
        if provider and provider not in normalized:
            normalized.append(provider)
    return tuple(normalized)
