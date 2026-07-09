from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from app.models.candle import Timeframe

ExecutionMode = Literal["DEMO", "DRY_RUN"]
ExecutionSignal = Literal["BUY", "SELL"]
ExecutionStatus = Literal["READY", "APPROVED", "BLOCKED", "SIMULATED"]


class ExecutionRequest(BaseModel):
    """Entrada para simular uma execução controlada em conta demo."""

    symbol: str = Field(default="EURUSD-OTC", min_length=3, description="Ativo desejado")
    timeframe: Timeframe = Field(default="M1", description="Timeframe operacional")
    signal: ExecutionSignal = Field(default="BUY", description="Direção da operação")
    bankroll: float = Field(default=200.0, gt=0, description="Banca atual usada pelo Risk Manager")
    entry_value: float | None = Field(default=None, gt=0, description="Valor da entrada. Se vazio, usa 5% da banca")
    daily_wins: int = Field(default=0, ge=0, description="WINs do dia")
    daily_losses: int = Field(default=0, ge=0, description="LOSSes do dia")
    gale_used: int = Field(default=0, ge=0, description="Quantidade de gales já usados")
    payout: float = Field(default=80.0, ge=0, le=100, description="Payout estimado")
    expiration_minutes: int = Field(default=1, ge=1, le=30, description="Expiração simulada em minutos")
    mode: ExecutionMode = Field(default="DEMO", description="Modo de execução permitido nesta fase")

    @model_validator(mode="after")
    def validate_demo_only(self) -> "ExecutionRequest":
        """Bloqueia qualquer modo diferente de demo/dry-run na fase de desenvolvimento."""
        if self.mode not in ("DEMO", "DRY_RUN"):
            raise ValueError("Apenas DEMO ou DRY_RUN são permitidos nesta fase")
        return self


class ExecutionResponse(BaseModel):
    """Resposta padronizada da camada de execução."""

    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    status: ExecutionStatus
    allowed: bool
    mode: ExecutionMode
    provider: str
    account_type: str
    symbol: str
    timeframe: Timeframe
    signal: ExecutionSignal
    entry_value: float
    expiration_minutes: int
    risk_score: int
    risk_decision: str
    action: str
    result: str | None = None
    reasons: list[str]
    warnings: list[str]
    safety_rules: list[str]
    official_rule: str = "Primeiro proteger a banca. Depois crescer a banca."
    disclaimer: str = "Execução em modo DEMO/DRY_RUN. Não envia ordens reais. Não é recomendação financeira."


class ExecutionStatusResponse(BaseModel):
    """Status operacional do Execution Engine."""

    status: ExecutionStatus
    provider: str
    account_type: str
    live_trading_enabled: bool
    demo_only: bool
    supported_modes: list[ExecutionMode]
    safety_rules: list[str]
