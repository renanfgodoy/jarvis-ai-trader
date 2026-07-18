from __future__ import annotations

from core.providers.factory import ProviderFactory, create_default_provider_factory
from core.providers.registry import ProviderRegistry
from core.providers.validators import ProviderValidator


class ProviderLoader:
    def __init__(
        self,
        factory: ProviderFactory | None = None,
        registry: ProviderRegistry | None = None,
        validator: ProviderValidator | None = None,
    ) -> None:
        self.validator = validator or ProviderValidator()
        self.factory = factory or create_default_provider_factory()
        self.registry = registry or ProviderRegistry(validator=self.validator)

    def discover(self) -> tuple[str, ...]:
        return self.factory.list_builders()

    def load(self, provider: str, *, default: bool = False, active: bool = False):
        instance = self.factory.create(provider)
        self.registry.register(instance, default=default, active=active)
        return instance

    def autoload(self, *, default_provider: str = "mock") -> ProviderRegistry:
        for provider_name in self.discover():
            self.load(
                provider_name,
                default=provider_name == default_provider,
                active=provider_name == default_provider,
            )
        return self.registry
