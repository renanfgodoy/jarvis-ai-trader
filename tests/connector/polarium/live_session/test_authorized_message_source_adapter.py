import json
from pathlib import Path
from typing import Any, Callable

from app.connector.polarium.live_session.event_bus import PolariumLiveSessionEventBus
from app.connector.polarium.live_session.manager import PolariumLiveSessionManager
from app.connector.polarium.live_session.models import LiveSessionMessage
from app.connector.polarium.live_session.sources.authorized_source import AuthorizedPolariumMessageSource, StaticAuthorizationProbe
from app.connector.polarium.live_session.sources.errors import AuthorizedSourceUnavailableError
from app.connector.polarium.live_session.sources.models import MessageSourceAuthorization


def assert_no_secret_markers(payload: dict | str) -> None:
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    lowered = text.lower()
    for marker in ["access_token", "refresh_token", "cookie", "bearer", "ssid", "password", "client_secret", "code_verifier", "headers"]:
        assert marker not in lowered


def authorization(*, authorized: bool = False, state: str = "NO_AUTHORIZED_SESSION") -> MessageSourceAuthorization:
    return MessageSourceAuthorization(
        authorized=authorized,
        state=state,  # type: ignore[arg-type]
        reason="Sanitized test authorization state.",
    )


class FakeConnectedSource:
    def __init__(self) -> None:
        self.start_calls = 0
        self.stop_calls = 0
        self.connected = False
        self.on_message: Callable[[dict[str, Any]], None] | None = None

    def authorization_status(self):
        return __import__("app.connector.polarium.live_session.models", fromlist=["AuthorizedSessionSnapshot"]).AuthorizedSessionSnapshot(
            authorized=True,
            status="AUTHORIZED",
            reason="Fake authorized source.",
        )

    def start(self, on_message: Callable[[dict[str, Any]], None]) -> None:
        self.start_calls += 1
        self.connected = True
        self.on_message = on_message

    def stop(self) -> None:
        self.stop_calls += 1
        self.connected = False

    def emit(self, message: dict[str, Any]) -> None:
        assert self.on_message is not None
        self.on_message(message)


def test_unauthorized_source_reports_sanitized_block() -> None:
    source = AuthorizedPolariumMessageSource(StaticAuthorizationProbe(authorization()))

    status = source.authorization_status()

    assert status.authorized is False
    assert status.status == "NO_AUTHORIZED_SESSION"
    assert_no_secret_markers(status.__dict__)


def test_authorized_but_unproven_source_reports_structured_unavailable() -> None:
    source = AuthorizedPolariumMessageSource(StaticAuthorizationProbe(authorization(authorized=True, state="AUTHORIZED")))

    status = source.authorization_status()

    assert status.authorized is False
    assert status.status == "AUTHORIZED_SOURCE_UNAVAILABLE"
    assert_no_secret_markers(status.__dict__)


def test_authorized_source_does_not_open_unproven_websocket() -> None:
    source = AuthorizedPolariumMessageSource(StaticAuthorizationProbe(authorization(authorized=True, state="AUTHORIZED")))

    try:
        source.start(lambda message: None)
    except AuthorizedSourceUnavailableError as exc:
        assert str(exc) == "AUTHORIZED_SOURCE_UNAVAILABLE"
        assert_no_secret_markers(str(exc))
    else:  # pragma: no cover
        raise AssertionError("Expected the adapter to block unproven WebSocket start.")

    assert source.is_connected() is False


def test_manager_start_uses_injected_authorized_fake_source() -> None:
    source = FakeConnectedSource()
    manager = PolariumLiveSessionManager(message_source=source)

    status = manager.start()

    assert status.state == "CONNECTED"
    assert source.start_calls == 1


def test_manager_enforces_single_connection_with_injected_source() -> None:
    source = FakeConnectedSource()
    manager = PolariumLiveSessionManager(message_source=source)

    manager.start()
    manager.start()

    assert source.start_calls == 1


def test_manager_stop_cleans_injected_source() -> None:
    source = FakeConnectedSource()
    manager = PolariumLiveSessionManager(message_source=source)
    manager.start()

    status = manager.stop()

    assert status.state == "STOPPED"
    assert source.stop_calls == 1
    assert source.connected is False


def test_injected_source_message_is_published_to_event_bus() -> None:
    source = FakeConnectedSource()
    bus = PolariumLiveSessionEventBus()
    received: list[LiveSessionMessage] = []
    bus.register(received.append)
    manager = PolariumLiveSessionManager(message_source=source, event_bus=bus)
    manager.start()

    source.emit({"name": "candle-generated", "msg": {"body": {"active_id": 76}}})

    assert len(received) == 1
    assert received[0].event_name == "candle-generated"
    assert "payload" not in received[0].sanitized_metadata()


def test_connection_error_is_sanitized_by_manager() -> None:
    source = AuthorizedPolariumMessageSource(StaticAuthorizationProbe(authorization(authorized=True, state="AUTHORIZED")))
    manager = PolariumLiveSessionManager(message_source=source)

    status = manager.start().sanitized()

    assert status["state"] == "ERROR"
    assert status["last_error_code"] == "AUTHORIZED_SOURCE_UNAVAILABLE"
    assert_no_secret_markers(status)


def test_listener_does_not_receive_authentication_data() -> None:
    source = FakeConnectedSource()
    bus = PolariumLiveSessionEventBus()
    received: list[LiveSessionMessage] = []
    bus.register(received.append)
    manager = PolariumLiveSessionManager(message_source=source, event_bus=bus)
    manager.start()

    source.emit({"name": "timeSync", "msg": {"server_time": 123}})

    serialized = json.dumps(received[0].sanitized_metadata(), ensure_ascii=False)
    assert "payload" not in serialized
    assert_no_secret_markers(serialized)


def test_logout_or_invalidation_blocks_new_start() -> None:
    source = AuthorizedPolariumMessageSource(StaticAuthorizationProbe(authorization()))
    manager = PolariumLiveSessionManager(message_source=source)

    status = manager.start()

    assert status.state == "ERROR"
    assert status.last_error_code == "NO_AUTHORIZED_SESSION"


def test_source_has_no_market_store_or_pipeline_dependency() -> None:
    root = Path("app/connector/polarium/live_session/sources")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))

    assert "MarketPipeline" not in source
    assert "CandleStore" not in source


def test_source_has_no_order_execution_api() -> None:
    source = AuthorizedPolariumMessageSource(StaticAuthorizationProbe(authorization(authorized=True, state="AUTHORIZED")))

    assert not hasattr(source, "send_order")
    assert not hasattr(source, "execute")
    assert not hasattr(source, "buy")


def test_no_auth_payload_is_logged_or_serialized_by_source() -> None:
    source = AuthorizedPolariumMessageSource(StaticAuthorizationProbe(authorization(authorized=True, state="AUTHORIZED")))

    serialized = json.dumps(source.authorization_status().__dict__, ensure_ascii=False)

    assert "payload" not in serialized.lower()
    assert_no_secret_markers(serialized)
