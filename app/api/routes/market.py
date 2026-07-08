from fastapi import APIRouter, Query

from app.core.config import settings
from app.models.candle import MarketSnapshot, Timeframe
from app.services.market_reader import MarketReaderService

router = APIRouter(prefix="/market", tags=["Market Reader"])


@router.get("/candles")
def get_candles(
    symbol: str = Query(default=settings.default_symbol, description="Ativo desejado, exemplo: EURUSD-OTC"),
    timeframe: Timeframe = Query(default=settings.default_timeframe, description="Timeframe dos candles"),
    limit: int = Query(default=20, ge=1, le=500, description="Quantidade de candles"),
) -> dict:
    """Retorna candles OHLC normalizados usando o provider configurado."""
    service = MarketReaderService()
    candles = service.get_candles(symbol=symbol, timeframe=timeframe, limit=limit)
    return {
        "provider": service.provider.name,
        "symbol": symbol.strip().upper(),
        "timeframe": timeframe,
        "count": len(candles),
        "candles": candles,
        "disclaimer": "Dados simulados para desenvolvimento. Não usar como sinal real de operação.",
    }


@router.get("/snapshot", response_model=MarketSnapshot)
def get_market_snapshot(
    symbol: str = Query(default=settings.default_symbol, description="Ativo desejado, exemplo: EURUSD-OTC"),
    timeframe: Timeframe = Query(default=settings.default_timeframe, description="Timeframe dos candles"),
    limit: int = Query(default=20, ge=1, le=500, description="Quantidade de candles"),
) -> MarketSnapshot:
    """Retorna resumo do mercado com o último candle normalizado."""
    service = MarketReaderService()
    return service.get_snapshot(symbol=symbol, timeframe=timeframe, limit=limit)
