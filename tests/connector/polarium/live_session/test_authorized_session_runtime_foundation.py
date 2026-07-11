import json
from pathlib import Path
from typing import Any, Callable

from fastapi.testclient import TestClient

from app.connector.polarium.live_session.event_bus import PolariumLiveSessionEventBus
from app.connector.polarium.live_session.manager import PolariumLiveSessionManager
from app.connector.polarium.live_session.models import AuthorizedSessionSnapshot, LiveSessionMessage
from app.main import app

client = TestClient(app)


class FakeAuthorizedMessageSource:
    def __init__(self, *, fail_start: bool = False) -> None:
        self.fail_start = fail_start
        self.start_calls = 0
        self.stop_calls = 0
        self.callback: Callable[[dict[str, Any]], None] | None = None

    def authorization_status(self) -> AuthorizedSessionSnapshot:
        return AuthorizedSessionSnapshot(authorized=True, status="AUTHORIZED", reason="Fake test source.")

    def start(self, on_message: Callable[[dict[str, Any]], None]) -> None:
        self.start_calls += 1
        if self.fail_start:
            raise RuntimeError("start failed")
        self.callback = on_message

    def stop(self) -> None:
        self.stop_calls += 1


def assert_no_secret_markers(payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False).lower()
    for marker in ["token", "cookie", "bearer", "ssid", "password", "client_secret", "code_verifier", "headers"]:
        assert marker not in text


def test_initial_state_is_stopped() -> None:
    manager = PolariumLiveSessionManager()

    status = manager.status().sanitized()

    assert status["state"] == "STOPPED"
    assert status["connected"] is False
    assert status["message_count"] == 0


def test_start_without_safe_authorization_is_blocked() -> None:
    manager = PolariumLiveSessionManager()

    status = manager.start().sanitized()

    assert status["state"] == "ERROR"
    assert status["connected"] is False
    assert status["authorized"] is False
    assert status["last_error_code"] == "NO_AUTHORIZED_SESSION"
    assert_no_secret_markers(status)


def test_start_is_idempotent_and_uses_one_connection() -> None:
    source = FakeAuthorizedMessageSource()
    manager = PolariumLiveSessionManager(message_source=source)

    first = manager.start()
    second = manager.start()

    assert first.state == "CONNECTED"
    assert second.state == "CONNECTED"
    assert source.start_calls == 1


def test_stop_is_idempotent_and_cleans_connection_state() -> None:
    source = FakeAuthorizedMessageSource()
    manager = PolariumLiveSessionManager(message_source=source)
    manager.start()

    first = manager.stop()
    second = manager.stop()

    assert first.state == "STOPPED"
    assert second.state == "STOPPED"
    assert first.connected is False
    assert source.stop_calls == 1


def test_status_is_sanitized_after_successful_start() -> None:
    manager = PolariumLiveSessionManager(message_source=FakeAuthorizedMessageSource())

    status = manager.start().sanitized()

    assert status["state"] == "CONNECTED"
    assert status["authorized"] is True
    assert_no_secret_markers(status)


def test_event_bus_register_remove_and_publish_message() -> None:
    bus = PolariumLiveSessionEventBus()
    received: list[LiveSessionMessage] = []

    listener_id = bus.register(received.append)
    removed = bus.remove(listener_id)
    result_without_listener = bus.publish(_message())
    bus.register(received.append)
    result_with_listener = bus.publish(_message(event_name="first-candles"))

    assert removed is True
    assert result_without_listener.delivered == 0
    assert result_with_listener.delivered == 1
    assert received[0].event_name == "first-candles"


def test_listener_error_is_isolated() -> None:
    bus = PolariumLiveSessionEventBus()
    received: list[LiveSessionMessage] = []

    def broken_listener(message: LiveSessionMessage) -> None:
        raise RuntimeError("listener failed")

    bus.register(broken_listener)
    bus.register(received.append)

    result = bus.publish(_message())

    assert result.delivered == 1
    assert result.failed == 1
    assert bus.listener_error_count == 1
    assert len(received) == 1


def test_internal_publication_updates_status_and_listener() -> None:
    source = FakeAuthorizedMessageSource()
    bus = PolariumLiveSessionEventBus()
    received: list[LiveSessionMessage] = []
    bus.register(received.append)
    manager = PolariumLiveSessionManager(message_source=source, event_bus=bus)
    manager.start()

    status = manager.publish_decoded_message({"name": "candle-generated", "msg": {"body": {"active_id": 76}}})

    assert status.message_count == 1
    assert status.last_event_name == "candle-generated"
    assert received[0].sanitized_metadata()["event_name"] == "candle-generated"
    assert "payload" not in received[0].sanitized_metadata()


def test_sensitive_message_is_rejected_before_event_bus() -> None:
    bus = PolariumLiveSessionEventBus()
    received: list[LiveSessionMessage] = []
    bus.register(received.append)
    manager = PolariumLiveSessionManager(message_source=FakeAuthorizedMessageSource(), event_bus=bus)
    manager.start()

    status = manager.publish_decoded_message({"name": "candle-generated", "headers": {"Authorization": "Bearer value"}})

    assert status.last_error_code == "SENSITIVE_MESSAGE_REJECTED"
    assert status.message_count == 0
    assert received == []


def test_reconnect_is_limited_when_connection_start_fails() -> None:
    manager = PolariumLiveSessionManager(message_source=FakeAuthorizedMessageSource(fail_start=True), max_reconnect_attempts=0)

    status = manager.start()

    assert status.state == "ERROR"
    assert status.reconnect_count == 0
    assert status.last_error_code == "CONNECTION_START_FAILED"


def test_endpoint_status_is_sanitized() -> None:
    response = client.get("/api/v1/polarium/live-session/status")

    assert response.status_code == 200
    assert response.json()["state"] in {"STOPPED", "ERROR"}
    assert_no_secret_markers(response.json())


def test_endpoint_start_accepts_no_body_or_credentials() -> None:
    response = client.post("/api/v1/polarium/live-session/start", json={"token": "not-accepted"})

    assert response.status_code == 400
    assert "do not accept request bodies" in response.json()["detail"]


def test_endpoint_start_without_authorized_source_returns_structured_block() -> None:
    response = client.post("/api/v1/polarium/live-session/start")

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["state"] == "ERROR"
    assert detail["last_error_code"] == "NO_AUTHORIZED_SESSION"
    assert_no_secret_markers(detail)


def test_endpoint_stop_is_idempotent() -> None:
    first = client.post("/api/v1/polarium/live-session/stop")
    second = client.post("/api/v1/polarium/live-session/stop")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["state"] == "STOPPED"


def test_manager_has_no_order_execution_api() -> None:
    manager = PolariumLiveSessionManager()

    assert not hasattr(manager, "send_order")
    assert not hasattr(manager, "execute")
    assert not hasattr(manager, "buy")


def test_live_session_foundation_has_no_market_store_or_pipeline_dependency() -> None:
    root = Path("app/connector/polarium/live_session")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))

    assert "MarketPipeline" not in source
    assert "CandleStore" not in source


def _message(event_name: str = "candle-generated") -> LiveSessionMessage:
    return LiveSessionMessage(
        event_name=event_name,
        received_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        message_sequence=1,
        connection_state="CONNECTED",
        payload={"name": event_name},
    )
