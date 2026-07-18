from __future__ import annotations

import json
from itertools import count
from typing import Protocol
from urllib.request import urlopen

from app.market.providers.pocket.cdp_models import PocketCDPEvent, PocketCDPTarget
from app.market.providers.pocket.errors import PocketRuntimeError

POCKET_CDP_CLIENT_UNAVAILABLE = "POCKET_CDP_CLIENT_UNAVAILABLE"
POCKET_CDP_TARGET_NOT_ATTACHED = "POCKET_CDP_TARGET_NOT_ATTACHED"
POCKET_CDP_TARGET_NOT_FOUND = "POCKET_CDP_TARGET_NOT_FOUND"


class PocketCDPClient(Protocol):
    def list_targets(self) -> tuple[PocketCDPTarget, ...]: ...

    def attach_target(self, target_id: str) -> None: ...

    def enable_network(self) -> None: ...

    def next_event(self) -> PocketCDPEvent | None: ...

    def close(self) -> None: ...


class DisabledPocketCDPClient:
    """Non-network placeholder used unless real validation is explicitly run."""

    def list_targets(self) -> tuple[PocketCDPTarget, ...]:
        return ()

    def attach_target(self, target_id: str) -> None:
        return None

    def enable_network(self) -> None:
        return None

    def next_event(self) -> PocketCDPEvent | None:
        return None

    def close(self) -> None:
        return None


class PocketLocalCDPClient:
    """Minimal local CDP client for passive Network observation."""

    def __init__(self, *, host: str = "127.0.0.1", port: int = 9230, http_timeout: float = 2.0) -> None:
        self.host = host
        self.port = port
        self.http_timeout = http_timeout
        self._targets: tuple[PocketCDPTarget, ...] = ()
        self._connection = None
        self._ids = count(1)

    def list_targets(self) -> tuple[PocketCDPTarget, ...]:
        with urlopen(f"http://{self.host}:{self.port}/json/list", timeout=self.http_timeout) as response:
            rows = json.loads(response.read().decode("utf-8"))
        targets: list[PocketCDPTarget] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            targets.append(
                PocketCDPTarget(
                    target_id=str(row.get("id") or ""),
                    type=str(row.get("type") or ""),
                    url=str(row.get("url") or ""),
                    title=str(row.get("title") or ""),
                    attached=bool(row.get("attached") or False),
                    websocket_debugger_url=str(row.get("webSocketDebuggerUrl") or "") or None,
                )
            )
        self._targets = tuple(target for target in targets if target.target_id)
        return self._targets

    def attach_target(self, target_id: str) -> None:
        target = next((candidate for candidate in self._targets if candidate.target_id == target_id), None)
        if target is None:
            target = next((candidate for candidate in self.list_targets() if candidate.target_id == target_id), None)
        if target is None:
            raise PocketRuntimeError(POCKET_CDP_TARGET_NOT_FOUND, "Pocket CDP target was not found.")
        if not target.websocket_debugger_url:
            raise PocketRuntimeError(POCKET_CDP_CLIENT_UNAVAILABLE, "Pocket CDP target has no debugger URL.")
        from tools.pocket_live_observation.cdp_wire import connect_cdp_wire

        self._connection = connect_cdp_wire(target.websocket_debugger_url, timeout=self.http_timeout)

    def enable_network(self) -> None:
        self._write_command("Network.enable")

    def next_event(self) -> PocketCDPEvent | None:
        if self._connection is None:
            raise PocketRuntimeError(POCKET_CDP_TARGET_NOT_ATTACHED, "Pocket CDP target is not attached.")
        while True:
            try:
                message = self._connection.read_json()
            except ConnectionError:
                return None
            if not message:
                return None
            method = message.get("method")
            if not method:
                continue
            params = message.get("params")
            return PocketCDPEvent(str(method), params if isinstance(params, dict) else {})

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _write_command(self, method: str) -> None:
        if self._connection is None:
            raise PocketRuntimeError(POCKET_CDP_TARGET_NOT_ATTACHED, "Pocket CDP target is not attached.")
        payload = {"id": next(self._ids), "method": method}
        self._connection.write_json(payload)
