from __future__ import annotations

from app.vision.enums import VisionStrategyMode
from app.vision.models import VisionAnalysisRequest


VISION_SYSTEM_PROMPT = """
You are Friday, a conservative visual market-chart analyst.
Analyze only what is visible in the submitted screenshot.
Do not invent prices, indicators, assets, timeframe, support levels, or context outside the image.
Do not promise profit, certainty, accuracy, or guaranteed execution.
Confidence means visual-reading confidence only, never probability of profit.
Prefer WAIT or DO_NOT_TRADE whenever the visual evidence is incomplete, conflicted, stretched, illegible, or risky.
CALL or PUT may only be used when the visible context supports a conditional scenario and you provide market_reading,
entry_condition, invalidation_condition, risk, warnings, and limitations.
Respond only with JSON matching the supplied schema.
""".strip()


def build_vision_user_prompt(context: VisionAnalysisRequest) -> str:
    strategy_hint = {
        VisionStrategyMode.COMPLETE: "Use a complete visual reading with risk-first behavior.",
        VisionStrategyMode.PRICE_ACTION: "Prioritize candle structure and visible price action.",
        VisionStrategyMode.SUPPORT_RESISTANCE: "Prioritize visible support and resistance zones without exact prices unless legible.",
        VisionStrategyMode.TREND: "Prioritize visible trend structure and trend exhaustion risk.",
    }[context.strategy_mode]
    return "\n".join(
        [
            "Analyze this trading-chart screenshot conservatively.",
            f"Asset informed by user: {context.asset or 'unknown'}",
            f"Timeframe informed by user: {context.timeframe}",
            f"Expiration informed by user: {context.expiration}",
            f"Strategy mode: {context.strategy_mode.value}",
            f"Strategy instruction: {strategy_hint}",
            f"User notes: {context.user_notes or 'none'}",
            "If chart/candles are not clearly visible, return DO_NOT_TRADE.",
            "If unsure, return WAIT or DO_NOT_TRADE.",
        ]
    )


VISION_RESULT_JSON_SCHEMA = {
    "name": "friday_vision_analysis",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "decision",
            "asset_detected",
            "timeframe_detected",
            "expiration_considered",
            "trend",
            "market_state",
            "risk",
            "confidence",
            "image_quality",
            "chart_visible",
            "candles_visible",
            "summary",
            "market_reading",
            "entry_condition",
            "invalidation_condition",
            "support_zones",
            "resistance_zones",
            "warnings",
            "limitations",
        ],
        "properties": {
            "decision": {"type": "string", "enum": ["CALL", "PUT", "WAIT", "DO_NOT_TRADE"]},
            "asset_detected": {"type": ["string", "null"]},
            "timeframe_detected": {"type": ["string", "null"]},
            "expiration_considered": {"type": "string"},
            "trend": {"type": "string", "enum": ["BULLISH", "BEARISH", "SIDEWAYS", "UNCLEAR"]},
            "market_state": {
                "type": "string",
                "enum": ["TRENDING", "RANGING", "BREAKOUT", "REVERSAL_ATTEMPT", "EXHAUSTION", "CHOPPY", "UNCLEAR"],
            },
            "risk": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "EXTREME"]},
            "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
            "image_quality": {"type": "string", "enum": ["GOOD", "ACCEPTABLE", "POOR", "UNUSABLE"]},
            "chart_visible": {"type": "boolean"},
            "candles_visible": {"type": "boolean"},
            "summary": {"type": "string"},
            "market_reading": {"type": "string"},
            "entry_condition": {"type": "string"},
            "invalidation_condition": {"type": "string"},
            "support_zones": {"type": "array", "items": {"type": "string"}},
            "resistance_zones": {"type": "array", "items": {"type": "string"}},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "limitations": {"type": "array", "items": {"type": "string"}},
        },
    },
}
