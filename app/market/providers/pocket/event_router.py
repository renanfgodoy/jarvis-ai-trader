from __future__ import annotations

from app.market.providers.pocket.errors import POCKET_UNKNOWN_EVENT
from app.market.providers.pocket.models import PocketDomainEvent


class PocketEventRouter:
    def route(self, event: PocketDomainEvent) -> str:
        if event.event_type in {
            "auth/success",
            "updateAssets",
            "changeSymbol",
            "updateHistoryNewFast",
            "updateStream",
            "updateCharts",
            "disconnect",
            "reconnect",
        }:
            return str(event.event_type)
        return POCKET_UNKNOWN_EVENT

