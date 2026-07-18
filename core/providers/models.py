from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Mapping

from core.prompts.models import PromptPackage


ProviderStatus = Literal["success", "placeholder", "not_configured", "error"]
HealthStatus = Literal["ONLINE", "OFFLINE", "DEGRADED", "LIMITED", "RATE_LIMITED", "UNKNOWN"]


@dataclass(frozen=True)
class ProviderConfig:
    default_provider: str = "openai"
    fallback_provider: str | None = None
    retry_enabled: bool = False
    retry_attempts: int = 1
    request_timeout: float = 30.0
    health_check_enabled: bool = True
    strict_capabilities: bool = True


@dataclass(frozen=True)
class ProviderUsage:
    input_units: int = 0
    output_units: int = 0
    total_units: int = 0


@dataclass(frozen=True)
class ProviderManifest:
    provider: str
    version: str = "1.0"
    author: str = "Friday AI Platform"
    supported_models: tuple[str, ...] = ("mock",)
    capabilities: tuple[str, ...] = ("chat",)
    status: str = "READY"


@dataclass(frozen=True)
class ProviderMetadata:
    fingerprint: str
    build: str = "development"
    runtime: str = "local"


@dataclass(frozen=True)
class ProviderRequest:
    identity: str
    prompt: str
    language: str = "pt-BR"
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 1024
    metadata: Mapping[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))


@dataclass(frozen=True)
class ProviderHealth:
    provider: str
    status: HealthStatus = "UNKNOWN"
    detail: str = "placeholder"
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.checked_at.tzinfo is None:
            object.__setattr__(self, "checked_at", self.checked_at.replace(tzinfo=timezone.utc))


@dataclass(frozen=True)
class ProviderResponse:
    provider: str
    provider_version: str
    request_id: str
    response: str
    usage: ProviderUsage
    latency: float
    metadata: Mapping[str, Any]
    status: ProviderStatus
    fingerprint: str
    model: str = "mock"
    content: str | None = None
    finish_reason: str = "stop"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))
        if self.content is None:
            object.__setattr__(self, "content", self.response)


@dataclass(frozen=True)
class ProviderInvocation:
    prompt_package: PromptPackage
    provider: str | None = None
    required_capabilities: tuple[str, ...] = ("chat",)
    metadata: Mapping[str, Any] = field(default_factory=dict)
