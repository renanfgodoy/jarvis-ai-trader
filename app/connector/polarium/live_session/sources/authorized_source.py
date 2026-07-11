from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from app.connector.polarium.live_session.models import AuthorizedSessionSnapshot
from app.connector.polarium.live_session.sources.errors import AuthorizedSourceUnavailableError
from app.connector.polarium.live_session.sources.models import MessageSourceAuthorization
from app.connector.polarium.oauth.lab import PolariumOAuthLabService


class AuthorizationProbe(Protocol):
    def current_authorization(self) -> MessageSourceAuthorization:
        ...


class OAuthLabAuthorizationProbe:
    """Reads only sanitized OAuth session state through the existing lab service."""

    def __init__(self, oauth_service: PolariumOAuthLabService | None = None) -> None:
        self._oauth_service = oauth_service or PolariumOAuthLabService()

    def current_authorization(self) -> MessageSourceAuthorization:
        session = self._oauth_service.session()
        if not session.has_token:
            return MessageSourceAuthorization(
                authorized=False,
                state="NO_AUTHORIZED_SESSION",
                reason="No previously authorized OAuth session is available through the safe session abstraction.",
                expires_at=None,
            )

        return MessageSourceAuthorization(
            authorized=True,
            state="AUTHORIZED",
            reason="A sanitized OAuth session exists, but the WebSocket authorization sequence is not proven yet.",
            expires_at=session.expires_at,
        )


@dataclass(frozen=True)
class StaticAuthorizationProbe:
    authorization: MessageSourceAuthorization

    def current_authorization(self) -> MessageSourceAuthorization:
        return self.authorization


class AuthorizedPolariumMessageSource:
    """Blocked concrete source until the real WS auth sequence is proven."""

    def __init__(self, authorization_probe: AuthorizationProbe | None = None) -> None:
        self._authorization_probe = authorization_probe or OAuthLabAuthorizationProbe()
        self._connected = False

    def authorization_status(self) -> AuthorizedSessionSnapshot:
        authorization = self._authorization_probe.current_authorization()
        if not authorization.authorized:
            return AuthorizedSessionSnapshot(
                authorized=False,
                status=authorization.state,
                reason=authorization.reason,
            )

        return AuthorizedSessionSnapshot(
            authorized=False,
            status="AUTHORIZED_SOURCE_UNAVAILABLE",
            reason=(
                "A sanitized authorization signal exists, but the real Polarium WebSocket URL, "
                "authentication handshake, and safe session-to-socket factory are not proven. "
                "No connection will be opened from this adapter."
            ),
        )

    def start(self, on_message: Callable[[dict[str, Any]], None]) -> None:
        raise AuthorizedSourceUnavailableError("AUTHORIZED_SOURCE_UNAVAILABLE")

    def stop(self) -> None:
        self._connected = False

    def is_authorized(self) -> bool:
        return self._authorization_probe.current_authorization().authorized

    def is_connected(self) -> bool:
        return self._connected
