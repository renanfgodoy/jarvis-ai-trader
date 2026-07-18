from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import struct
from urllib.parse import urlsplit


class CDPWireConnection:
    def __init__(self, raw: socket.socket) -> None:
        self._raw = raw

    def write_json(self, payload: dict) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self._write_frame(0x1, encoded)

    def read_json(self) -> dict | None:
        while True:
            opcode, payload = self._read_frame()
            if opcode == 0x8:
                return None
            if opcode == 0x9:
                self._write_frame(0xA, payload)
                continue
            if opcode == 0x1:
                decoded = json.loads(payload.decode("utf-8"))
                return decoded if isinstance(decoded, dict) else None

    def close(self) -> None:
        try:
            self._write_frame(0x8, b"")
        finally:
            self._raw.close()

    def _write_frame(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        first = 0x80 | opcode
        length = len(payload)
        if length < 126:
            header = bytes((first, 0x80 | length))
        elif length < 65536:
            header = bytes((first, 0x80 | 126)) + struct.pack("!H", length)
        else:
            header = bytes((first, 0x80 | 127)) + struct.pack("!Q", length)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self._raw.sendall(header + mask + masked)

    def _read_frame(self) -> tuple[int, bytes]:
        first, second = self._read_exact(2)
        opcode = first & 0x0F
        masked = bool(second & 0x80)
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._read_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._read_exact(8))[0]
        mask = self._read_exact(4) if masked else b""
        payload = self._read_exact(length) if length else b""
        if masked:
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        return opcode, payload

    def _read_exact(self, size: int) -> bytes:
        chunks = bytearray()
        while len(chunks) < size:
            chunk = self._raw.recv(size - len(chunks))
            if not chunk:
                raise ConnectionError("CDP wire connection closed.")
            chunks.extend(chunk)
        return bytes(chunks)


def connect_cdp_wire(url: str, *, timeout: float = 2.0) -> CDPWireConnection:
    parsed = urlsplit(url)
    if parsed.scheme != "ws":
        raise ValueError("Only local non-TLS CDP URLs are supported.")
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"
    raw = socket.create_connection((host, port), timeout=timeout)
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    ).encode("ascii")
    raw.sendall(request)
    response = _read_http_headers(raw)
    expected = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()).decode("ascii")
    if b" 101 " not in response or expected.encode("ascii") not in response:
        raw.close()
        raise ConnectionError("CDP wire handshake failed.")
    raw.settimeout(None)
    return CDPWireConnection(raw)


def _read_http_headers(raw: socket.socket) -> bytes:
    data = bytearray()
    while b"\r\n\r\n" not in data:
        chunk = raw.recv(4096)
        if not chunk:
            raise ConnectionError("CDP wire handshake closed.")
        data.extend(chunk)
    return bytes(data)
