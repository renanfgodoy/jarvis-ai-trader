import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.connector.polarium.live_session.binding import (
    SESSION_EXPIRED,
    SESSION_NOT_AVAILABLE,
    UNSUPPORTED_SESSION,
    AuthenticatedSessionBinding,
    AuthorizedSessionHandle,
    SessionCapabilities,
)
from app.connector.polarium.live_session.binding.provider import UnavailableAuthorizedSessionProvider
from app.connector.polarium.live_session.sources.authorized_source import AuthorizedPolariumMessageSource, StaticAuthorizationProbe
from app.connector.polarium.live_session.sources.models import MessageSourceAuthorization


class FakeProvider:
    def __init__(self, session: Any) -> None:
        self.session = session
        self.calls = 0

    def current_session(self) -> Any:
        self.calls += 1
        return self.session


def authorized_handle(**overrides: Any) -> AuthorizedSessionHandle:
    now = datetime.now(timezone.utc)
    values = {
        "authorized": True,
        "connected": True,
        "available": True,
        "reason": "AUTHORIZED_SESSION_AVAILABLE",
        "created_at": now,
        "expires_at": now + timedelta(minutes=10),
        "source": "fake_authorized_session_provider",
        "capabilities": SessionCapabilities(),
    }
    values.update(overrides)
    return AuthorizedSessionHandle(**values)


def source_authorization() -> MessageSourceAuthorization:
    return MessageSourceAuthorization(
        authorized=True,
        state="AUTHORIZED",
        reason="Sanitized fake authorization.",
    )


def assert_no_secret_markers(payload: dict | str) -> None:
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    lowered = text.lower()
    for marker in [
        "access_token",
        "refresh_token",
        "cookie",
        "bearer",
        "authorization",
        "ssid",
        "password",
        "client_secret",
        "code_verifier",
        "headers",
        "payload",
    ]:
        assert marker not in lowered


def test_unavailable_provider_returns_sanitized_status() -> None:
    binding = AuthenticatedSessionBinding(UnavailableAuthorizedSessionProvider())

    status = binding.status().sanitized()

    assert status["available"] is False
    assert status["authorized"] is False
    assert status["error_code"] == SESSION_NOT_AVAILABLE
    assert status["reason"] == "AUTHORIZED_SESSION_UNAVAILABLE"
    assert_no_secret_markers(status)


def test_invalid_session_handle_is_blocked() -> None:
    binding = AuthenticatedSessionBinding(FakeProvider({"authorized": True}))

    status = binding.status().sanitized()

    assert status["available"] is False
    assert status["error_code"] == "INVALID_SESSION_HANDLE"
    assert_no_secret_markers(status)


def test_expired_session_is_blocked() -> None:
    expired = authorized_handle(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))
    binding = AuthenticatedSessionBinding(FakeProvider(expired))

    status = binding.status().sanitized()

    assert status["available"] is False
    assert status["error_code"] == SESSION_EXPIRED
    assert status["reason"] == "AUTHORIZED_SESSION_EXPIRED"


def test_authorized_fake_session_is_available_without_exposing_secret() -> None:
    binding = AuthenticatedSessionBinding(FakeProvider(authorized_handle()))

    handle = binding.bind()
    status = binding.status().sanitized()

    assert handle.authorized is True
    assert status["available"] is True
    assert status["connected"] is True
    assert status["error_code"] is None
    assert_no_secret_markers(handle.sanitized())
    assert_no_secret_markers(status)


def test_binding_status_is_idempotent_for_same_provider_state() -> None:
    provider = FakeProvider(authorized_handle())
    binding = AuthenticatedSessionBinding(provider)

    first = binding.status().sanitized()
    second = binding.status().sanitized()

    assert first == second
    assert provider.calls == 2


def test_secret_marker_in_sanitized_handle_rejects_session() -> None:
    handle = authorized_handle(reason="token leaked")
    binding = AuthenticatedSessionBinding(FakeProvider(handle))

    status = binding.status().sanitized()

    assert status["available"] is False
    assert status["error_code"] == "INVALID_SESSION_HANDLE"


def test_unsupported_session_capabilities_are_blocked() -> None:
    handle = authorized_handle(capabilities=SessionCapabilities(read_only=True, message_stream=True, orders=True))
    binding = AuthenticatedSessionBinding(FakeProvider(handle))

    status = binding.status().sanitized()

    assert status["available"] is False
    assert status["error_code"] == UNSUPPORTED_SESSION


def test_binding_integrates_with_authorized_message_source_without_starting_transport() -> None:
    source = AuthorizedPolariumMessageSource(
        authorization_probe=StaticAuthorizationProbe(source_authorization()),
        session_binding=AuthenticatedSessionBinding(FakeProvider(authorized_handle())),
    )

    status = source.authorization_status()

    assert status.authorized is False
    assert status.status == "AUTHORIZED_SOURCE_UNAVAILABLE"
    assert "No connection will be opened" in status.reason
    assert source.is_connected() is False
    assert_no_secret_markers(status.__dict__)


def test_binding_reports_unavailable_to_message_source() -> None:
    source = AuthorizedPolariumMessageSource(
        authorization_probe=StaticAuthorizationProbe(source_authorization()),
        session_binding=AuthenticatedSessionBinding(UnavailableAuthorizedSessionProvider()),
    )

    status = source.authorization_status()

    assert status.authorized is False
    assert status.status == SESSION_NOT_AVAILABLE
    assert status.reason == "AUTHORIZED_SESSION_UNAVAILABLE"
    assert_no_secret_markers(status.__dict__)


def test_binding_package_has_no_io_or_network_dependency() -> None:
    root = Path("app/connector/polarium/live_session/binding")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))

    forbidden = [
        "httpx",
        "requests",
        "aiohttp",
        "websockets",
        "socket",
        "open(",
        "Path(",
        "MarketPipeline",
        "CandleStore",
        "frontend",
    ]
    for marker in forbidden:
        assert marker not in source
