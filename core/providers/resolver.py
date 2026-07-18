from __future__ import annotations

from dataclasses import dataclass

from core.providers.config import ProviderConfiguration
from core.providers.errors import ProviderNotFoundError
from core.providers.registry import ProviderRegistry


@dataclass(frozen=True)
class ProviderResolution:
    requested_provider: str | None
    selected_provider: str
    fallback_used: bool = False
    reason: str = "DEFAULT"


class ProviderResolver:
    def __init__(self, configuration: ProviderConfiguration | None = None, registry: ProviderRegistry | None = None) -> None:
        self.configuration = configuration or ProviderConfiguration()
        self.registry = registry

    def resolve(self, requested_provider: str | None = None) -> ProviderResolution:
        requested = self._normalize(requested_provider)
        candidates = self._candidate_providers(requested)
        for provider in candidates:
            if self._is_available(provider):
                fallback_used = requested is not None and provider != requested
                reason = "REQUESTED" if provider == requested else "FALLBACK" if fallback_used else "DEFAULT"
                return ProviderResolution(
                    requested_provider=requested,
                    selected_provider=provider,
                    fallback_used=fallback_used,
                    reason=reason,
                )
        raise ProviderNotFoundError("no enabled provider available")

    def _candidate_providers(self, requested: str | None) -> tuple[str, ...]:
        candidates: list[str] = []
        if requested:
            candidates.append(requested)
        candidates.append(self.configuration.settings.default_provider)
        candidates.extend(self.configuration.settings.provider_priority)
        if self.configuration.settings.fallback_enabled:
            candidates.append(self.configuration.settings.fallback_provider)
        normalized: list[str] = []
        for provider in candidates:
            candidate = self._normalize(provider)
            if candidate and candidate not in normalized:
                normalized.append(candidate)
        return tuple(normalized)

    def _is_available(self, provider: str) -> bool:
        if provider not in self.configuration.settings.enabled_providers:
            return False
        if not self.configuration.feature_flags.enabled(provider):
            return False
        if self.registry is None:
            return True
        try:
            self.registry.get(provider)
        except ProviderNotFoundError:
            return False
        return True

    @staticmethod
    def _normalize(provider: str | None) -> str | None:
        if provider is None:
            return None
        normalized = provider.strip().lower()
        return normalized or None
