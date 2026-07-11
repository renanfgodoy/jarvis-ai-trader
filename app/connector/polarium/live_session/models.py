from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Mapping

LiveSessionState = Literal["STOPPED", "STARTING", "CONNECTED", "RECONNECTING", "ERROR", "STOPPING"]


@dataclass(frozen=True)
class AuthorizedSessionSnapshot:
    authorized: bool
    status: str
    reason: str


@dataclass(frozen=True)
class LiveSessionMessage:
    event_name: str | None
    received_at: datetime
    message_sequence: int
    connection_state: LiveSessionState
    payload: Mapping[str, Any]

    def sanitized_metadata(self) -> dict[str, Any]:
        return {
            "event_name": self.event_name,
            "received_at": self.received_at.isoformat(),
            "message_sequence": self.message_sequence,
            "connection_state": self.connection_state,
        }


@dataclass(frozen=True)
class LiveSessionStatus:
    state: LiveSessionState
    authorized: bool
    connected: bool
    started_at: datetime | None
    last_message_at: datetime | None
    last_event_name: str | None
    message_count: int
    reconnect_count: int
    last_error_code: str | None

    def sanitized(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "authorized": self.authorized,
            "connected": self.connected,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "last_event_name": self.last_event_name,
            "message_count": self.message_count,
            "reconnect_count": self.reconnect_count,
            "last_error_code": self.last_error_code,
        }
