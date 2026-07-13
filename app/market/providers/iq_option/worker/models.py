from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

WorkerCommand = Literal["status", "connect", "list_assets", "list_otc_assets", "get_candles", "disconnect", "stop"]


@dataclass(frozen=True)
class WorkerRequest:
    command: WorkerCommand
    params: dict[str, Any]


@dataclass(frozen=True)
class WorkerResponse:
    success: bool
    data: dict[str, Any]
    error_code: str | None


@dataclass(frozen=True)
class WorkerCandle:
    start_timestamp: int
    end_timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float | None

    def sanitized(self) -> dict[str, Any]:
        return {
            "from": self.start_timestamp,
            "to": self.end_timestamp,
            "open": self.open,
            "max": self.high,
            "min": self.low,
            "close": self.close,
            "volume": self.volume,
        }
