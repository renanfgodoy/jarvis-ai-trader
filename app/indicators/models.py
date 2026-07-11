from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IndicatorRequest:
    name: str
    active_id: int
    raw_size: int
    limit: int
    parameters: dict[str, Any] | None = None


@dataclass(frozen=True)
class IndicatorValue:
    name: str
    value: Any
    metadata: dict[str, Any]


@dataclass(frozen=True)
class IndicatorResult:
    success: bool
    request: IndicatorRequest
    candles_used: int
    value: IndicatorValue | None
    errors: tuple[str, ...] = ()
