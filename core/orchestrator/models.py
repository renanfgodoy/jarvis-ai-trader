from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Mapping

from core.providers.models import ProviderResponse


ExecutionStatus = Literal["PENDING", "RUNNING", "SUCCESS", "FAILED"]


@dataclass(frozen=True)
class ExecutionRequest:
    request_id: str
    module: str
    input: str
    identity: str | None = None
    provider: str | None = None
    language: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    template_id: str | None = None
    template_version: str | None = None
    response_format: str = "text"

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            object.__setattr__(self, "created_at", self.created_at.replace(tzinfo=timezone.utc))


@dataclass(frozen=True)
class ExecutionMetadata:
    execution_id: str
    request_id: str
    started_at: datetime
    finished_at: datetime | None
    duration: float | None
    provider: str | None
    provider_version: str | None
    identity: str | None
    module: str
    pipeline_version: str
    fingerprint: str
    status: ExecutionStatus


@dataclass(frozen=True)
class ExecutionResponse:
    request_id: str
    identity: str
    provider: str
    provider_response: ProviderResponse
    latency: float
    status: ExecutionStatus
    metadata: ExecutionMetadata
    fingerprint: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))
