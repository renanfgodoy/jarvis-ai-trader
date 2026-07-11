from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from app.connector.polarium.live_session.models import AuthorizedSessionSnapshot


class PolariumMessageSource(Protocol):
    """Read-only source contract consumed by PolariumLiveSessionManager."""

    def authorization_status(self) -> AuthorizedSessionSnapshot:
        ...

    def start(self, on_message: Callable[[dict[str, Any]], None]) -> None:
        ...

    def stop(self) -> None:
        ...

    def is_authorized(self) -> bool:
        ...

    def is_connected(self) -> bool:
        ...
