from __future__ import annotations

from app.market.providers.pocket.contracts import PocketTransport
from app.market.providers.pocket.runtime import PocketMarketRuntime


class PocketReadOnlyLiveSource:
    def __init__(self, transport: PocketTransport, runtime: PocketMarketRuntime) -> None:
        self.transport = transport
        self.runtime = runtime
        self.events_routed = 0

    def start(self) -> None:
        self.runtime.start(live_connection=False)
        if hasattr(self.transport, "set_domain_event_handler"):
            self.transport.set_domain_event_handler(self._process_event)
        self.transport.start()
        while True:
            event = self.transport.next_event()
            if event is None:
                break
            self._process_event(event)

    def stop(self) -> None:
        if hasattr(self.transport, "set_domain_event_handler"):
            self.transport.set_domain_event_handler(None)
        self.transport.stop()
        self.runtime.stop()

    def status(self) -> dict:
        return {"transport": self.transport.status(), "events_routed": self.events_routed, "runtime": self.runtime.status()}

    def _process_event(self, event) -> None:
        self.runtime.process(event)
        self.events_routed += 1
