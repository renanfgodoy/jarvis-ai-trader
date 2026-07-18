from core.providers.models import ProviderManifest

MOCK_PROVIDER_MANIFEST = ProviderManifest(
    provider="mock",
    version="1.0",
    author="Friday AI Platform",
    supported_models=("mock", "mock-trading"),
    capabilities=("chat", "json"),
    status="READY",
)
