from typing import Literal

from pydantic import BaseModel, Field, model_validator

AccountCurrency = Literal["BRL", "USD"]
AccountType = Literal["DEMO", "REAL"]
OperationalTimeframe = Literal["M1", "M5", "M15"]

MIN_ENTRY_BY_CURRENCY: dict[AccountCurrency, float] = {"BRL": 5.0, "USD": 1.0}
CURRENCY_SYMBOLS: dict[AccountCurrency, str] = {"BRL": "R$", "USD": "US$"}


class AccountState(BaseModel):
    """Estado operacional da conta usado pelo AutoTrade Gate.

    A Sprint 14.2 mantém tudo em DEMO. Em integrações futuras, estes dados
    deverão ser lidos diretamente do adapter Polarium/Quadcode autorizado.
    """

    account_type: AccountType = Field(default="DEMO", description="Tipo da conta operacional")
    currency: AccountCurrency = Field(default="BRL", description="Moeda da conta detectada")
    balance: float = Field(default=200.0, gt=0, description="Saldo atual da conta")
    demo_only: bool = True

    @property
    def minimum_entry(self) -> float:
        return MIN_ENTRY_BY_CURRENCY[self.currency]

    @property
    def currency_symbol(self) -> str:
        return CURRENCY_SYMBOLS[self.currency]


class AutoTradeGateRequest(BaseModel):
    """Entrada para liberar ou bloquear o AutoTrade em modo seguro."""

    symbol: str = Field(default="EURUSD-OTC", min_length=3)
    timeframe: OperationalTimeframe | None = Field(default=None, description="M1, M5 ou M15 precisam ser escolhidos antes da análise")
    account_type: AccountType = Field(default="DEMO")
    currency: AccountCurrency = Field(default="BRL")
    balance: float = Field(default=200.0, gt=0)
    entry_value: float | None = Field(default=None, gt=0)
    score: int = Field(default=90, ge=0, le=100)
    minimum_score: int = Field(default=80, ge=0, le=100)
    risk_approved: bool = Field(default=True)
    websocket_online: bool = Field(default=True)
    execution_ready: bool = Field(default=True)
    asset_valid: bool = Field(default=True)
    autotrade_requested: bool = Field(default=False)

    @model_validator(mode="after")
    def validate_entry_against_balance(self) -> "AutoTradeGateRequest":
        if self.entry_value is not None and self.entry_value > self.balance:
            raise ValueError("entry_value não pode ser maior que balance")
        return self


class AutoTradeGateResponse(BaseModel):
    """Resposta de segurança do AutoTrade Gate."""

    allowed: bool
    status: Literal["READY", "BLOCKED", "WAITING"]
    symbol: str
    timeframe: OperationalTimeframe | None
    account_type: AccountType
    currency: AccountCurrency
    currency_symbol: str
    balance: float
    entry_value: float
    minimum_entry: float
    score: int
    minimum_score: int
    can_analyze: bool
    autotrade_enabled: bool
    reasons: list[str]
    warnings: list[str]
    safety_rules: list[str]
    official_rule: str = "Primeiro proteger a banca. Depois crescer a banca."
    disclaimer: str = "AutoTrade liberado apenas em conta DEMO durante desenvolvimento."
