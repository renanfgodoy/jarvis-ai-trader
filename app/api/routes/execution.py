from fastapi import APIRouter

from app.execution.demo_executor import DemoExecutionService
from app.models.account import AutoTradeGateRequest, AutoTradeGateResponse
from app.models.execution import ExecutionRequest, ExecutionResponse, ExecutionStatusResponse
from app.services.autotrade_gate import AutoTradeGateService

router = APIRouter(prefix="/execution", tags=["Execution Engine"])


@router.get("/status", response_model=ExecutionStatusResponse)
def execution_status() -> ExecutionStatusResponse:
    """Mostra o status seguro do Execution Engine."""
    return DemoExecutionService().status()


@router.post("/demo/run", response_model=ExecutionResponse)
def run_demo_execution(request: ExecutionRequest) -> ExecutionResponse:
    """Simula uma execução em conta demo após validação do Risk Manager.

    Esta rota não envia ordens reais. Ela prepara a arquitetura do Executor para
    integrações futuras com Polarium/Quadcode em ambiente demo autorizado.
    """
    return DemoExecutionService().run(request)


@router.post("/autotrade/gate", response_model=AutoTradeGateResponse)
def check_autotrade_gate(request: AutoTradeGateRequest) -> AutoTradeGateResponse:
    """Valida se AutoTrade pode analisar, sinalizar e operar em modo DEMO."""
    return AutoTradeGateService().check(request)
