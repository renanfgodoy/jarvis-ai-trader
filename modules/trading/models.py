from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from sdk.models import ModuleResponse

from modules.trading.contracts import TradingDecision, TradingMarket, TradingRisk, TradingStrategy


@dataclass(frozen=True)
class TradingRequest:
    market: TradingMarket
    symbol: str
    timeframe: str
    strategy: TradingStrategy
    message: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))


@dataclass(frozen=True)
class TradingScenario:
    market: TradingMarket
    symbol: str
    timeframe: str
    strategy: TradingStrategy
    bias: str
    context: str
    risk: TradingRisk


@dataclass(frozen=True)
class TradingResponse:
    status: str
    trend: str
    support: str
    resistance: str
    decision: TradingDecision
    confidence: int
    risk: TradingRisk
    analysis: str
    execution: ModuleResponse
    metadata: Mapping[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            object.__setattr__(self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc))
