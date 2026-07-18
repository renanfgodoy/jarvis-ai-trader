from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from app.market.providers.pocket.cdp_models import PocketCDPEvent, PocketCDPTarget


class FakePocketCDPClient:
    def __init__(self, *, targets: Iterable[PocketCDPTarget] = (), events: Iterable[PocketCDPEvent] = ()) -> None:
        self._targets = tuple(targets)
        self._events = deque(events)
        self.attached_target_id: str | None = None
        self.network_enabled = False
        self.closed = False

    def list_targets(self) -> tuple[PocketCDPTarget, ...]:
        return self._targets

    def attach_target(self, target_id: str) -> None:
        self.attached_target_id = target_id

    def enable_network(self) -> None:
        self.network_enabled = True

    def next_event(self) -> PocketCDPEvent | None:
        if self.closed or not self._events:
            return None
        return self._events.popleft()

    def close(self) -> None:
        self.closed = True
        self._events.clear()

