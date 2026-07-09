from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.candle import Timeframe

ProviderSignal = Literal["BUY", "SELL", "WAIT"]
WebhookStatus = Literal["queued", "rejected"]


class TradingViewWebhookPayload(BaseModel):
    """Payload normalizado recebido por webhook do TradingView.

    Nesta Sprint o webhook apenas recebe e normaliza o alerta. Ele não executa
    ordens e não deve ser usado como recomendação financeira.
    """

    symbol: str = Field(..., min_length=2, examples=["EURUSD-OTC"])
    timeframe: Timeframe = Field(default="M1", examples=["M1"])
    signal: ProviderSignal = Field(..., examples=["BUY"])
    price: float = Field(..., gt=0, examples=[1.17545])
    strategy: str = Field(default="TradingView Alert", min_length=1, max_length=80, examples=["Jarvis v1"])
    timestamp: datetime | None = Field(default=None, description="Timestamp opcional do alerta.")

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("signal")
    @classmethod
    def normalize_signal(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("strategy")
    @classmethod
    def normalize_strategy(cls, value: str) -> str:
        return value.strip()

    @field_validator("timestamp")
    @classmethod
    def normalize_timestamp(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class TradingViewWebhookResponse(BaseModel):
    """Resposta do Provider Engine ao receber um alerta do TradingView."""

    received: bool
    provider: str = "TradingView"
    status: WebhookStatus
    symbol: str
    timeframe: Timeframe
    signal: ProviderSignal
    price: float
    strategy: str
    queued_at: datetime
    message: str
    disclaimer: str = "Webhook recebido apenas para análise. Não executa ordens automaticamente."


class ProviderInfo(BaseModel):
    """Metadados simples sobre providers disponíveis no sistema."""

    name: str
    type: str
    status: str
    description: str
