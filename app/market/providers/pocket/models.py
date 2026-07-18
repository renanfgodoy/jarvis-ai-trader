from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from tools.pocket_parser.models import PocketAssetInfo, PocketHistoryBatch, PocketRealtimeTick

PocketEventType = Literal[
    "auth/success",
    "updateAssets",
    "changeSymbol",
    "updateHistoryNewFast",
    "updateStream",
    "updateCharts",
    "disconnect",
    "reconnect",
    "invalid",
    "unknown",
]
ConnectionState = Literal["STOPPED", "STARTING", "CONNECTING", "ONLINE", "RECONNECTING", "OFFLINE", "ERROR"]
SessionState = Literal["EMPTY", "AUTHORIZED_REPLAY", "DISCONNECTED", "ERROR"]
HistoryState = Literal["EMPTY", "BOOTSTRAPPING", "LIMITED", "READY", "ERROR"]


@dataclass(frozen=True)
class PocketDomainEvent:
    event_type: PocketEventType | str
    payload: Any = None
    source: str = "fixture"
    session_index: int = 0
    sequence: int = 0


@dataclass(frozen=True)
class PocketAssetCatalog:
    assets: tuple[PocketAssetInfo, ...]


@dataclass(frozen=True)
class PocketHistoryEvent:
    batch: PocketHistoryBatch


@dataclass(frozen=True)
class PocketRealtimeEvent:
    tick: PocketRealtimeTick

