from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class PlatformRequest:
    request_id: str
    module: str
    intent: str
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlatformResponse:
    request_id: str
    module: str
    status: str
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderRequest:
    provider: str
    operation: str
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderResponse:
    provider: str
    status: str
    payload: Mapping[str, Any] = field(default_factory=dict)

