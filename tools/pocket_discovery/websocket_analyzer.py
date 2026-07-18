from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import parse_qs, urlsplit

from tools.pocket_discovery.har_loader import har_entries
from tools.pocket_discovery.models import Direction, SocketFrameSummary, WebSocketSummary
from tools.pocket_discovery.sanitizer import payload_keys, sanitize, sanitize_url
from tools.pocket_discovery.socketio_parser import parse_socketio_frame

MARKET_EVENTS = {"changeSymbol", "updateStream", "updateCharts", "updateHistoryNewFast", "updateAssets", "saveCharts"}
ACCOUNT_MARKERS = {"balance", "portfolio", "position", "order", "payment", "profile", "account"}
CHAT_MARKERS = {"chat", "message", "support"}
ANALYTICS_MARKERS = {"analytics", "metric", "log", "track"}


def analyze_websockets(har_path: str, har: dict) -> tuple[WebSocketSummary, ...]:
    sockets: list[WebSocketSummary] = []
    for entry in har_entries(har):
        messages = _websocket_messages(entry)
        url = str(entry.get("request", {}).get("url", ""))
        if not messages and not _looks_like_websocket(entry, url):
            continue
        sockets.append(_summarize_socket(har_path, entry, url, messages))
    return tuple(sockets)


def _summarize_socket(har_path: str, entry: dict, url: str, messages: list[dict]) -> WebSocketSummary:
    parsed_url = urlsplit(url)
    query = parse_qs(parsed_url.query)
    frames: list[SocketFrameSummary] = []
    sent = 0
    received = 0
    heartbeat = 0
    event_names: set[str] = set()
    pending_binary_event_name: str | None = None
    for message in messages:
        direction = _direction(message)
        if direction == "sent":
            sent += 1
        elif direction == "received":
            received += 1
        data = str(message.get("data", ""))
        parsed = parse_socketio_frame(data)
        event_name = parsed.event_name
        payload = parsed.payload
        payload_keys_value = parsed.payload_keys
        frame_kind = parsed.frame_kind
        if parsed.frame_kind == "ENCODED_JSON" and pending_binary_event_name:
            event_name = pending_binary_event_name
            payload_keys_value = payload_keys(payload)
            frame_kind = "SOCKET_IO_BINARY_ATTACHMENT"
            pending_binary_event_name = None
        elif parsed.frame_kind == "SOCKET_IO_BINARY_EVENT" and parsed.event_name:
            pending_binary_event_name = parsed.event_name
        if parsed.frame_kind in {"ENGINE_IO_PING", "ENGINE_IO_PONG"}:
            heartbeat += 1
        if event_name:
            event_names.add(event_name)
        frames.append(
            SocketFrameSummary(
                direction=direction,
                timestamp=str(message.get("time")) if message.get("time") is not None else None,
                frame_kind=frame_kind,
                event_name=event_name,
                payload_type=parsed.payload_type,
                payload_keys=payload_keys_value,
                sample_sanitized=sanitize(payload),
            )
        )
    event_names_tuple = tuple(sorted(event_names))
    return WebSocketSummary(
        har_path=har_path,
        url_sanitized=sanitize_url(url),
        host=parsed_url.netloc,
        path=parsed_url.path,
        query_keys=tuple(sorted(query.keys())),
        transport=_first_query_value(query, "transport"),
        socket_io_version=_first_query_value(query, "EIO"),
        opened_at=str(entry.get("startedDateTime")) if entry.get("startedDateTime") else None,
        closed_at=None,
        frames_sent=sent,
        frames_received=received,
        heartbeat_count=heartbeat,
        event_names=event_names_tuple,
        classification=_classify_socket(event_names_tuple, parsed_url.netloc, parsed_url.path),
        frames=tuple(frames),
    )


def _websocket_messages(entry: dict) -> list[dict]:
    messages = entry.get("_webSocketMessages") or entry.get("_websocketMessages") or entry.get("webSocketMessages")
    return messages if isinstance(messages, list) else []


def _looks_like_websocket(entry: dict, url: str) -> bool:
    response = entry.get("response", {})
    status = response.get("status")
    return url.startswith(("ws://", "wss://")) or status == 101


def _direction(message: dict) -> Direction:
    raw_type = str(message.get("type") or message.get("direction") or "").lower()
    if raw_type in {"send", "sent", "out", "outgoing"}:
        return "sent"
    if raw_type in {"receive", "received", "in", "incoming"}:
        return "received"
    return "unknown"


def _first_query_value(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key)
    return values[0] if values else None


def _classify_socket(event_names: Iterable[str], host: str, path: str) -> str:
    haystack = " ".join([host, path, *event_names]).lower()
    event_set = set(event_names)
    if event_set & MARKET_EVENTS:
        return "MARKET_SOCKET"
    if any(marker in haystack for marker in ACCOUNT_MARKERS):
        return "ACCOUNT_SOCKET"
    if any(marker in haystack for marker in CHAT_MARKERS):
        return "CHAT_SOCKET"
    if any(marker in haystack for marker in ANALYTICS_MARKERS):
        return "ANALYTICS_SOCKET"
    return "UNKNOWN_SOCKET"
