from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from core.identity.exceptions import InvalidIdentityRequestError


SerializableMapping = Mapping[str, Any]


@dataclass(frozen=True)
class IdentityProfile:
    identity_id: str
    version: str
    display_name: str
    description: str
    language: str
    tone: str
    style: str
    principles: tuple[str, ...]
    capabilities: tuple[str, ...]
    limitations: tuple[str, ...]
    metadata: SerializableMapping = field(default_factory=dict)
    fingerprint: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            object.__setattr__(self, "created_at", self.created_at.replace(tzinfo=timezone.utc))


@dataclass(frozen=True)
class IdentityRequest:
    module: str
    requested_identity: str | None = None
    language: str | None = None
    metadata: SerializableMapping = field(default_factory=dict)
    context: SerializableMapping = field(default_factory=dict)
    request_id: str | None = None

    def __post_init__(self) -> None:
        if not self.module or not self.module.strip():
            raise InvalidIdentityRequestError("module is required")
        if self.metadata is None or not isinstance(self.metadata, Mapping):
            raise InvalidIdentityRequestError("metadata must be a mapping")
        if self.context is None or not isinstance(self.context, Mapping):
            raise InvalidIdentityRequestError("context must be a mapping")


@dataclass(frozen=True)
class IdentityResult:
    request_id: str
    identity_profile: IdentityProfile
    resolved_identity: str
    metadata: SerializableMapping
    fingerprint: str
    timestamp: datetime

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))
