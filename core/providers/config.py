from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from core.providers.environment import ProviderEnvironment
from core.providers.feature_flags import FeatureFlags
from core.providers.settings import ProviderSettings


@dataclass(frozen=True)
class ProviderConfiguration:
    settings: ProviderSettings = ProviderSettings()
    feature_flags: FeatureFlags = FeatureFlags()
    environment: ProviderEnvironment = ProviderEnvironment()

    @classmethod
    def from_environment(cls, environ: Mapping[str, str]) -> "ProviderConfiguration":
        default_provider = environ.get("FRIDAY_PROVIDER_DEFAULT", "mock")
        fallback_provider = environ.get("FRIDAY_PROVIDER_FALLBACK", "mock")
        fallback_enabled = _read_bool(environ, "FRIDAY_PROVIDER_FALLBACK_ENABLED", True)
        health_check_enabled = _read_bool(environ, "FRIDAY_PROVIDER_HEALTH_ENABLED", True)
        debug = _read_bool(environ, "FRIDAY_PROVIDER_DEBUG", True)
        environment_name = environ.get("FRIDAY_ENVIRONMENT", "development")

        feature_flags = FeatureFlags(
            mock=_read_bool(environ, "FRIDAY_PROVIDER_MOCK_ENABLED", True),
            openai=_read_bool(environ, "FRIDAY_PROVIDER_OPENAI_ENABLED", False),
            gemini=_read_bool(environ, "FRIDAY_PROVIDER_GEMINI_ENABLED", False),
            anthropic=_read_bool(environ, "FRIDAY_PROVIDER_ANTHROPIC_ENABLED", False),
            ollama=_read_bool(environ, "FRIDAY_PROVIDER_OLLAMA_ENABLED", False),
            lmstudio=_read_bool(environ, "FRIDAY_PROVIDER_LMSTUDIO_ENABLED", False),
            azure=_read_bool(environ, "FRIDAY_PROVIDER_AZURE_ENABLED", False),
        )
        enabled = feature_flags.enabled_providers() or ("mock",)
        priority = _read_sequence(environ.get("FRIDAY_PROVIDER_PRIORITY")) or enabled

        return cls(
            settings=ProviderSettings(
                default_provider=default_provider,
                enabled_providers=enabled,
                provider_priority=priority,
                fallback_provider=fallback_provider,
                fallback_enabled=fallback_enabled,
                health_check_enabled=health_check_enabled,
                debug=debug,
            ),
            feature_flags=feature_flags,
            environment=ProviderEnvironment(
                name=environment_name,
                debug=debug,
                external_providers_allowed=any(
                    (
                        feature_flags.openai,
                        feature_flags.gemini,
                        feature_flags.anthropic,
                        feature_flags.ollama,
                        feature_flags.lmstudio,
                        feature_flags.azure,
                    )
                ),
            ),
        )

    @classmethod
    def compatibility(cls, default_provider: str, fallback_provider: str | None = None) -> "ProviderConfiguration":
        enabled = (
            "mock",
            "openai",
            "anthropic",
            "google",
            "groq",
            "ollama",
            "lmstudio",
            "azure",
        )
        default = default_provider.strip().lower() or "mock"
        fallback = (fallback_provider or "mock").strip().lower() or "mock"
        return cls(
            settings=ProviderSettings(
                default_provider=default,
                enabled_providers=enabled,
                provider_priority=(default, *tuple(provider for provider in enabled if provider != default)),
                fallback_provider=fallback,
                fallback_enabled=bool(fallback_provider),
                health_check_enabled=True,
                debug=True,
            ),
            feature_flags=FeatureFlags(
                mock=True,
                openai=True,
                anthropic=True,
                ollama=True,
                lmstudio=True,
                azure=True,
            ),
            environment=ProviderEnvironment(name="compatibility", debug=True, external_providers_allowed=False),
        )

    @property
    def default_provider(self) -> str:
        return self.settings.default_provider

    def as_metadata(self) -> dict[str, object]:
        return {
            "default_provider": self.settings.default_provider,
            "enabled_providers": self.settings.enabled_providers,
            "provider_priority": self.settings.provider_priority,
            "fallback_enabled": self.settings.fallback_enabled,
            "fallback_provider": self.settings.fallback_provider,
            "health_check_enabled": self.settings.health_check_enabled,
            "debug": self.settings.debug,
            "environment": self.environment.as_dict(),
            "feature_flags": self.feature_flags.as_dict(),
        }


def _read_bool(environ: Mapping[str, str], key: str, default: bool) -> bool:
    raw = environ.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _read_sequence(raw: str | None) -> tuple[str, ...]:
    if raw is None:
        return ()
    values: list[str] = []
    for value in raw.split(","):
        normalized = value.strip().lower()
        if normalized and normalized not in values:
            values.append(normalized)
    return tuple(values)
