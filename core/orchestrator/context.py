from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from core.identity.models import IdentityResult
from core.orchestrator.events import ExecutionEvent
from core.orchestrator.models import ExecutionMetadata, ExecutionRequest, ExecutionResponse, ExecutionStatus
from core.prompts.models import PromptPackage
from core.providers.models import ProviderResponse


@dataclass
class ExecutionContext:
    request: ExecutionRequest
    identity_result: IdentityResult | None = None
    prompt_result: PromptPackage | None = None
    provider_result: ProviderResponse | None = None
    execution_metadata: ExecutionMetadata | None = None
    response: ExecutionResponse | None = None
    status: ExecutionStatus = "PENDING"
    pipeline_stage: str = "created"
    errors: list[str] = field(default_factory=list)
    events: list[ExecutionEvent] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scratchpad: dict[str, Any] = field(default_factory=dict)

    def add_event(self, name: str, stage: str, metadata: dict | None = None) -> None:
        self.events.append(ExecutionEvent(name=name, stage=stage, metadata=metadata or {}))
