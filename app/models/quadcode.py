from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.candle import Timeframe

QuadcodeMode = Literal["DEMO", "DRY_RUN"]
QuadcodeConnectionStatus = Literal["READY", "CONNECTED", "DISCONNECTED", "BLOCKED"]
QuadcodeTradingSignal = Literal["BUY", "SELL"]


class QuadcodeDemoConnectRequest(BaseModel):
    """Solicitação segura para preparar o adapter Quadcode/Polarium em modo DEMO.

    Nesta Sprint o adapter não autentica em conta real, não captura senha e não envia
    ordens. Ele apenas cria a base de configuração para integração futura em DEMO.
    """

    mode: QuadcodeMode = Field(default="DEMO", examples=["DEMO"])
    dry_run: bool = Field(default=True, description="Deve permanecer true durante desenvolvimento.")
    account_type: str = Field(default="DEMO", examples=["DEMO"])
    allow_real_orders: bool = Field(default=False, description="Bloqueado por segurança nesta fase.")

    @field_validator("account_type")
    @classmethod
    def normalize_account_type(cls, value: str) -> str:
        return value.strip().upper()


class QuadcodeConnectionResponse(BaseModel):
    provider: str = "quadcode"
    broker: str = "Polarium"
    mode: QuadcodeMode
    status: QuadcodeConnectionStatus
    connected: bool
    dry_run: bool
    account_type: str = Field(alias="accountType")
    can_trade: bool = Field(alias="canTrade")
    message: str
    safety_rules: list[str] = Field(alias="safetyRules")
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="checkedAt")

    model_config = {"populate_by_name": True}


class QuadcodeSymbolInfo(BaseModel):
    symbol: str
    market: str = "OTC"
    type: str = "digital"
    timeframe_default: Timeframe = Field(default="M1", alias="timeframeDefault")
    enabled: bool = True
    demo_supported: bool = Field(default=True, alias="demoSupported")

    model_config = {"populate_by_name": True}


class QuadcodeSymbolsResponse(BaseModel):
    provider: str = "quadcode"
    broker: str = "Polarium"
    mode: QuadcodeMode = "DEMO"
    total: int
    symbols: list[QuadcodeSymbolInfo]
    disclaimer: str = "Universo inicial para DEMO/Discovery. Não representa garantia de disponibilidade em tempo real."


class QuadcodeDemoOrderRequest(BaseModel):
    """Contrato futuro de ordem DEMO. Mantido em DRY_RUN nesta Sprint."""

    symbol: str = Field(..., examples=["EURUSD-OTC"])
    signal: QuadcodeTradingSignal = Field(..., examples=["BUY"])
    entry_value: float = Field(..., gt=0, examples=[10.0], alias="entryValue")
    timeframe: Timeframe = Field(default="M1")
    expiration_minutes: int = Field(default=1, ge=1, le=5, alias="expirationMinutes")
    dry_run: bool = Field(default=True, alias="dryRun")

    model_config = {"populate_by_name": True}

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("signal")
    @classmethod
    def normalize_signal(cls, value: str) -> str:
        return value.strip().upper()


class QuadcodeDemoOrderResponse(BaseModel):
    accepted: bool
    executed: bool = False
    provider: str = "quadcode"
    broker: str = "Polarium"
    mode: QuadcodeMode = "DRY_RUN"
    symbol: str
    signal: QuadcodeTradingSignal
    entry_value: float = Field(alias="entryValue")
    timeframe: Timeframe
    message: str
    blocked_reason: str | None = Field(default=None, alias="blockedReason")
    disclaimer: str = "Nenhuma ordem foi enviada. Sprint em modo DEMO/DRY_RUN."

    model_config = {"populate_by_name": True}
