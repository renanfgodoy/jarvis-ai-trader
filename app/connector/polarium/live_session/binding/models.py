from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class SessionCapabilities:
    read_only: bool = True
    message_stream: bool = True
    orders: bool = False
    credential_export: bool = False

    def sanitized(self) -> dict[str, bool]:
        return {
            "read_only": self.read_only,
            "message_stream": self.message_stream,
            "orders": self.orders,
            "credential_export": self.credential_export,
        }


@dataclass(frozen=True)
class AuthorizedSessionHandle:
    authorized: bool
    connected: bool
    available: bool
    reason: str
    created_at: datetime | None
    expires_at: datetime | None
    source: str
    capabilities: SessionCapabilities = field(default_factory=SessionCapabilities)

    def sanitized(self) -> dict:
        return {
            "authorized": self.authorized,
            "connected": self.connected,
            "available": self.available,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source": self.source,
            "capabilities": self.capabilities.sanitized(),
        }


@dataclass(frozen=True)
class BindingStatus:
    authorized: bool
    connected: bool
    available: bool
    reason: str
    created_at: datetime | None
    expires_at: datetime | None
    source: str
    error_code: str | None = None

    def sanitized(self) -> dict:
        return {
            "authorized": self.authorized,
            "connected": self.connected,
            "available": self.available,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source": self.source,
            "error_code": self.error_code,
        }


def unavailable_status(reason: str, error_code: str | None = None, source: str = "authorized_session_provider") -> BindingStatus:
    return BindingStatus(
        authorized=False,
        connected=False,
        available=False,
        reason=reason,
        created_at=None,
        expires_at=None,
        source=source,
        error_code=error_code,
    )
