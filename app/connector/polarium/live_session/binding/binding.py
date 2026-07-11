from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.connector.polarium.live_session.binding.errors import (
    BINDING_FAILED,
    INVALID_SESSION_HANDLE,
    SESSION_EXPIRED,
    SESSION_NOT_AUTHORIZED,
    SESSION_NOT_AVAILABLE,
    UNSUPPORTED_SESSION,
    AuthorizedSessionBindingError,
    BindingFailedError,
    InvalidSessionHandleError,
    SessionExpiredError,
    SessionNotAuthorizedError,
    SessionNotAvailableError,
    UnsupportedSessionError,
)
from app.connector.polarium.live_session.binding.models import AuthorizedSessionHandle, BindingStatus, unavailable_status
from app.connector.polarium.live_session.binding.provider import AuthorizedSessionProvider, UnavailableAuthorizedSessionProvider
from app.connector.polarium.live_session.models import AuthorizedSessionSnapshot

SENSITIVE_MARKERS = (
    "token",
    "cookie",
    "bearer",
    "authorization",
    "headers",
    "ssid",
    "password",
    "client_secret",
    "code_verifier",
    "payload",
)


class AuthenticatedSessionBinding:
    """Validates an already-authorized session handle without creating transport."""

    def __init__(self, provider: AuthorizedSessionProvider | None = None) -> None:
        self._provider = provider or UnavailableAuthorizedSessionProvider()

    def bind(self) -> AuthorizedSessionHandle:
        handle = self._load_handle()
        self._validate(handle)
        return handle

    def status(self) -> BindingStatus:
        try:
            handle = self.bind()
        except AuthorizedSessionBindingError as exc:
            return unavailable_status(reason=exc.reason, error_code=exc.code)
        except Exception:
            return unavailable_status(reason="BINDING_FAILED", error_code=BINDING_FAILED)

        return BindingStatus(
            authorized=handle.authorized,
            connected=handle.connected,
            available=handle.available,
            reason=handle.reason,
            created_at=handle.created_at,
            expires_at=handle.expires_at,
            source=handle.source,
            error_code=None,
        )

    def authorization_snapshot(self) -> AuthorizedSessionSnapshot:
        status = self.status()
        return AuthorizedSessionSnapshot(
            authorized=status.authorized and status.available,
            status="AUTHORIZED_SESSION_AVAILABLE" if status.available else status.error_code or SESSION_NOT_AVAILABLE,
            reason=status.reason,
        )

    def _load_handle(self) -> AuthorizedSessionHandle:
        try:
            handle = self._provider.current_session()
        except AuthorizedSessionBindingError:
            raise
        except Exception as exc:
            raise BindingFailedError("BINDING_FAILED") from exc

        if not isinstance(handle, AuthorizedSessionHandle):
            raise InvalidSessionHandleError("INVALID_SESSION_HANDLE")
        return handle

    def _validate(self, handle: AuthorizedSessionHandle) -> None:
        if _contains_sensitive_marker(handle.sanitized()):
            raise InvalidSessionHandleError("INVALID_SESSION_HANDLE")
        if not handle.available:
            raise SessionNotAvailableError("AUTHORIZED_SESSION_UNAVAILABLE")
        if not handle.authorized:
            raise SessionNotAuthorizedError("AUTHORIZED_SESSION_UNAVAILABLE")
        if handle.expires_at and handle.expires_at <= datetime.now(timezone.utc):
            raise SessionExpiredError("AUTHORIZED_SESSION_EXPIRED")
        if not handle.capabilities.read_only or not handle.capabilities.message_stream:
            raise UnsupportedSessionError("UNSUPPORTED_SESSION")
        if handle.capabilities.orders or handle.capabilities.credential_export:
            raise UnsupportedSessionError("UNSUPPORTED_SESSION")


def _contains_sensitive_marker(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in SENSITIVE_MARKERS):
                return True
            if _contains_sensitive_marker(child):
                return True
    elif isinstance(value, list):
        return any(_contains_sensitive_marker(child) for child in value)
    elif isinstance(value, str):
        lowered = value.lower()
        return any(marker in lowered for marker in SENSITIVE_MARKERS)
    return False
