from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock

from app.connector.polarium.live_session.models import LiveSessionMessage

LiveSessionListener = Callable[[LiveSessionMessage], None]


@dataclass(frozen=True)
class EventBusPublishResult:
    delivered: int
    failed: int


class PolariumLiveSessionEventBus:
    """In-process read-only event bus for decoded live session messages."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._listeners: dict[int, LiveSessionListener] = {}
        self._next_listener_id = 1
        self._published_count = 0
        self._listener_error_count = 0

    @property
    def listener_count(self) -> int:
        with self._lock:
            return len(self._listeners)

    @property
    def published_count(self) -> int:
        with self._lock:
            return self._published_count

    @property
    def listener_error_count(self) -> int:
        with self._lock:
            return self._listener_error_count

    def register(self, listener: LiveSessionListener) -> int:
        with self._lock:
            listener_id = self._next_listener_id
            self._next_listener_id += 1
            self._listeners[listener_id] = listener
            return listener_id

    def remove(self, listener_id: int) -> bool:
        with self._lock:
            return self._listeners.pop(listener_id, None) is not None

    def publish(self, message: LiveSessionMessage) -> EventBusPublishResult:
        with self._lock:
            listeners = tuple(self._listeners.values())
            self._published_count += 1

        delivered = 0
        failed = 0
        for listener in listeners:
            try:
                listener(message)
                delivered += 1
            except Exception:
                failed += 1

        if failed:
            with self._lock:
                self._listener_error_count += failed

        return EventBusPublishResult(delivered=delivered, failed=failed)
