from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class ExecutionEvent:
    name: str
    stage: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))


EVENT_EXECUTION_STARTED = "ExecutionStarted"
EVENT_IDENTITY_RESOLVED = "IdentityResolved"
EVENT_PROMPT_BUILT = "PromptBuilt"
EVENT_PROVIDER_SELECTED = "ProviderSelected"
EVENT_PROVIDER_EXECUTED = "ProviderExecuted"
EVENT_RESPONSE_NORMALIZED = "ResponseNormalized"
EVENT_EXECUTION_FINISHED = "ExecutionFinished"
EVENT_EXECUTION_FAILED = "ExecutionFailed"
