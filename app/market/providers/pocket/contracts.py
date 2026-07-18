from __future__ import annotations

from typing import Protocol

from app.market.providers.pocket.models import PocketDomainEvent


class PocketTransport(Protocol):
    def start(self) -> None: ...

    def stop(self) -> None: ...

    def is_running(self) -> bool: ...

    def next_event(self) -> PocketDomainEvent | None: ...

    def status(self) -> dict: ...

