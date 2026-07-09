from typing import Literal

from pydantic import BaseModel, Field

from app.models.candle import Timeframe

SignalTrend = Literal["BUY", "SELL", "NEUTRAL"]
VolatilityLevel = Literal["LOW", "NORMAL", "HIGH"]
MomentumLevel = Literal["BULLISH", "BEARISH", "NEUTRAL"]


class SignalAnalysisResponse(BaseModel):
    """Resposta do Signal Engine com indicadores técnicos consolidados."""

    symbol: str
    timeframe: Timeframe
    candles_analyzed: int
    ema9: float
    ema21: float
    rsi14: float
    atr14: float
    trend: SignalTrend
    momentum: MomentumLevel
    volatility: VolatilityLevel
    strength: int = Field(..., ge=0, le=100)
    reasons: list[str]
    warnings: list[str]
    disclaimer: str = "Análise técnica probabilística para apoio à decisão. Não é recomendação financeira."
