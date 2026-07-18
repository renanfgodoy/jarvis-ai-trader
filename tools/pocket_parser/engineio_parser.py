from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.pocket_discovery.socketio_parser import parse_socketio_frame


@dataclass(frozen=True)
class EngineIOParseResult:
    kind: str
    event_name: str | None
    payload: Any
    payload_type: str | None
    payload_keys: tuple[str, ...]
    parse_error: str | None = None


def parse_engineio_frame(raw_data: str) -> EngineIOParseResult:
    parsed = parse_socketio_frame(raw_data)
    kind_map = {
        "ENGINE_IO_OPEN": "ENGINE_OPEN",
        "ENGINE_IO_PING": "PING",
        "ENGINE_IO_PONG": "PONG",
        "SOCKET_IO_CONNECT": "SOCKET_CONNECT",
        "SOCKET_IO_DISCONNECT": "SOCKET_DISCONNECT",
        "SOCKET_IO_EVENT": "SOCKET_EVENT",
        "SOCKET_IO_BINARY_EVENT": "SOCKET_EVENT",
        "ENCODED_JSON": "SOCKET_EVENT",
        "UNKNOWN_FRAME": "UNKNOWN_ENGINE_FRAME",
    }
    kind = kind_map.get(parsed.frame_kind, parsed.frame_kind)
    if parsed.parse_error:
        kind = "PARSE_ERROR"
    return EngineIOParseResult(
        kind=kind,
        event_name=parsed.event_name,
        payload=parsed.payload,
        payload_type=parsed.payload_type,
        payload_keys=parsed.payload_keys,
        parse_error=parsed.parse_error,
    )

