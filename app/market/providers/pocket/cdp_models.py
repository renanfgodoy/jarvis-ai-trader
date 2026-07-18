from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ObserverState = Literal[
    "STOPPED",
    "STARTING_CHROME",
    "WAITING_TARGET",
    "TARGET_ATTACHED",
    "WAITING_MARKET_SOCKET",
    "OBSERVING",
    "DEGRADED",
    "ERROR",
]

SocketClassification = Literal["UNKNOWN", "CANDIDATE", "MARKET_SOCKET", "AUXILIARY_SOCKET", "REJECTED"]


@dataclass(frozen=True)
class PocketCDPTarget:
    target_id: str
    type: str
    url: str
    title: str = ""
    attached: bool = False
    websocket_debugger_url: str | None = None


@dataclass(frozen=True)
class PocketCDPEvent:
    method: str
    params: dict[str, Any]


@dataclass
class PocketObservedSocket:
    request_id: str
    target_id: str
    url_sanitized: str
    host: str
    path: str
    query_keys: tuple[str, ...]
    frames_sent_count: int = 0
    frames_received_count: int = 0
    event_names: set[str] = field(default_factory=set)
    classification: SocketClassification = "UNKNOWN"
    classification_reason: str = "NO_MARKET_EVIDENCE"


@dataclass(frozen=True)
class PocketObservedFrame:
    cdp_request_id: str
    target_id: str
    direction: Literal["sent", "received"]
    timestamp: float | None
    payload_data: str
