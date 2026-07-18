from __future__ import annotations

from core.providers.errors import ProviderCapabilityError, ProviderNotFoundError


class ProviderCapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, tuple[str, ...]] = {}

    def register(self, provider: str, capabilities: tuple[str, ...]) -> None:
        normalized = provider.strip().lower()
        self._capabilities[normalized] = tuple(sorted(set(capabilities)))

    def get(self, provider: str) -> tuple[str, ...]:
        normalized = provider.strip().lower()
        if normalized not in self._capabilities:
            raise ProviderNotFoundError(f"provider capabilities not found: {normalized}")
        return self._capabilities[normalized]

    def supports(self, provider: str, capability: str) -> bool:
        return capability in self.get(provider)

    def validate(self, provider: str, required_capabilities: tuple[str, ...]) -> None:
        available = set(self.get(provider))
        missing = [capability for capability in required_capabilities if capability not in available]
        if missing:
            raise ProviderCapabilityError(f"provider {provider} missing capabilities: {', '.join(missing)}")

    def list(self) -> dict[str, tuple[str, ...]]:
        return dict(sorted(self._capabilities.items()))
