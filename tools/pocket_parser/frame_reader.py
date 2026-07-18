from __future__ import annotations

from urllib.parse import urlsplit

from tools.pocket_discovery.har_loader import har_entries, load_har
from tools.pocket_discovery.socketio_parser import parse_socketio_frame
from tools.pocket_parser.models import PocketSocketEvent


def read_har_events(har_path: str, *, session_index: int) -> tuple[PocketSocketEvent, ...]:
    result = load_har(har_path)
    if result.har is None:
        return ()
    events: list[PocketSocketEvent] = []
    pending_binary_event_name: str | None = None
    pending_binary_direction = "unknown"
    frame_index = 0
    for entry in har_entries(result.har):
        url = str(entry.get("request", {}).get("url", ""))
        parsed_url = urlsplit(url)
        messages = entry.get("_webSocketMessages") or entry.get("_websocketMessages") or entry.get("webSocketMessages") or []
        if not isinstance(messages, list):
            continue
        for message in messages:
            raw_data = str(message.get("data", ""))
            parsed = parse_socketio_frame(raw_data)
            direction = _direction(message)
            event_name = parsed.event_name
            payload = parsed.payload
            frame_kind = parsed.frame_kind
            if parsed.frame_kind == "SOCKET_IO_BINARY_EVENT" and parsed.event_name:
                pending_binary_event_name = parsed.event_name
                pending_binary_direction = direction
            elif parsed.frame_kind == "ENCODED_JSON" and pending_binary_event_name:
                event_name = pending_binary_event_name
                direction = pending_binary_direction
                frame_kind = "SOCKET_IO_BINARY_ATTACHMENT"
                pending_binary_event_name = None
                pending_binary_direction = "unknown"
            events.append(
                PocketSocketEvent(
                    event_name=event_name,
                    direction=direction,
                    timestamp=_timestamp(message),
                    payload=payload,
                    source_har=har_path,
                    socket_host=parsed_url.netloc,
                    socket_path=parsed_url.path,
                    frame_index=frame_index,
                    session_index=session_index,
                    frame_kind=frame_kind,
                    parse_error=parsed.parse_error,
                )
            )
            frame_index += 1
    return tuple(events)


def _direction(message: dict) -> str:
    raw = str(message.get("type") or message.get("direction") or "").lower()
    if raw in {"send", "sent", "out", "outgoing"}:
        return "sent"
    if raw in {"receive", "received", "in", "incoming"}:
        return "received"
    return "unknown"


def _timestamp(message: dict) -> float | None:
    value = message.get("time")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

