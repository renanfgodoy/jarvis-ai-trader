from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PolariumAnalysisReadinessState = Literal["NO_HISTORY", "BOOTSTRAPPING", "LIMITED", "READY", "STALE"]

HISTORY_EVENTS = {"first-candles", "candles"}
REALTIME_EVENTS = {"candle-generated", "candles-generated"}


@dataclass(frozen=True)
class PolariumReadinessConfig:
    limited_candles: int = 20
    ready_candles: int = 50
    stale_after_ms: int = 120_000


@dataclass
class PolariumReadinessSnapshot:
    state: PolariumAnalysisReadinessState
    history_count: int
    required_candles: int
    limited_candles: int
    realtime_count: int = 0
    last_history_update: int | None = None
    last_realtime_update: int | None = None

    @property
    def progress(self) -> int:
        return min(self.history_count, self.required_candles)

    def sanitized(self) -> dict:
        return {
            "state": self.state,
            "history_count": self.history_count,
            "required_candles": self.required_candles,
            "limited_candles": self.limited_candles,
            "progress": self.progress,
            "realtime_count": self.realtime_count,
            "last_history_update": self.last_history_update,
            "last_realtime_update": self.last_realtime_update,
        }


class PolariumReadinessTracker:
    def __init__(self, config: PolariumReadinessConfig | None = None) -> None:
        self._config = config or PolariumReadinessConfig()
        self._items: dict[tuple[int, int], PolariumReadinessSnapshot] = {}

    @property
    def config(self) -> PolariumReadinessConfig:
        return self._config

    def start_bootstrap(self, active_id: int, raw_size: int | None, *, now_ms: int) -> None:
        if raw_size is None:
            return
        key = (active_id, raw_size)
        current = self._items.get(key)
        if current is not None and current.state in {"LIMITED", "READY"}:
            return
        self._items[key] = PolariumReadinessSnapshot(
            state="BOOTSTRAPPING",
            history_count=current.history_count if current else 0,
            required_candles=self._config.ready_candles,
            limited_candles=self._config.limited_candles,
            realtime_count=current.realtime_count if current else 0,
            last_history_update=current.last_history_update if current else None,
            last_realtime_update=current.last_realtime_update if current else None,
        )

    def record_history(self, active_id: int, raw_size: int, history_count: int, *, now_ms: int) -> PolariumReadinessSnapshot:
        snapshot = self._items.get((active_id, raw_size))
        realtime_count = snapshot.realtime_count if snapshot else 0
        state: PolariumAnalysisReadinessState = "READY" if history_count >= self._config.ready_candles else "LIMITED" if history_count >= self._config.limited_candles else "LIMITED" if history_count > 0 else "NO_HISTORY"
        updated = PolariumReadinessSnapshot(
            state=state,
            history_count=history_count,
            required_candles=self._config.ready_candles,
            limited_candles=self._config.limited_candles,
            realtime_count=realtime_count,
            last_history_update=now_ms,
            last_realtime_update=snapshot.last_realtime_update if snapshot else None,
        )
        self._items[(active_id, raw_size)] = updated
        return updated

    def record_realtime(self, active_id: int, raw_size: int, *, now_ms: int) -> PolariumReadinessSnapshot:
        snapshot = self._items.get((active_id, raw_size))
        if snapshot is None:
            snapshot = PolariumReadinessSnapshot(
                state="NO_HISTORY",
                history_count=0,
                required_candles=self._config.ready_candles,
                limited_candles=self._config.limited_candles,
            )
        snapshot.realtime_count += 1
        snapshot.last_realtime_update = now_ms
        self._items[(active_id, raw_size)] = snapshot
        return snapshot

    def snapshot(self, active_id: int | None, raw_size: int | None, *, now_ms: int | None = None) -> PolariumReadinessSnapshot:
        if active_id is None or raw_size is None:
            return self._empty()
        snapshot = self._items.get((active_id, raw_size), self._empty())
        if now_ms is not None and snapshot.last_realtime_update is not None and now_ms - snapshot.last_realtime_update > self._config.stale_after_ms:
            return PolariumReadinessSnapshot(
                state="STALE",
                history_count=snapshot.history_count,
                required_candles=snapshot.required_candles,
                limited_candles=snapshot.limited_candles,
                realtime_count=snapshot.realtime_count,
                last_history_update=snapshot.last_history_update,
                last_realtime_update=snapshot.last_realtime_update,
            )
        return snapshot

    def _empty(self) -> PolariumReadinessSnapshot:
        return PolariumReadinessSnapshot(
            state="NO_HISTORY",
            history_count=0,
            required_candles=self._config.ready_candles,
            limited_candles=self._config.limited_candles,
        )
