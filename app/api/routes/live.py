import asyncio
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.models.candle import Timeframe
from app.services.live_market import LiveMarketEngine

router = APIRouter(prefix="/live", tags=["Live Market Engine"])


@router.get("/candles")
def get_live_candles(
    symbol: str = Query(default=settings.default_symbol, description="Ativo do gráfico ao vivo"),
    timeframe: Timeframe = Query(default=settings.default_timeframe, description="Timeframe do candle"),
    limit: int = Query(default=120, ge=30, le=300, description="Quantidade de candles vivos"),
) -> dict:
    """Retorna candles vivos em modo DEMO para o gráfico Candlestick."""
    return LiveMarketEngine().get_live_candles(symbol=symbol, timeframe=timeframe, limit=limit).model_dump(mode="json")


@router.get("/tick")
def get_live_tick(
    symbol: str = Query(default=settings.default_symbol, description="Ativo selecionado"),
    timeframe: Timeframe = Query(default=settings.default_timeframe, description="Timeframe do workspace"),
    limit: int = Query(default=120, ge=30, le=300, description="Quantidade de candles"),
) -> dict:
    """Retorna um pacote completo do Live Workspace, incluindo countdown, sinal e scanner."""
    return LiveMarketEngine().get_tick(symbol=symbol, timeframe=timeframe, limit=limit).model_dump(mode="json")


@router.get("/workspace")
def get_live_workspace(
    symbol: str = Query(default=settings.default_symbol, description="Ativo selecionado no workspace"),
    timeframe: Timeframe = Query(default=settings.default_timeframe, description="Timeframe do gráfico"),
    limit: int = Query(default=120, ge=30, le=300, description="Quantidade de candles para o gráfico"),
) -> dict:
    """Mantém compatibilidade com a Sprint 12 usando o novo Live Market Engine."""
    tick = LiveMarketEngine().get_tick(symbol=symbol, timeframe=timeframe, limit=limit)
    return {
        "mode": "LIVE_WORKSPACE_DEMO",
        "symbol": tick.symbol,
        "timeframe": tick.timeframe,
        "provider": tick.provider,
        "candles": [candle.model_dump(mode="json") for candle in tick.candles],
        "signal": tick.signal.model_dump(mode="json"),
        "top_assets": [asset.model_dump(mode="json") for asset in tick.top_assets],
        "scanner_total": tick.scanner_total,
        "countdown_seconds": tick.countdown_seconds,
        "last_price": tick.price,
        "events": tick.events,
        "disclaimer": tick.disclaimer,
    }


@router.websocket("/workspace/ws")
async def live_workspace_ws(websocket: WebSocket) -> None:
    """WebSocket DEMO para streaming do Live Trading Workspace."""
    await websocket.accept()
    symbol = websocket.query_params.get("symbol", settings.default_symbol)
    timeframe = websocket.query_params.get("timeframe", settings.default_timeframe)
    try:
        while True:
            tick = LiveMarketEngine().get_tick(symbol=symbol, timeframe=timeframe, limit=120)
            await websocket.send_json(tick.model_dump(mode="json"))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
