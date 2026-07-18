from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.providers.models import ProviderHealth

if TYPE_CHECKING:
    from core.providers.registry import ProviderRegistry


@dataclass
class ProviderHealthState:
    status: str = "UNKNOWN"
    uptime: float = 0.0
    last_execution: datetime | None = None
    last_error: str | None = None
    latency_average: float = 0.0
    request_count: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "uptime": self.uptime,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "last_error": self.last_error,
            "latency_average": self.latency_average,
            "request_count": self.request_count,
        }


class ProviderHealthManager:
    def __init__(self, registry: "ProviderRegistry | None" = None) -> None:
        self.registry = registry
        self._states: dict[str, ProviderHealthState] = {}

    def check(self, provider: str) -> ProviderHealthState:
        state = self._states.setdefault(provider, ProviderHealthState())
        state.uptime = max(0.0, (datetime.now(timezone.utc) - state.started_at).total_seconds())
        if self.registry is not None:
            health = self.registry.get(provider).health()
            state.status = health.status
            if health.detail and health.status in {"OFFLINE", "DEGRADED", "LIMITED", "RATE_LIMITED"}:
                state.last_error = health.detail
        return state

    def check_all(self) -> dict[str, ProviderHealthState]:
        if self.registry is None:
            return dict(self._states)
        return {provider: self.check(provider) for provider in self.registry.list()}

    def record_execution(self, provider: str, latency: float, *, error: Exception | None = None) -> ProviderHealthState:
        state = self._states.setdefault(provider, ProviderHealthState())
        state.request_count += 1
        state.last_execution = datetime.now(timezone.utc)
        if state.request_count == 1:
            state.latency_average = latency
        else:
            state.latency_average = ((state.latency_average * (state.request_count - 1)) + latency) / state.request_count
        if error is None:
            state.status = "ONLINE"
            state.last_error = None
        else:
            state.status = "DEGRADED"
            state.last_error = error.__class__.__name__
        state.uptime = max(0.0, (state.last_execution - state.started_at).total_seconds())
        return state

    def as_metadata(self) -> dict[str, object]:
        return {provider: state.as_dict() for provider, state in self.check_all().items()}


def unknown_provider_health(provider: str) -> ProviderHealth:
    return ProviderHealth(provider=provider, status="UNKNOWN", detail="placeholder provider has not been checked")
