from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

Timeframe = Literal["M1", "M5", "M15", "M30", "H1", "H4", "D1"]


class Candle(BaseModel):
    """Representa um candle OHLC normalizado para uso interno do sistema."""

    symbol: str = Field(..., examples=["EURUSD-OTC"])
    timeframe: Timeframe = Field(default="M1")
    timestamp: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: float | None = Field(default=None, ge=0)

    @field_validator("timestamp")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        """Garante timestamp com timezone para evitar ambiguidades no backtesting."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    @model_validator(mode="after")
    def validate_ohlc(self) -> "Candle":
        """Valida a consistência básica do candle."""
        max_price = max(self.open, self.close)
        min_price = min(self.open, self.close)

        if self.high < max_price:
            raise ValueError("high não pode ser menor que open/close")
        if self.low > min_price:
            raise ValueError("low não pode ser maior que open/close")
        if self.low > self.high:
            raise ValueError("low não pode ser maior que high")
        return self


class MarketSnapshot(BaseModel):
    """Resumo normalizado de mercado para consumo da API e motores internos."""

    provider: str
    symbol: str
    timeframe: Timeframe
    candles_count: int
    last_candle: Candle
    status: str = "ok"
