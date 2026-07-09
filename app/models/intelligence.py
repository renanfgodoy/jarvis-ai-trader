from typing import Literal

from pydantic import BaseModel, Field

from app.models.candle import Timeframe
from app.models.signal import MomentumLevel, SignalTrend, VolatilityLevel

ConfluenceStatus = Literal["APPROVED", "WATCHLIST", "BLOCKED"]
RiskBias = Literal["LOW", "MEDIUM", "HIGH"]


class ConfluenceFactor(BaseModel):
    """Um fator técnico usado para compor o score operacional."""

    name: str
    points: int = Field(..., ge=0)
    max_points: int = Field(..., ge=1)
    passed: bool
    explanation: str


class MarketIntelligenceRequest(BaseModel):
    """Parâmetros para análise inteligente de mercado."""

    symbol: str = Field(default="EURUSD-OTC", min_length=3)
    timeframe: Timeframe = Field(default="M1")
    payout: float = Field(default=80.0, ge=0, le=100)
    minimum_score: int = Field(default=80, ge=0, le=100)
    minimum_payout: float = Field(default=75.0, ge=0, le=100)
    candle_limit: int = Field(default=80, ge=30, le=500)


class MarketIntelligenceResponse(BaseModel):
    """Análise consolidada de confluência para um ativo."""

    symbol: str
    timeframe: Timeframe
    signal: SignalTrend
    score: int = Field(..., ge=0, le=100)
    status: ConfluenceStatus
    confidence_label: str
    payout: float
    minimum_score: int
    minimum_payout: float
    risk_bias: RiskBias
    trend: SignalTrend
    momentum: MomentumLevel
    volatility: VolatilityLevel
    ema9: float
    ema21: float
    rsi14: float
    atr14: float
    strength: int = Field(..., ge=0, le=100)
    factors: list[ConfluenceFactor]
    reasons: list[str]
    warnings: list[str]
    action: str
    official_rule: str = "Não buscamos mais operações. Buscamos operações melhores."
    disclaimer: str = "Análise probabilística para apoio à decisão. Não é recomendação financeira."


class MarketIntelligenceScannerResponse(BaseModel):
    """Ranking inteligente dos melhores ativos por score de confluência."""

    timeframe: Timeframe
    assets_scanned: int
    top_limit: int
    minimum_score: int
    minimum_payout: float
    approved_count: int
    watchlist_count: int
    blocked_count: int
    results: list[MarketIntelligenceResponse]
    official_rule: str = "Primeiro proteger a banca. Depois crescer a banca."
    disclaimer: str = "Scanner de inteligência probabilística. Validar em DEMO antes de qualquer uso operacional."
