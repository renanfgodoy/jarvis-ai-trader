from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

AccountCurrency = Literal["BRL", "USD"]
AccountMode = Literal["DEMO", "REAL"]
ConnectionStatus = Literal["CONNECTED", "DISCONNECTED", "BLOCKED"]
AccountDataSource = Literal["REAL_SESSION", "DEVTOOLS_PAYLOAD", "SIMULATED", "CACHE", "UNAVAILABLE"]
SyncStatus = Literal["SYNCED", "NOT_SYNCED", "FAILED", "CACHE_ONLY"]


class PolariumLoginRequest(BaseModel):
    """Credenciais usadas apenas para iniciar uma sessão local segura.

    Importante: a senha nunca deve ser persistida em cache. Quando a integração
    real estiver disponível, o adapter trocará estas credenciais por um token de
    sessão autorizado pela Polarium/Quadcode.
    """

    email: str = Field(min_length=5, max_length=160)
    password: str = Field(min_length=4, max_length=128)
    force_demo: bool = True
    remember_session: bool = True


class PolariumAccountState(BaseModel):
    connected: bool = False
    status: ConnectionStatus = "DISCONNECTED"
    account_mode: AccountMode = "DEMO"
    currency: AccountCurrency | None = None
    currency_symbol: str | None = None
    balance: float | None = None
    minimum_entry: float | None = None
    demo_only: bool = True
    email_masked: str | None = None
    session_cached: bool = False
    session_id: str | None = None
    provider: str = "POLARIUM_DEMO_CONNECTOR"
    data_source: AccountDataSource = "UNAVAILABLE"
    sync_status: SyncStatus = "NOT_SYNCED"
    is_balance_synced: bool = False
    last_sync: datetime | None = None
    last_sync_error: str | None = None
    warnings: list[str] = []
    safety_rules: list[str] = []
    account_id: int | None = None
    user_id: int | None = None
    available: float | None = None
    equity: float | None = None
    can_autotrade: bool = False
    autotrade_block_reason: str | None = None
    last_event_name: str | None = None
    raw_summary: dict = {}


class PolariumLoginResponse(BaseModel):
    success: bool
    message: str
    account: PolariumAccountState


class PolariumSyncResponse(BaseModel):
    success: bool
    message: str
    account: PolariumAccountState


class PolariumLogoutResponse(BaseModel):
    success: bool
    message: str


class PolariumWsDebugRequest(BaseModel):
    """Payload JSON copiado do DevTools/Network/WebSocket da sessão do usuário.

    Uso seguro: esta rota não autentica, não conecta em serviços externos e não envia ordens.
    Ela só interpreta mensagens que o operador forneceu manualmente para validar parser.
    """

    payload: dict
    force_demo: bool = True


class PolariumWsDebugResponse(BaseModel):
    accepted: bool
    message: str
    account: PolariumAccountState
