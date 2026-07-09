from fastapi import APIRouter

from app.models.provider import (
    ProviderCurrentResponse,
    ProviderInfo,
    ProviderManagerItem,
    TradingViewWebhookPayload,
    TradingViewWebhookResponse,
)
from app.services.provider_engine import ProviderEngineService

router = APIRouter(prefix="/providers", tags=["Providers"])
manager_router = APIRouter(prefix="/providers", tags=["Provider Manager"])


@router.get("", response_model=list[ProviderInfo])
def list_providers() -> list[ProviderInfo]:
    """Lista provedores disponíveis no Provider Engine."""
    service = ProviderEngineService()
    return service.list_providers()


@router.post("/tradingview/webhook", response_model=TradingViewWebhookResponse)
def receive_tradingview_webhook(payload: TradingViewWebhookPayload) -> TradingViewWebhookResponse:
    """Recebe alerta do TradingView via webhook para análise posterior.

    Esta rota não executa ordens. Todo alerta recebido ainda deverá passar pelo
    AI Decision Engine e pelo Risk Manager antes de qualquer uso operacional.
    """
    service = ProviderEngineService()
    return service.receive_tradingview_webhook(payload)


@manager_router.get("/current", response_model=ProviderCurrentResponse)
def current_provider() -> ProviderCurrentResponse:
    """Retorna o provider de mercado ativo do J.A.R.V.I.S."""
    service = ProviderEngineService()
    return service.current_provider()


@manager_router.get("/list", response_model=list[ProviderManagerItem])
def list_provider_manager_items() -> list[ProviderManagerItem]:
    """Lista todos os providers registrados no Provider Manager."""
    service = ProviderEngineService()
    return service.list_provider_manager_items()
