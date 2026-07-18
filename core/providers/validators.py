from __future__ import annotations

import json

from core.providers.base import BaseProvider
from core.providers.errors import InvalidProviderConfigError, InvalidProviderError, InvalidProviderResponseError
from core.providers.models import ProviderConfig, ProviderManifest, ProviderRequest, ProviderResponse


class ProviderValidator:
    def validate_config(self, config: ProviderConfig) -> None:
        if not config.default_provider.strip():
            raise InvalidProviderConfigError("default_provider is required")
        if config.retry_attempts < 1:
            raise InvalidProviderConfigError("retry_attempts must be >= 1")
        if config.request_timeout <= 0:
            raise InvalidProviderConfigError("request_timeout must be positive")

    def validate_provider(self, provider: BaseProvider) -> None:
        required = ("initialize", "shutdown", "health", "execute", "metadata", "manifest", "capabilities", "invoke", "close")
        for method in required:
            if not callable(getattr(provider, method, None)):
                raise InvalidProviderError(f"provider missing method: {method}")
        self.validate_manifest(provider.manifest())

    def validate_manifest(self, manifest: ProviderManifest) -> None:
        if not manifest.provider.strip():
            raise InvalidProviderError("provider manifest name is required")
        if not manifest.version.strip():
            raise InvalidProviderError("provider manifest version is required")
        if not manifest.supported_models:
            raise InvalidProviderError("provider manifest requires supported models")
        if not manifest.capabilities:
            raise InvalidProviderError("provider manifest requires capabilities")

    def validate_request(self, request: ProviderRequest) -> None:
        if not request.identity.strip():
            raise InvalidProviderConfigError("provider request identity is required")
        if not request.prompt.strip():
            raise InvalidProviderConfigError("provider request prompt is required")
        if request.temperature < 0:
            raise InvalidProviderConfigError("temperature must be non-negative")
        if request.top_p <= 0:
            raise InvalidProviderConfigError("top_p must be positive")
        if request.max_tokens < 1:
            raise InvalidProviderConfigError("max_tokens must be >= 1")

    def validate_response(self, response: ProviderResponse) -> None:
        if not response.provider.strip():
            raise InvalidProviderResponseError("provider is required")
        if not response.provider_version.strip():
            raise InvalidProviderResponseError("provider_version is required")
        if not response.request_id.strip():
            raise InvalidProviderResponseError("request_id is required")
        if response.latency < 0:
            raise InvalidProviderResponseError("latency must be non-negative")
        json.dumps(response.metadata, ensure_ascii=False, sort_keys=True, default=str)
