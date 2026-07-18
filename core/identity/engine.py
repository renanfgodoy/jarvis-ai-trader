from __future__ import annotations

from core.engine import EngineDescriptor
from core.identity.builder import IdentityBuilder
from core.identity.config import IdentityConfig
from core.identity.models import IdentityRequest, IdentityResult
from core.identity.profiles import official_identity_profiles
from core.identity.registry import IdentityRegistry
from core.identity.resolver import IdentityResolver
from core.identity.validators import IdentityValidator


class IdentityEngine:
    descriptor = EngineDescriptor(name="identity", responsibility="Product identity, behavior, and tone.")

    def __init__(
        self,
        registry: IdentityRegistry | None = None,
        config: IdentityConfig | None = None,
        validator: IdentityValidator | None = None,
    ) -> None:
        self.config = config or IdentityConfig()
        self.validator = validator or IdentityValidator(self.config)
        self.registry = registry or create_default_identity_registry(self.config, self.validator)
        self.resolver = IdentityResolver(self.registry, self.config, self.validator)
        self.builder = IdentityBuilder(self.validator, resolver_version=self.resolver.resolver_version)

    def describe(self) -> str:
        return self.descriptor.responsibility

    def resolve(self, request: IdentityRequest) -> IdentityResult:
        profile = self.resolver.resolve(request)
        return self.builder.build(request, profile)


def create_default_identity_registry(
    config: IdentityConfig | None = None,
    validator: IdentityValidator | None = None,
) -> IdentityRegistry:
    registry = IdentityRegistry(config=config, validator=validator)
    for profile in official_identity_profiles():
        registry.register(profile, default=profile.identity_id == (config or IdentityConfig()).default_identity)
    return registry
