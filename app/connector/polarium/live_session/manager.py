from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Protocol

from app.connector.polarium.live_session.event_bus import PolariumLiveSessionEventBus
from app.connector.polarium.live_session.models import AuthorizedSessionSnapshot, LiveSessionMessage, LiveSessionStatus

SENSITIVE_MARKERS = (
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "bearer",
    "cookie",
    "ssid",
    "password",
    "email",
    "client_secret",
    "code_verifier",
    "headers",
)


class PolariumLiveMessageSource(Protocol):
    def authorization_status(self) -> AuthorizedSessionSnapshot:
        ...

    def start(self, on_message: Callable[[dict[str, Any]], None]) -> None:
        ...

    def stop(self) -> None:
        ...


class UnavailablePolariumLiveMessageSource:
    """Safe default: no token is read and no WebSocket is opened."""

    def authorization_status(self) -> AuthorizedSessionSnapshot:
        return AuthorizedSessionSnapshot(
            authorized=False,
            status="NO_AUTHORIZED_SESSION",
            reason=(
                "No safe authorized Polarium backend session source is configured. "
                "The runtime will not read raw tokens, cookies, bearer headers, SSID, or HAR files."
            ),
        )

    def start(self, on_message: Callable[[dict[str, Any]], None]) -> None:
        raise RuntimeError("Authorized Polarium live message source is unavailable.")

    def stop(self) -> None:
        return None


class PolariumLiveSessionManager:
    """Single-process foundation for an authorized read-only Polarium live session."""

    def __init__(
        self,
        message_source: PolariumLiveMessageSource | None = None,
        event_bus: PolariumLiveSessionEventBus | None = None,
        max_reconnect_attempts: int = 0,
    ) -> None:
        self._message_source = message_source or UnavailablePolariumLiveMessageSource()
        self.event_bus = event_bus or PolariumLiveSessionEventBus()
        self.max_reconnect_attempts = max_reconnect_attempts
        self._lock = RLock()
        self._state = "STOPPED"
        self._authorized = False
        self._connected = False
        self._started_at: datetime | None = None
        self._last_message_at: datetime | None = None
        self._last_event_name: str | None = None
        self._message_count = 0
        self._reconnect_count = 0
        self._last_error_code: str | None = None

    def start(self) -> LiveSessionStatus:
        with self._lock:
            if self._state in {"STARTING", "CONNECTED", "RECONNECTING"}:
                return self.status()

            self._state = "STARTING"
            self._last_error_code = None
            authorization = self._message_source.authorization_status()
            self._authorized = authorization.authorized
            if not authorization.authorized:
                self._state = "ERROR"
                self._connected = False
                self._last_error_code = authorization.status
                return self.status()

            try:
                self._message_source.start(self.publish_decoded_message)
            except Exception:
                self._state = "ERROR"
                self._connected = False
                self._last_error_code = "CONNECTION_START_FAILED"
                return self.status()

            self._state = "CONNECTED"
            self._connected = True
            self._started_at = _utcnow()
            return self.status()

    def stop(self) -> LiveSessionStatus:
        with self._lock:
            if self._state == "STOPPED":
                return self.status()

            was_connected = self._connected
            self._state = "STOPPING"
            self._connected = False

        if was_connected:
            try:
                self._message_source.stop()
            except Exception:
                with self._lock:
                    self._last_error_code = "CONNECTION_STOP_FAILED"

        with self._lock:
            self._state = "STOPPED"
            return self.status()

    def status(self) -> LiveSessionStatus:
        return LiveSessionStatus(
            state=self._state,  # type: ignore[arg-type]
            authorized=self._authorized,
            connected=self._connected,
            started_at=self._started_at,
            last_message_at=self._last_message_at,
            last_event_name=self._last_event_name,
            message_count=self._message_count,
            reconnect_count=self._reconnect_count,
            last_error_code=self._last_error_code,
        )

    def publish_decoded_message(self, message: dict[str, Any]) -> LiveSessionStatus:
        with self._lock:
            if not self._connected:
                self._last_error_code = "SESSION_NOT_CONNECTED"
                return self.status()
            if not isinstance(message, dict):
                self._last_error_code = "INVALID_MESSAGE"
                return self.status()
            if _find_sensitive_marker(message):
                self._last_error_code = "SENSITIVE_MESSAGE_REJECTED"
                return self.status()

            self._message_count += 1
            received_at = _utcnow()
            event_name = _extract_event_name(message)
            self._last_message_at = received_at
            self._last_event_name = event_name
            session_message = LiveSessionMessage(
                event_name=event_name,
                received_at=received_at,
                message_sequence=self._message_count,
                connection_state=self._state,  # type: ignore[arg-type]
                payload=message,
            )

        self.event_bus.publish(session_message)
        return self.status()


def _extract_event_name(message: dict[str, Any]) -> str | None:
    name = message.get("name") or message.get("event") or message.get("type")
    return str(name) if name is not None else None


def _find_sensitive_marker(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in SENSITIVE_MARKERS):
                return str(key)
            found = _find_sensitive_marker(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_sensitive_marker(child)
            if found:
                return found
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in SENSITIVE_MARKERS):
            return "$"
    return None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
