from __future__ import annotations

from typing import Protocol

from app.connector.polarium.live_session.binding.models import AuthorizedSessionHandle, unavailable_status


class AuthorizedSessionProvider(Protocol):
    """Provides an already-authorized session handle without exposing secrets."""

    def current_session(self) -> AuthorizedSessionHandle:
        ...


class UnavailableAuthorizedSessionProvider:
    """Safe default provider for processes without a reusable authorized session."""

    def current_session(self) -> AuthorizedSessionHandle:
        status = unavailable_status(
            reason="AUTHORIZED_SESSION_UNAVAILABLE",
            error_code="SESSION_NOT_AVAILABLE",
            source="unavailable_authorized_session_provider",
        )
        return AuthorizedSessionHandle(
            authorized=status.authorized,
            connected=status.connected,
            available=status.available,
            reason=status.reason,
            created_at=status.created_at,
            expires_at=status.expires_at,
            source=status.source,
        )
