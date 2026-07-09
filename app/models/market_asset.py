from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.candle import Timeframe

AssetStatus = Literal["OPEN", "CLOSED", "SUSPENDED"]
DataQuality = Literal["SIMULATED", "REAL", "DELAYED", "UNAVAILABLE"]


class MarketAsset(BaseModel):
    """Ativo negociável normalizado pelo Provider Engine.

    Este modelo separa a lista de ativos/payout/status do fluxo de candles.
    Com isso o Scanner pode ranquear ativos considerando se estão abertos,
    qual o payout e se os dados são reais ou simulados.
    """

    symbol: str = Field(..., examples=["EURUSD-OTC"])
    display_name: str = Field(..., examples=["EUR/USD OTC"])
    category: str = Field(default="otc", examples=["forex", "crypto", "commodity", "otc"])
    status: AssetStatus = Field(default="OPEN")
    payout: float = Field(default=80.0, ge=0, le=100)
    supported_timeframes: list[Timeframe] = Field(default_factory=lambda: ["M1", "M5", "M15"])
    data_quality: DataQuality = Field(default="SIMULATED")
    provider: str = Field(default="simulated")
    is_tradable: bool = Field(default=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()


class MarketAssetsResponse(BaseModel):
    """Resposta padronizada para ativos disponíveis no provider ativo."""

    provider: str
    data_quality: DataQuality
    total_assets: int
    open_assets: int
    closed_assets: int
    simulated: bool
    assets: list[MarketAsset]
    message: str
    disclaimer: str = "Dados usados para apoio à decisão. Não são recomendação financeira."
