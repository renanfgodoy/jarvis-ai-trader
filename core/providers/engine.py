from __future__ import annotations

from core.engine import EngineDescriptor
from core.providers.capabilities import ProviderCapabilityRegistry
from core.providers.config import ProviderConfiguration
from core.providers.fallback import FallbackPolicy
from core.providers.factory import ProviderFactory, create_default_provider_factory
from core.providers.health import ProviderHealthManager
from core.providers.loader import ProviderLoader
from core.providers.models import ProviderConfig, ProviderInvocation, ProviderResponse
from core.providers.registry import ProviderRegistry
from core.providers.resolver import ProviderResolver
from core.providers.retry import RetryPolicy
from core.providers.validators import ProviderValidator


class ProviderEngine:
    descriptor = EngineDescriptor(
        name="providers",
        responsibility="Broker-neutral and model-neutral provider orchestration contracts.",
    )

    def __init__(
        self,
        factory: ProviderFactory | None = None,
        registry: ProviderRegistry | None = None,
        capability_registry: ProviderCapabilityRegistry | None = None,
        config: ProviderConfig | None = None,
        configuration: ProviderConfiguration | None = None,
        resolver: ProviderResolver | None = None,
        health_manager: ProviderHealthManager | None = None,
        retry_policy: RetryPolicy | None = None,
        fallback_policy: FallbackPolicy | None = None,
        validator: ProviderValidator | None = None,
    ) -> None:
        self.configuration = configuration or (
            ProviderConfiguration.compatibility(config.default_provider, config.fallback_provider)
            if config is not None
            else ProviderConfiguration()
        )
        self.config = config or ProviderConfig(
            default_provider=self.configuration.settings.default_provider,
            fallback_provider=(
                self.configuration.settings.fallback_provider
                if self.configuration.settings.fallback_enabled
                else None
            ),
            health_check_enabled=self.configuration.settings.health_check_enabled,
        )
        self.validator = validator or ProviderValidator()
        self.validator.validate_config(self.config)
        self.factory = factory or create_default_provider_factory()
        self.registry = registry or create_default_provider_registry(self.factory, self.config, self.validator)
        self.resolver = resolver or ProviderResolver(configuration=self.configuration, registry=self.registry)
        self.health_manager = health_manager or ProviderHealthManager(registry=self.registry)
        self.capability_registry = capability_registry or create_default_capability_registry(self.registry)
        self.retry_policy = retry_policy or RetryPolicy(
            enabled=self.config.retry_enabled,
            max_attempts=self.config.retry_attempts,
        )
        self.fallback_policy = fallback_policy or FallbackPolicy(
            enabled=bool(self.config.fallback_provider),
            fallback_provider=self.config.fallback_provider,
        )

    def describe(self) -> str:
        return self.descriptor.responsibility

    def invoke(self, invocation: ProviderInvocation) -> ProviderResponse:
        resolution = self.resolver.resolve(invocation.provider or self.config.default_provider)
        provider_name = resolution.selected_provider
        try:
            return self._invoke_provider(provider_name, invocation, fallback_used=resolution.fallback_used)
        except Exception as exc:
            self.health_manager.record_execution(provider_name, 0.0, error=exc)
            fallback_provider = self.fallback_policy.next_provider(provider_name)
            if not fallback_provider:
                raise
            return self._invoke_provider(fallback_provider, invocation, fallback_used=True)

    def _invoke_provider(self, provider_name: str, invocation: ProviderInvocation, *, fallback_used: bool = False) -> ProviderResponse:
        self.capability_registry.validate(provider_name, invocation.required_capabilities)
        provider = self.registry.get(provider_name)
        self.validator.validate_provider(provider)
        manifest = provider.manifest()
        health = provider.health()
        health_state = self.health_manager.check(provider_name)
        if self.config.health_check_enabled:
            health = provider.health()

        attempts = 0
        while True:
            attempts += 1
            try:
                response = provider.invoke(
                    invocation.prompt_package,
                    metadata={
                        **dict(invocation.metadata),
                        "retry_count": attempts - 1,
                        "fallback_used": fallback_used,
                        "provider_registry": self.registry.list(),
                        "active_provider": provider.name,
                        "provider_health": health.status,
                        "provider_health_state": health_state.as_dict(),
                        "provider_health_summary": self.health_manager.as_metadata(),
                        "provider_model": manifest.supported_models[0] if manifest.supported_models else provider.name,
                        "provider_capabilities": manifest.capabilities,
                        "provider_manifest_status": manifest.status,
                        "provider_configuration": self.configuration.as_metadata(),
                        "provider_environment": self.configuration.environment.as_dict(),
                        "provider_feature_flags": self.configuration.feature_flags.as_dict(),
                        "provider_fallback_enabled": self.configuration.settings.fallback_enabled,
                    },
                )
                updated_health_state = self.health_manager.record_execution(provider_name, response.latency)
                if isinstance(response.metadata, dict):
                    response.metadata.update(
                        {
                            "provider_health_state": updated_health_state.as_dict(),
                            "provider_health_summary": self.health_manager.as_metadata(),
                        }
                    )
                self.validator.validate_response(response)
                return response
            except Exception as exc:
                if not self.retry_policy.should_retry(attempts, exc):
                    raise


def create_default_provider_registry(
    factory: ProviderFactory | None = None,
    config: ProviderConfig | None = None,
    validator: ProviderValidator | None = None,
) -> ProviderRegistry:
    provider_factory = factory or create_default_provider_factory()
    provider_config = config or ProviderConfig()
    loader = ProviderLoader(factory=provider_factory, registry=ProviderRegistry(validator=validator), validator=validator)
    return loader.autoload(default_provider=provider_config.default_provider)


def create_default_capability_registry(registry: ProviderRegistry) -> ProviderCapabilityRegistry:
    capability_registry = ProviderCapabilityRegistry()
    for provider_name in registry.list():
        provider = registry.get(provider_name)
        capability_registry.register(provider.name, provider.capabilities())
    return capability_registry
