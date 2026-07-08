from fastapi import APIRouter, Query

from app.core.config import settings
from app.models.candle import Timeframe
from app.models.decision import DecisionResponse
from app.services.ai_decision import AIDecisionEngine

router = APIRouter(prefix="/ai", tags=["AI Decision Engine"])


@router.get("/decision", response_model=DecisionResponse)
def get_ai_decision(
    symbol: str = Query(default=settings.default_symbol, description="Ativo analisado, exemplo: EURUSD-OTC"),
    timeframe: Timeframe = Query(default=settings.default_timeframe, description="Timeframe analisado"),
    limit: int = Query(default=20, ge=5, le=500, description="Quantidade de candles usados na análise"),
) -> DecisionResponse:
    """Retorna uma decisão probabilística baseada nos candles do Market Reader."""
    engine = AIDecisionEngine()
    return engine.analyze(symbol=symbol, timeframe=timeframe, limit=limit)
