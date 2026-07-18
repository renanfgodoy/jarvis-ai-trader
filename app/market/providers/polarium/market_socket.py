from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MARKET_WS_HOST_FRAGMENT = "ws.trade.polariumbroker.com"
MARKET_SIGNALS = {"first-candles", "candles", "candle-generated", "candles-generated", "get-first-candles"}


@dataclass
class PolariumMarketSocketState:
    request_id: str
    host: str
    active: bool = True
    authenticated: bool = False
    time_sync: bool = False
    market_messages: int = 0

    @property
    def ready(self) -> bool:
        return self.active and self.authenticated and self.time_sync and self.market_messages > 0

    def sanitized(self) -> dict:
        return {
            "host": self.host,
            "active": self.active,
            "authenticated": self.authenticated,
            "time_sync": self.time_sync,
            "market_messages": self.market_messages,
            "ready": self.ready,
        }


class PolariumMarketSocketDiscovery:
    def __init__(self) -> None:
        self._sockets: dict[str, PolariumMarketSocketState] = {}
        self._market_request_id: str | None = None
        self.reconnects = 0

    def register_socket(self, *, request_id: str, url: str) -> None:
        if MARKET_WS_HOST_FRAGMENT not in url:
            return
        if request_id in self._sockets and not self._sockets[request_id].active:
            self.reconnects += 1
        self._sockets[request_id] = PolariumMarketSocketState(request_id=request_id, host=_host(url))

    def close_socket(self, request_id: str) -> None:
        state = self._sockets.get(request_id)
        if state is not None:
            state.active = False

    def observe_frame(self, *, request_id: str, message: dict[str, Any]) -> None:
        state = self._sockets.get(request_id)
        if state is None:
            return
        name = _event_name(message)
        if name == "authenticated":
            state.authenticated = True
        if name == "timeSync":
            state.time_sync = True
        if name in MARKET_SIGNALS:
            state.market_messages += 1
            self._market_request_id = request_id

    @property
    def market_socket(self) -> PolariumMarketSocketState | None:
        if self._market_request_id is None:
            return None
        return self._sockets.get(self._market_request_id)

    @property
    def active_market_socket_count(self) -> int:
        return sum(1 for state in self._sockets.values() if state.active and state.market_messages > 0)

    def sanitized(self) -> dict:
        return {
            "active_market_socket_count": self.active_market_socket_count,
            "market_socket": self.market_socket.sanitized() if self.market_socket else None,
            "reconnects": self.reconnects,
        }


def _event_name(message: dict[str, Any]) -> str | None:
    name = message.get("name")
    if isinstance(name, str) and name != "sendMessage":
        return name
    msg = message.get("msg")
    if isinstance(msg, dict) and isinstance(msg.get("name"), str):
        return msg["name"]
    return name if isinstance(name, str) else None


def _host(url: str) -> str:
    return url.split("/", 3)[2] if "://" in url and len(url.split("/", 3)) > 2 else "UNKNOWN"
