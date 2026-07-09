from typing import Literal

from pydantic import BaseModel, Field

from app.models.candle import Timeframe
from app.models.market_asset import DataQuality
from app.models.risk import RiskLevel
from app.models.signal import MomentumLevel, SignalTrend, VolatilityLevel

ScannerStatus = Literal["APPROVED", "WATCHLIST", "BLOCKED"]


class AssetScanResult(BaseModel):
    """Resultado consolidado da análise de um ativo no scanner."""

    rank: int = Field(..., ge=1)
    symbol: str
    timeframe: Timeframe
    signal: SignalTrend
    payout: float = Field(default=80.0, ge=0, le=100)
    data_quality: DataQuality = Field(default="SIMULATED")
    market_status: str = "OPEN"
    score: int = Field(..., ge=0, le=100)
    strength: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    risk_score: int = Field(..., ge=0, le=100)
    status: ScannerStatus
    ema9: float
    ema21: float
    rsi14: float
    atr14: float
    momentum: MomentumLevel
    volatility: VolatilityLevel
    reasons: list[str]
    warnings: list[str]


class AssetScannerResponse(BaseModel):
    """Resposta do Asset Scanner com os melhores ativos ranqueados."""

    timeframe: Timeframe
    assets_scanned: int
    top_limit: int
    approved_count: int
    watchlist_count: int
    blocked_count: int
    provider: str = "simulated"
    data_quality: DataQuality = "SIMULATED"
    simulated: bool = True
    results: list[AssetScanResult]
    official_rule: str = "Não buscamos mais operações. Buscamos operações melhores."
    disclaimer: str = "Scanner probabilístico para apoio à decisão. Não executa ordens e não é recomendação financeira."
