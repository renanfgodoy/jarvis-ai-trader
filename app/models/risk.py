from typing import Literal

from app.models.account import AccountCurrency
from pydantic import BaseModel, Field, model_validator

RiskDecision = Literal["APPROVED", "BLOCKED"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class RiskCheckRequest(BaseModel):
    """Entrada para validar se uma operação respeita as regras oficiais de risco."""

    bankroll: float = Field(default=200.0, gt=0, description="Banca atual do operador")
    entry_value: float | None = Field(default=None, gt=0, description="Valor da entrada. Se vazio, usa 5% da banca")
    daily_wins: int = Field(default=0, ge=0, description="Quantidade de WINs no dia")
    daily_losses: int = Field(default=0, ge=0, description="Quantidade de LOSSes no dia")
    gale_used: int = Field(default=0, ge=0, description="Quantidade de gales já usados na operação")
    payout: float = Field(default=80.0, ge=0, le=100, description="Payout estimado da operação")
    account_currency: AccountCurrency = Field(default="BRL", description="Moeda da conta: BRL ou USD")

    @model_validator(mode="after")
    def validate_entry_value(self) -> "RiskCheckRequest":
        """Garante que a entrada não seja maior que a banca."""
        if self.entry_value is not None and self.entry_value > self.bankroll:
            raise ValueError("entry_value não pode ser maior que bankroll")
        return self


class RiskCheckResponse(BaseModel):
    """Resposta padronizada do Risk Manager."""

    decision: RiskDecision
    allowed: bool
    risk_level: RiskLevel
    risk_score: int = Field(..., ge=0, le=100)
    bankroll: float
    recommended_entry: float
    max_entry_allowed: float
    daily_wins: int
    daily_losses: int
    gale_used: int
    rules_checked: list[str]
    reasons: list[str]
    warnings: list[str]
    account_currency: AccountCurrency = "BRL"
    minimum_entry: float = 5.0
    currency_symbol: str = "R$"
    official_rule: str = "Primeiro proteger a banca. Depois crescer a banca."
    disclaimer: str = "Controle de risco simulado para desenvolvimento. Não é recomendação financeira."
