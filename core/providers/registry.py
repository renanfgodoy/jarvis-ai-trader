from __future__ import annotations

from core.providers.base import BaseProvider
from core.providers.errors import DuplicateProviderError, ProviderNotFoundError
from core.providers.validators import ProviderValidator


class ProviderRegistry:
    def __init__(self, validator: ProviderValidator | None = None) -> None:
        self.validator = validator or ProviderValidator()
        self._providers: dict[str, dict[str, BaseProvider]] = {}
        self._defaults: dict[str, str] = {}
        self._active_provider: str | None = None

    def register(self, provider: BaseProvider, *, default: bool = False, active: bool = False) -> None:
        self.validator.validate_provider(provider)
        provider_name = provider.name.strip().lower()
        version = provider.provider_version.strip()
        versions = self._providers.setdefault(provider_name, {})
        if version in versions:
            raise DuplicateProviderError(f"provider already registered: {provider_name}@{version}")
        provider.initialize()
        versions[version] = provider
        if default or provider_name not in self._defaults:
            self._defaults[provider_name] = version
        if active or self._active_provider is None:
            self._active_provider = provider_name

    def get(self, provider: str, version: str | None = None) -> BaseProvider:
        normalized = provider.strip().lower()
        if normalized not in self._providers:
            raise ProviderNotFoundError(f"provider not found: {normalized}")
        selected_version = version or self._defaults[normalized]
        if selected_version not in self._providers[normalized]:
            raise ProviderNotFoundError(f"provider version not found: {normalized}@{selected_version}")
        return self._providers[normalized][selected_version]

    def list(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def list_versions(self, provider: str) -> tuple[str, ...]:
        normalized = provider.strip().lower()
        if normalized not in self._providers:
            raise ProviderNotFoundError(f"provider not found: {normalized}")
        return tuple(sorted(self._providers[normalized]))

    def default_version(self, provider: str) -> str:
        normalized = provider.strip().lower()
        if normalized not in self._defaults:
            raise ProviderNotFoundError(f"provider not found: {normalized}")
        return self._defaults[normalized]

    def active(self) -> BaseProvider:
        if self._active_provider is None:
            raise ProviderNotFoundError("active provider not set")
        return self.get(self._active_provider)

    def set_active(self, provider: str) -> None:
        self.get(provider)
        self._active_provider = provider.strip().lower()

    def remove(self, provider: str, version: str | None = None) -> None:
        normalized = provider.strip().lower()
        if normalized not in self._providers:
            raise ProviderNotFoundError(f"provider not found: {normalized}")
        selected_version = version or self._defaults[normalized]
        if selected_version not in self._providers[normalized]:
            raise ProviderNotFoundError(f"provider version not found: {normalized}@{selected_version}")
        self._providers[normalized][selected_version].shutdown()
        del self._providers[normalized][selected_version]
        if not self._providers[normalized]:
            del self._providers[normalized]
            self._defaults.pop(normalized, None)
            if self._active_provider == normalized:
                self._active_provider = next(iter(sorted(self._providers)), None)
        elif self._defaults.get(normalized) == selected_version:
            self._defaults[normalized] = sorted(self._providers[normalized])[0]

    def default(self, provider: str | None = None) -> BaseProvider:
        if provider is None:
            return self.active()
        normalized = provider.strip().lower()
        return self.get(normalized, self.default_version(normalized))

    def health(self) -> dict[str, object]:
        return {provider_name: self.get(provider_name).health() for provider_name in self.list()}
