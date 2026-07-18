from __future__ import annotations

from core.providers.base import BaseProvider
from core.providers.mock.manifest import MOCK_PROVIDER_MANIFEST
from core.providers.models import ProviderManifest
from shared.contracts import ProviderRequest, ProviderResponse


class MockProvider(BaseProvider):
    name = MOCK_PROVIDER_MANIFEST.provider
    provider_version = MOCK_PROVIDER_MANIFEST.version
    placeholder_status = "placeholder"
    placeholder_response = "Mock provider placeholder response."
    declared_capabilities = MOCK_PROVIDER_MANIFEST.capabilities
    supported_models = MOCK_PROVIDER_MANIFEST.supported_models

    def manifest(self) -> ProviderManifest:
        status = "READY" if self.initialized else MOCK_PROVIDER_MANIFEST.status
        return ProviderManifest(
            provider=MOCK_PROVIDER_MANIFEST.provider,
            version=MOCK_PROVIDER_MANIFEST.version,
            author=MOCK_PROVIDER_MANIFEST.author,
            supported_models=MOCK_PROVIDER_MANIFEST.supported_models,
            capabilities=MOCK_PROVIDER_MANIFEST.capabilities,
            status=status,
        )

    def execute(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(provider=self.name, status="placeholder", payload={"operation": request.operation})
