from __future__ import annotations

from collections import deque

from app.market.providers.pocket.models import PocketDomainEvent
from tools.pocket_parser.models import PocketReplayResult
from tools.pocket_parser.replay_engine import PocketOfflineReplayEngine


class PocketReplayTransport:
    def __init__(self, har_paths: tuple[str, ...]) -> None:
        self.har_paths = har_paths
        self._events: deque[PocketDomainEvent] = deque()
        self._running = False
        self.parser_result: PocketReplayResult | None = None

    def start(self) -> None:
        engine = PocketOfflineReplayEngine()
        self.parser_result = engine.replay(self.har_paths)
        self._events = deque(_events_from_result(self.parser_result))
        self._running = True

    def stop(self) -> None:
        self._running = False
        self._events.clear()

    def is_running(self) -> bool:
        return self._running

    def next_event(self) -> PocketDomainEvent | None:
        if not self._running or not self._events:
            return None
        return self._events.popleft()

    def status(self) -> dict:
        return {
            "transport": "REPLAY",
            "running": self._running,
            "queued_events": len(self._events),
            "sessions": self.parser_result.sessions_processed if self.parser_result else 0,
        }


def _events_from_result(result: PocketReplayResult) -> list[PocketDomainEvent]:
    events: list[PocketDomainEvent] = []
    sequence = 0
    events.append(PocketDomainEvent("auth/success", {"mode": "replay"}, source="replay", sequence=sequence))
    sequence += 1
    if result.assets:
        events.append(PocketDomainEvent("updateAssets", tuple(result.assets), source="replay", sequence=sequence))
        sequence += 1
    for changed in result.change_symbols:
        events.append(PocketDomainEvent("changeSymbol", changed, source="replay", sequence=sequence))
        sequence += 1
    for update in result.chart_updates:
        events.append(PocketDomainEvent("updateCharts", update, source="replay", sequence=sequence))
        sequence += 1
    for batch in result.history_batches:
        events.append(PocketDomainEvent("updateHistoryNewFast", batch, source="replay", sequence=sequence))
        sequence += 1
    for tick in result.ticks:
        events.append(PocketDomainEvent("updateStream", tick, source="replay", sequence=sequence))
        sequence += 1
    return events

