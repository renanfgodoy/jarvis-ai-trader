from __future__ import annotations

from app.market.providers.pocket.models import HistoryState


class PocketReadinessTracker:
    def __init__(self, history_required: int = 50) -> None:
        self.history_required = history_required
        self._counts: dict[str, int] = {}
        self._errors: set[str] = set()

    def start_bootstrap(self, key: str) -> HistoryState:
        self._counts.setdefault(key, 0)
        return "BOOTSTRAPPING"

    def mark_error(self, key: str) -> HistoryState:
        self._errors.add(key)
        return "ERROR"

    def update_history(self, key: str, count: int) -> HistoryState:
        self._counts[key] = count
        return self.state_for(key)

    def count_for(self, key: str) -> int:
        return self._counts.get(key, 0)

    def state_for(self, key: str) -> HistoryState:
        if key in self._errors:
            return "ERROR"
        count = self._counts.get(key, 0)
        if count <= 0:
            return "EMPTY"
        if count < self.history_required:
            return "LIMITED"
        return "READY"

