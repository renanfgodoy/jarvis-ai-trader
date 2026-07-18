from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TargetPlanAction = Literal["open_friday", "reuse_friday", "wait", "skip"]


@dataclass(frozen=True)
class CDPTarget:
    target_id: str
    url: str
    kind: str = "page"


@dataclass(frozen=True)
class CDPTargetPlan:
    action: TargetPlanAction
    reason: str
    friday_url: str
    polarium_target_id: str | None = None
    friday_target_id: str | None = None


class DualTabCDPSessionManager:
    """Decides when to open/reuse the Friday tab without touching Polarium."""

    def __init__(
        self,
        *,
        friday_frontend_url: str,
        polarium_host_fragment: str = "trade.polariumbroker.com",
        min_attempt_interval_ms: int = 5_000,
    ) -> None:
        self._friday_frontend_url = _normalize_url(friday_frontend_url)
        self._polarium_host_fragment = polarium_host_fragment
        self._min_attempt_interval_ms = min_attempt_interval_ms
        self._last_attempt_at: int | None = None
        self._opened_or_reused = False

    @property
    def friday_frontend_url(self) -> str:
        return self._friday_frontend_url

    def plan(
        self,
        *,
        targets: tuple[CDPTarget, ...],
        market_ready: bool,
        frontend_available: bool,
        now_ms: int,
    ) -> CDPTargetPlan:
        polarium = self._find_polarium_target(targets)
        friday = self._find_friday_target(targets)
        if friday is not None:
            self._opened_or_reused = True
            return CDPTargetPlan(
                action="reuse_friday",
                reason="FRIDAY_TAB_ALREADY_EXISTS",
                friday_url=self._friday_frontend_url,
                polarium_target_id=polarium.target_id if polarium else None,
                friday_target_id=friday.target_id,
            )
        if self._opened_or_reused:
            return CDPTargetPlan(action="skip", reason="FRIDAY_TAB_ALREADY_HANDLED", friday_url=self._friday_frontend_url, polarium_target_id=polarium.target_id if polarium else None)
        if polarium is None:
            return CDPTargetPlan(action="wait", reason="POLARIUM_TARGET_NOT_DETECTED", friday_url=self._friday_frontend_url)
        if not frontend_available:
            self._last_attempt_at = now_ms
            return CDPTargetPlan(action="wait", reason="FRIDAY_FRONTEND_UNAVAILABLE", friday_url=self._friday_frontend_url, polarium_target_id=polarium.target_id)
        if self._last_attempt_at is not None and now_ms - self._last_attempt_at < self._min_attempt_interval_ms:
            return CDPTargetPlan(action="wait", reason="FRIDAY_OPEN_THROTTLED", friday_url=self._friday_frontend_url, polarium_target_id=polarium.target_id)
        self._last_attempt_at = now_ms
        return CDPTargetPlan(action="open_friday", reason="SAFE_TO_OPEN_FRIDAY_TAB", friday_url=self._friday_frontend_url, polarium_target_id=polarium.target_id)

    def mark_opened(self, target_id: str | None) -> None:
        self._opened_or_reused = True

    def _find_polarium_target(self, targets: tuple[CDPTarget, ...]) -> CDPTarget | None:
        for target in targets:
            if target.kind == "page" and self._polarium_host_fragment in target.url:
                return target
        return None

    def _find_friday_target(self, targets: tuple[CDPTarget, ...]) -> CDPTarget | None:
        for target in targets:
            if target.kind == "page" and _normalize_url(target.url).startswith(self._friday_frontend_url):
                return target
        return None


def _normalize_url(url: str) -> str:
    return url.rstrip("/")
