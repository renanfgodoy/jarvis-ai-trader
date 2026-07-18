from __future__ import annotations

from app.market.providers.pocket.errors import POCKET_READ_ONLY_GUARD_BLOCKED, PocketRuntimeError

ALLOWED_ACTIONS = {
    "PROCESS_ASSET_CATALOG",
    "PROCESS_HISTORY",
    "PROCESS_REALTIME",
    "PROCESS_CHART_METADATA",
    "UPDATE_SESSION_STATE",
}

BLOCKED_ACTIONS = {
    "AUTHENTICATE_REAL_SESSION",
    "OPEN_SOCKET_DIRECTLY",
    "SEND_CHANGE_SYMBOL",
    "SEND_MESSAGE",
    "SEND_ORDER",
    "SEND_CALL",
    "SEND_PUT",
    "READ_BALANCE",
    "READ_PERSONAL_DATA",
    "MODIFY_CDP_FRAME",
    "INTERCEPT_REQUEST",
    "REPLAY_LIVE_CREDENTIAL",
}


class PocketRuntimeGuard:
    def __init__(self) -> None:
        self.blocked_count = 0

    def ensure_allowed(self, action: str) -> None:
        if action in ALLOWED_ACTIONS:
            return
        self.blocked_count += 1
        raise PocketRuntimeError(POCKET_READ_ONLY_GUARD_BLOCKED, f"Action is blocked in read-only Pocket runtime: {action}")
