from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from app.market.providers.polarium.runtime_guard import PolariumRuntimeGuard

BootstrapActionKind = Literal["none", "send", "retry", "failed"]


@dataclass(frozen=True)
class BootstrapRequest:
    active_id: int
    raw_size: int
    request_id: str
    payload: dict[str, Any]
    created_at: int
    attempt: int


@dataclass(frozen=True)
class BootstrapAction:
    kind: BootstrapActionKind
    request: BootstrapRequest | None = None
    reason: str | None = None


class BootstrapRequestFactory:
    """Builds the proven read-only get-first-candles envelope."""

    def __init__(self, guard: PolariumRuntimeGuard | None = None) -> None:
        self._guard = guard or PolariumRuntimeGuard()

    def create(self, *, active_id: int, raw_size: int, now_ms: int, attempt: int) -> BootstrapRequest:
        request_id = f"friday_get_first_candles_{active_id}_{raw_size}_{now_ms}_{attempt}"
        payload = {
            "name": "sendMessage",
            "request_id": request_id,
            "msg": {
                "name": "get-first-candles",
                "body": {"active_id": active_id, "size": raw_size},
            },
        }
        self._guard.validate_outbound(payload)
        return BootstrapRequest(
            active_id=active_id,
            raw_size=raw_size,
            request_id=request_id,
            payload=payload,
            created_at=now_ms,
            attempt=attempt,
        )


class HistoricalBootstrapManager:
    """Controls active historical bootstrap requests for the visible context."""

    def __init__(
        self,
        *,
        factory: BootstrapRequestFactory | None = None,
        timeout_ms: int = 10_000,
        max_retries: int = 1,
    ) -> None:
        self._factory = factory or BootstrapRequestFactory()
        self._timeout_ms = timeout_ms
        self._max_retries = max_retries
        self._context: tuple[int, int] | None = None
        self._pending: BootstrapRequest | None = None
        self._completed: tuple[int, int] | None = None
        self._attempts = 0
        self._state = "NO_HISTORY"
        self._last_error: str | None = None

    def on_visible_context(self, *, active_id: int | None, raw_size: int | None, now_ms: int, socket_ready: bool) -> BootstrapAction:
        if active_id is None or raw_size is None:
            return BootstrapAction(kind="none", reason="VISIBLE_CONTEXT_INCOMPLETE")
        context = (active_id, raw_size)
        if context != self._context:
            self._context = context
            self._pending = None
            self._completed = None
            self._attempts = 0
            self._state = "BOOTSTRAPPING"
            self._last_error = None
        if self._completed == context:
            return BootstrapAction(kind="none", reason="BOOTSTRAP_ALREADY_COMPLETED")
        if self._pending is not None:
            return BootstrapAction(kind="none", reason="BOOTSTRAP_ALREADY_PENDING")
        if not socket_ready:
            self._state = "WAITING_FOR_MARKET_SOCKET"
            return BootstrapAction(kind="none", reason="MARKET_SOCKET_NOT_READY")
        return self._new_request(active_id=active_id, raw_size=raw_size, now_ms=now_ms, kind="send")

    def on_external_request(self, *, active_id: int | None, raw_size: int | None, request_id: str | None, now_ms: int) -> None:
        if active_id is None or raw_size is None or request_id is None:
            return
        context = (active_id, raw_size)
        if context != self._context:
            self._context = context
            self._completed = None
            self._attempts = 0
        self._pending = BootstrapRequest(
            active_id=active_id,
            raw_size=raw_size,
            request_id=request_id,
            payload={},
            created_at=now_ms,
            attempt=max(1, self._attempts),
        )
        self._state = "BOOTSTRAPPING"

    def on_response(self, *, request_id: str | None, active_id: int | None, raw_size: int | None) -> None:
        if self._pending is None:
            return
        request_matches = request_id is not None and request_id == self._pending.request_id
        context_matches = active_id == self._pending.active_id and (raw_size is None or raw_size == self._pending.raw_size)
        if request_matches or context_matches:
            self._completed = (self._pending.active_id, self._pending.raw_size)
            self._pending = None
            self._state = "READY"
            self._last_error = None

    def tick(self, *, now_ms: int, socket_ready: bool) -> BootstrapAction:
        if self._pending is None:
            return BootstrapAction(kind="none")
        if now_ms - self._pending.created_at < self._timeout_ms:
            return BootstrapAction(kind="none")
        if self._attempts <= self._max_retries and socket_ready:
            self._last_error = "BOOTSTRAP_TIMEOUT"
            return self._new_request(active_id=self._pending.active_id, raw_size=self._pending.raw_size, now_ms=now_ms, kind="retry")
        self._pending = None
        self._state = "NO_HISTORY"
        self._last_error = "BOOTSTRAP_FAILED"
        return BootstrapAction(kind="failed", reason="BOOTSTRAP_FAILED")

    def sanitized(self) -> dict[str, Any]:
        return {
            "state": self._state,
            "active_id": self._context[0] if self._context else None,
            "raw_size": self._context[1] if self._context else None,
            "pending": self._pending is not None,
            "request_id_present": bool(self._pending and self._pending.request_id),
            "attempts": self._attempts,
            "last_error": self._last_error,
        }

    def _new_request(self, *, active_id: int, raw_size: int, now_ms: int, kind: Literal["send", "retry"]) -> BootstrapAction:
        self._attempts += 1
        request = self._factory.create(active_id=active_id, raw_size=raw_size, now_ms=now_ms, attempt=self._attempts)
        self._pending = request
        self._state = "BOOTSTRAPPING"
        return BootstrapAction(kind=kind, request=request)
