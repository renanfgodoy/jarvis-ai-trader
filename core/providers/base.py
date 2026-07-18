from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter

from core.providers.health import unknown_provider_health
from core.providers.metadata import build_provider_fingerprint
from core.providers.models import ProviderHealth, ProviderManifest, ProviderMetadata, ProviderResponse as CoreProviderResponse, ProviderUsage
from shared.contracts import ProviderRequest, ProviderResponse


class BaseProvider:
    name = "base"
    provider_version = "1.0"
    placeholder_status = "placeholder"
    placeholder_response = "Provider placeholder response. No external API was called."
    declared_capabilities: tuple[str, ...] = ("chat",)
    supported_models: tuple[str, ...] = ("mock",)

    def __init__(self) -> None:
        self._initialized = False

    def initialize(self) -> None:
        self._initialized = True

    def shutdown(self) -> None:
        self.close()
        self._initialized = False

    def manifest(self) -> ProviderManifest:
        return ProviderManifest(
            provider=self.name,
            version=self.provider_version,
            supported_models=self.supported_models,
            capabilities=self.capabilities(),
            status="READY" if self._initialized else "ONLINE",
        )

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            fingerprint=build_provider_fingerprint(
                {
                    "provider": self.name,
                    "version": self.provider_version,
                    "capabilities": self.capabilities(),
                    "models": self.supported_models,
                }
            ),
            build="plugin-system-v1",
            runtime="local",
        )

    def execute(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(provider=self.name, status=self.placeholder_status, payload={"operation": request.operation})

    def connect(self) -> None:
        return None

    def health(self) -> ProviderHealth:
        return unknown_provider_health(self.name)

    def capabilities(self) -> tuple[str, ...]:
        return self.declared_capabilities

    def invoke(self, prompt_package, *, request_id: str | None = None, metadata: dict | None = None) -> CoreProviderResponse:
        started = perf_counter()
        response_text = self.placeholder_response
        usage = ProviderUsage(
            input_units=sum(len(message.content) for message in prompt_package.messages),
            output_units=len(response_text),
            total_units=sum(len(message.content) for message in prompt_package.messages) + len(response_text),
        )
        response_metadata = {
            **(metadata or {}),
            "placeholder": True,
            "external_api_called": False,
        }
        fingerprint = build_provider_fingerprint(
            {
                "provider": self.name,
                "provider_version": self.provider_version,
                "request_id": request_id or prompt_package.request_id,
                "status": self.placeholder_status,
                "response": response_text,
                "metadata": response_metadata,
            }
        )
        return CoreProviderResponse(
            provider=self.name,
            provider_version=self.provider_version,
            request_id=request_id or prompt_package.request_id,
            response=response_text,
            usage=usage,
            latency=perf_counter() - started,
            metadata=response_metadata,
            status=self.placeholder_status,
            fingerprint=fingerprint,
            model=self.supported_models[0] if self.supported_models else self.name,
            content=response_text,
            finish_reason="stop",
            timestamp=datetime.now(timezone.utc),
        )

    def close(self) -> None:
        return None

    @property
    def initialized(self) -> bool:
        return self._initialized
