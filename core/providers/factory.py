from __future__ import annotations

from collections.abc import Callable

from core.providers.anthropic import AnthropicProvider
from core.providers.base import BaseProvider
from core.providers.errors import DuplicateProviderError, InvalidProviderError, ProviderNotFoundError
from core.providers.google import GoogleProvider
from core.providers.groq import GroqProvider
from core.providers.lmstudio import LMStudioProvider
from core.providers.mock import MockProvider
from core.providers.ollama import OllamaProvider
from core.providers.openai import OpenAIProvider
from core.providers.validators import ProviderValidator


ProviderBuilder = Callable[[], BaseProvider]


class ProviderFactory:
    def __init__(self, validator: ProviderValidator | None = None) -> None:
        self.validator = validator or ProviderValidator()
        self._builders: dict[str, ProviderBuilder] = {}

    def register(self, name: str, builder: ProviderBuilder) -> None:
        self.register_builder(name, builder)

    def register_builder(self, name: str, builder: ProviderBuilder) -> None:
        normalized = name.strip().lower()
        if not normalized:
            raise ValueError("provider name is required")
        if normalized in self._builders:
            raise DuplicateProviderError(f"provider builder already registered: {normalized}")
        sample = builder()
        self.validator.validate_provider(sample)
        self._builders[normalized] = builder

    def create(self, name: str) -> BaseProvider:
        normalized = name.strip().lower()
        if normalized not in self._builders:
            raise ProviderNotFoundError(f"provider builder not registered: {normalized}")
        provider = self._builders[normalized]()
        if provider.name != normalized:
            raise InvalidProviderError(f"builder returned provider {provider.name}, expected {normalized}")
        self.validator.validate_provider(provider)
        return provider

    def list(self) -> tuple[str, ...]:
        return self.list_builders()

    def list_builders(self) -> tuple[str, ...]:
        return tuple(sorted(self._builders))

    def has_builder(self, name: str) -> bool:
        return name.strip().lower() in self._builders

    def unregister_builder(self, name: str) -> None:
        normalized = name.strip().lower()
        if normalized not in self._builders:
            raise ProviderNotFoundError(f"provider builder not registered: {normalized}")
        del self._builders[normalized]

    def clear(self) -> None:
        self._builders.clear()


def create_default_provider_factory() -> ProviderFactory:
    factory = ProviderFactory()
    for provider_class in (
        MockProvider,
        OpenAIProvider,
        AnthropicProvider,
        GoogleProvider,
        GroqProvider,
        OllamaProvider,
        LMStudioProvider,
    ):
        factory.register_builder(provider_class.name, provider_class)
    return factory
