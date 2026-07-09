from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.candle import Candle, Timeframe
from app.models.scanner import AssetScanResult
from app.models.signal import SignalAnalysisResponse

LiveMode = Literal["LIVE_DEMO", "LIVE_STREAM", "DRY_RUN"]


class LiveMarketTick(BaseModel):
    """Pacote de atualização incremental para o workspace ao vivo."""

    type: str = "live_tick"
    mode: LiveMode = "LIVE_DEMO"
    symbol: str
    timeframe: Timeframe
    provider: str
    server_time: datetime
    price: float = Field(..., gt=0)
    candle: Candle
    candles: list[Candle]
    countdown_seconds: int = Field(..., ge=0, le=300)
    signal: SignalAnalysisResponse
    top_assets: list[AssetScanResult]
    scanner_total: int
    events: list[str] = Field(default_factory=list)
    demo_only: bool = True
    disclaimer: str = "Streaming em modo DEMO/DRY_RUN. Nenhuma ordem real é enviada."


class LiveCandlesResponse(BaseModel):
    """Resposta REST com candles vivos e metadados de streaming."""

    mode: LiveMode = "LIVE_DEMO"
    symbol: str
    timeframe: Timeframe
    provider: str
    count: int
    countdown_seconds: int
    candles: list[Candle]
    last_price: float
    status: str = "streaming_demo"
    disclaimer: str = "Candles simulados em tempo real para desenvolvimento seguro."
