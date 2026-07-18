from __future__ import annotations

from tools.pocket_parser.event_router import PocketEventRouter
from tools.pocket_parser.frame_reader import read_har_events
from tools.pocket_parser.models import PocketReplayResult
from tools.pocket_parser.offline_store import PocketOfflineStore


class PocketOfflineReplayEngine:
    def __init__(self) -> None:
        self.store = PocketOfflineStore()
        self.router = PocketEventRouter(self.store)

    def replay(self, har_paths: tuple[str, ...]) -> PocketReplayResult:
        result = PocketReplayResult(har_paths=har_paths)
        for session_index, har_path in enumerate(har_paths, start=1):
            events = read_har_events(har_path, session_index=session_index)
            if events:
                result.sessions_processed += 1
            result.frames_total += len(events)
            for event in sorted(events, key=lambda item: (item.timestamp is None, item.timestamp or 0, item.frame_index)):
                if event.parse_error:
                    result.frames_invalid += 1
                else:
                    result.frames_valid += 1
                self.router.route(event, result)
        return result

