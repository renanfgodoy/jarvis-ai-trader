from fastapi import APIRouter

from app.models.polarium import (
    PolariumAccountState,
    PolariumLoginRequest,
    PolariumLoginResponse,
    PolariumLogoutResponse,
    PolariumSyncResponse,
    PolariumWsDebugRequest,
    PolariumWsDebugResponse,
)
from app.connector.polarium.session.connector import PolariumConnectorService

router = APIRouter(prefix="/polarium", tags=["Polarium Connector"])


@router.get("/status", response_model=PolariumAccountState)
def polarium_status() -> PolariumAccountState:
    """Lê a sessão cacheada da Polarium sem inventar saldo."""
    return PolariumConnectorService().status()


@router.post("/login", response_model=PolariumLoginResponse)
def polarium_login(payload: PolariumLoginRequest) -> PolariumLoginResponse:
    """Cria uma sessão segura em cache local sem salvar senha.

    V0.18.1 não exibe saldo fake. O saldo só aparece como sincronizado quando
    vier de uma sessão real autorizada.
    """
    return PolariumConnectorService().login(payload)


@router.post("/sync", response_model=PolariumSyncResponse)
def polarium_sync() -> PolariumSyncResponse:
    """Tenta sincronizar saldo/moeda reais da conta DEMO.

    Enquanto o adapter autorizado não estiver configurado, retorna falha segura
    e mantém AutoTrade bloqueado.
    """
    return PolariumConnectorService().sync_account()


@router.post("/logout", response_model=PolariumLogoutResponse)
def polarium_logout() -> PolariumLogoutResponse:
    """Remove a sessão cacheada da Polarium."""
    return PolariumConnectorService().logout()


@router.get("/account/state", response_model=PolariumAccountState)
def polarium_account_state() -> PolariumAccountState:
    """Retorna o estado atual da conta, incluindo saldo sincronizado por payload real quando existir."""
    return PolariumConnectorService().status()


@router.post("/debug/ws-message", response_model=PolariumWsDebugResponse)
def polarium_debug_ws_message(payload: PolariumWsDebugRequest) -> PolariumWsDebugResponse:
    """Processa uma mensagem copiada do DevTools/WebSocket da Polarium.

    Segurança: esta rota não conecta no WebSocket externo, não autentica fora do app
    e não envia ordem. Serve para validar o parser do payload real.
    """
    account = PolariumConnectorService().ingest_ws_message(payload.payload, force_demo=payload.force_demo)
    return PolariumWsDebugResponse(
        accepted=account.is_balance_synced or account.last_event_name == "subscription-balance-changed",
        message="Payload processado e conta atualizada." if account.is_balance_synced else (account.autotrade_block_reason or "Payload processado."),
        account=account,
    )
