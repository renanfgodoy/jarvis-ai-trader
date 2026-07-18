from __future__ import annotations

import base64
import json
from typing import Any

from tools.pocket_discovery.models import ParsedSocketIOFrame
from tools.pocket_discovery.sanitizer import payload_keys


def parse_socketio_frame(raw_data: str) -> ParsedSocketIOFrame:
    data = raw_data.strip()
    decoded = _decode_base64_json(data)
    if decoded is not None:
        return _frame("base64", "ENCODED_JSON", None, decoded)
    if data == "2":
        return _frame("2", "ENGINE_IO_PING", None, None)
    if data == "3":
        return _frame("3", "ENGINE_IO_PONG", None, None)
    if data == "40":
        return _frame("40", "SOCKET_IO_CONNECT", None, None)
    if data == "41":
        return _frame("41", "SOCKET_IO_DISCONNECT", None, None)
    if data.startswith("0"):
        return _parse_json_tail(data, "0", "ENGINE_IO_OPEN")
    if data.startswith("42"):
        return _parse_event(data)
    if data.startswith("451-"):
        return _parse_event(data, raw_type="451-", kind="SOCKET_IO_BINARY_EVENT")
    if data.startswith("45"):
        return _parse_event(data, raw_type=data[:3], kind="SOCKET_IO_BINARY_EVENT")
    if data.startswith("4"):
        return _frame(data[:2], "ENGINE_IO_MESSAGE", None, None)
    return _frame(data[:1] or "unknown", "UNKNOWN_FRAME", None, None)


def _parse_event(data: str, raw_type: str = "42", kind: str = "SOCKET_IO_EVENT") -> ParsedSocketIOFrame:
    start = data.find("[")
    if start < 0:
        return _frame(raw_type, kind, None, None, parse_error="EVENT_ARRAY_NOT_FOUND")
    metadata = data[len(raw_type) : start]
    namespace, ack_id = _parse_event_metadata(metadata)
    try:
        parsed = json.loads(data[start:])
    except json.JSONDecodeError as error:
        return _frame(raw_type, kind, None, None, parse_error=f"JSON_DECODE_ERROR:{error.msg}", namespace=namespace, ack_id=ack_id)
    if not isinstance(parsed, list) or not parsed:
        return _frame(raw_type, kind, None, parsed, parse_error="INVALID_EVENT_ARRAY", namespace=namespace, ack_id=ack_id)
    event_name = parsed[0] if isinstance(parsed[0], str) else None
    payload: Any = parsed[1] if len(parsed) > 1 else None
    return _frame(raw_type, kind, event_name, payload, namespace=namespace, ack_id=ack_id, args=tuple(parsed[1:]))


def _parse_json_tail(data: str, raw_type: str, kind: str) -> ParsedSocketIOFrame:
    payload: Any = None
    parse_error = None
    if len(data) > 1:
        try:
            payload = json.loads(data[1:])
        except json.JSONDecodeError as error:
            parse_error = f"JSON_DECODE_ERROR:{error.msg}"
    return _frame(raw_type, kind, None, payload, parse_error=parse_error)


def _frame(
    raw_type: str,
    kind: str,
    event_name: str | None,
    payload: Any,
    parse_error: str | None = None,
    namespace: str | None = None,
    ack_id: str | None = None,
    args: tuple[Any, ...] = (),
) -> ParsedSocketIOFrame:
    return ParsedSocketIOFrame(
        raw_type=raw_type,
        frame_kind=kind,
        event_name=event_name,
        payload=payload,
        payload_type=type(payload).__name__ if payload is not None else None,
        payload_keys=payload_keys(payload),
        parse_error=parse_error,
        namespace=namespace,
        ack_id=ack_id,
        args=args,
    )


def _parse_event_metadata(metadata: str) -> tuple[str | None, str | None]:
    namespace = None
    ack_id = None
    cursor = metadata
    if cursor.startswith("/"):
        comma = cursor.find(",")
        if comma >= 0:
            namespace = cursor[:comma]
            cursor = cursor[comma + 1 :]
        else:
            namespace = cursor
            cursor = ""
    digits = "".join(char for char in cursor if char.isdigit())
    if digits:
        ack_id = digits
    return namespace, ack_id


def _decode_base64_json(data: str) -> Any | None:
    if not data or data[0] in "0123456789[{":
        return None
    try:
        decoded = base64.b64decode(data, validate=True)
    except Exception:
        return None
    try:
        text = decoded.decode("utf-8")
    except UnicodeDecodeError:
        return None
    stripped = text.strip()
    if not stripped.startswith(("[", "{")):
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None
