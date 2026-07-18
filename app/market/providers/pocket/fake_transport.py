from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from app.market.providers.pocket.models import PocketDomainEvent


class FakePocketTransport:
    def __init__(self, events: Iterable[PocketDomainEvent] = ()) -> None:
        self._events = deque(events)
        self._running = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def next_event(self) -> PocketDomainEvent | None:
        if not self._running or not self._events:
            return None
        return self._events.popleft()

    def status(self) -> dict:
        return {"transport": "FAKE", "running": self._running, "queued_events": len(self._events)}

