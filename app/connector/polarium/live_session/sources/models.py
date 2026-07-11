from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

AuthorizationSourceState = Literal["AUTHORIZED", "NO_AUTHORIZED_SESSION", "AUTHORIZED_SOURCE_UNAVAILABLE"]


@dataclass(frozen=True)
class MessageSourceAuthorization:
    authorized: bool
    state: AuthorizationSourceState
    reason: str
    expires_at: datetime | None = None

    def sanitized(self) -> dict:
        return {
            "authorized": self.authorized,
            "state": self.state,
            "reason": self.reason,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
