from typing import Literal

from pydantic import BaseModel, Field

from app.models.candle import Timeframe

SignalAction = Literal["BUY", "SELL", "WAIT"]
TrendDirection = Literal["UP", "DOWN", "SIDEWAYS"]
SignalGrade = Literal["A+", "A", "B", "C", "NO_TRADE"]


class DecisionRequest(BaseModel):
    """Parâmetros usados para solicitar uma decisão do motor de análise."""

    symbol: str = Field(default="EURUSD-OTC", description="Ativo analisado")
    timeframe: Timeframe = Field(default="M1", description="Timeframe analisado")
    limit: int = Field(default=20, ge=5, le=500, description="Quantidade de candles usados na análise")


class DecisionResponse(BaseModel):
    """Resposta padronizada do AI Decision Engine.

    Esta versão é baseada em regras. Ela não promete lucro e não deve ser usada
    como sinal real sem backtesting e validação em ambiente de demonstração.
    """

    symbol: str
    timeframe: Timeframe
    signal: SignalAction
    grade: SignalGrade
    confidence: int = Field(..., ge=0, le=100)
    trend: TrendDirection
    momentum: float
    volatility: float
    score: int = Field(..., ge=0, le=100)
    reasons: list[str]
    warnings: list[str]
    disclaimer: str = "Análise probabilística para apoio à decisão. Não é recomendação financeira."
