from fastapi import APIRouter

from app.models.quadcode import (
    QuadcodeConnectionResponse,
    QuadcodeDemoConnectRequest,
    QuadcodeDemoOrderRequest,
    QuadcodeDemoOrderResponse,
    QuadcodeSymbolsResponse,
)
from app.providers.quadcode import QuadcodePolariumProvider

router = APIRouter(prefix="/quadcode", tags=["Quadcode / Polarium Demo"])
_quadcode_provider = QuadcodePolariumProvider()


@router.get("/status", response_model=QuadcodeConnectionResponse)
def quadcode_status() -> QuadcodeConnectionResponse:
    """Retorna o estado seguro do adapter Quadcode/Polarium.

    Esta rota não autentica, não captura credenciais e não executa ordens.
    """
    health = _quadcode_provider.health()
    return QuadcodeConnectionResponse(
        mode="DEMO",
        status="CONNECTED" if health.get("connected") else "READY",
        connected=bool(health.get("connected")),
        dry_run=True,
        accountType="DEMO_ONLY",
        canTrade=False,
        message=str(health.get("message")),
        safetyRules=[
            "Desenvolvimento somente em conta DEMO",
            "Ordens reais bloqueadas",
            "Toda execução futura deve passar pelo Risk Manager",
        ],
    )


@router.post("/demo/connect", response_model=QuadcodeConnectionResponse)
def connect_demo(request: QuadcodeDemoConnectRequest) -> QuadcodeConnectionResponse:
    """Prepara o adapter Quadcode/Polarium em modo DEMO/DRY_RUN."""
    return _quadcode_provider.connect(request)


@router.post("/demo/disconnect", response_model=QuadcodeConnectionResponse)
def disconnect_demo() -> QuadcodeConnectionResponse:
    """Desconecta o adapter do modo DEMO/DRY_RUN."""
    return _quadcode_provider.disconnect()


@router.get("/symbols", response_model=QuadcodeSymbolsResponse)
def list_quadcode_symbols() -> QuadcodeSymbolsResponse:
    """Lista o universo inicial de ativos OTC para discovery da Polarium/Quadcode."""
    return _quadcode_provider.get_symbol_catalog()


@router.post("/demo/order", response_model=QuadcodeDemoOrderResponse)
def dry_run_order(request: QuadcodeDemoOrderRequest) -> QuadcodeDemoOrderResponse:
    """Recebe uma ordem DEMO em DRY_RUN sem enviar nada para a Polarium."""
    return _quadcode_provider.dry_run_order(request)
