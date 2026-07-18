from __future__ import annotations

from enum import StrEnum


class VisionTradeDecision(StrEnum):
    CALL = "CALL"
    PUT = "PUT"
    WAIT = "WAIT"
    DO_NOT_TRADE = "DO_NOT_TRADE"


class VisionTrend(StrEnum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAYS = "SIDEWAYS"
    UNCLEAR = "UNCLEAR"


class VisionRiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class VisionMarketState(StrEnum):
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    BREAKOUT = "BREAKOUT"
    REVERSAL_ATTEMPT = "REVERSAL_ATTEMPT"
    EXHAUSTION = "EXHAUSTION"
    CHOPPY = "CHOPPY"
    UNCLEAR = "UNCLEAR"


class VisionImageQuality(StrEnum):
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    POOR = "POOR"
    UNUSABLE = "UNUSABLE"


class VisionStrategyMode(StrEnum):
    COMPLETE = "COMPLETE"
    PRICE_ACTION = "PRICE_ACTION"
    SUPPORT_RESISTANCE = "SUPPORT_RESISTANCE"
    TREND = "TREND"
