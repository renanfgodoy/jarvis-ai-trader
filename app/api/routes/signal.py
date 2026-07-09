from fastapi import APIRouter, Query

from app.core.config import settings
from app.indicators.signal_engine import SignalEngineService
from app.models.candle import Timeframe
from app.models.signal import SignalAnalysisResponse

router = APIRouter(prefix="/signal", tags=["Signal Engine"])


@router.get("/analyze", response_model=SignalAnalysisResponse)
def analyze_signal(
    symbol: str = Query(default=settings.default_symbol, description="Ativo analisado, exemplo: EURUSD-OTC"),
    timeframe: Timeframe = Query(default=settings.default_timeframe, description="Timeframe analisado"),
    limit: int = Query(default=50, ge=22, le=500, description="Quantidade de candles para cálculo dos indicadores"),
) -> SignalAnalysisResponse:
    """Calcula EMA, RSI, ATR, tendência, momentum, volatilidade e força técnica."""
    return SignalEngineService().analyze(symbol=symbol, timeframe=timeframe, limit=limit)
