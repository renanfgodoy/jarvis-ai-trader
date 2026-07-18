from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from core.orchestrator.models import ExecutionResponse


ModuleStatus = str


@dataclass(frozen=True)
class ModuleRequest:
    module: str
    payload: str
    identity: str | None = None
    provider: str | None = None
    language: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    request_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))


@dataclass(frozen=True)
class ModuleResponse:
    status: ModuleStatus
    module: str
    identity: str
    provider: str
    execution: ExecutionResponse
    response: str
    latency: float
    metadata: Mapping[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))
