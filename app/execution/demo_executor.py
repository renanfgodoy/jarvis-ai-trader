from app.models.execution import ExecutionRequest, ExecutionResponse, ExecutionStatusResponse
from app.models.risk import RiskCheckRequest
from app.services.risk_manager import RiskManagerService


class DemoExecutionService:
    """Executor seguro para validar operações em modo DEMO/DRY_RUN.

    Esta classe não clica na corretora e não envia ordens reais. Ela prepara a
    arquitetura do Execution Engine para que futuras integrações sejam adicionadas
    com proteção de banca e validação do Risk Manager.
    """

    provider_name = "Polarium Demo Adapter"
    account_type = "DEMO"

    def status(self) -> ExecutionStatusResponse:
        """Retorna o status seguro da camada de execução."""
        return ExecutionStatusResponse(
            status="READY",
            provider=self.provider_name,
            account_type=self.account_type,
            live_trading_enabled=False,
            demo_only=True,
            supported_modes=["DEMO", "DRY_RUN"],
            safety_rules=self._safety_rules(),
        )

    def run(self, request: ExecutionRequest) -> ExecutionResponse:
        """Simula uma execução após aprovação do Risk Manager."""
        risk_request = RiskCheckRequest(
            bankroll=request.bankroll,
            entry_value=request.entry_value,
            daily_wins=request.daily_wins,
            daily_losses=request.daily_losses,
            gale_used=request.gale_used,
            payout=request.payout,
        )
        risk = RiskManagerService().check(risk_request)
        entry_value = round(request.entry_value if request.entry_value is not None else risk.recommended_entry, 2)

        if not risk.allowed:
            return ExecutionResponse(
                status="BLOCKED",
                allowed=False,
                mode=request.mode,
                provider=self.provider_name,
                account_type=self.account_type,
                symbol=request.symbol,
                timeframe=request.timeframe,
                signal=request.signal,
                entry_value=entry_value,
                expiration_minutes=request.expiration_minutes,
                risk_score=risk.risk_score,
                risk_decision=risk.decision,
                action="NO_EXECUTION",
                result=None,
                reasons=risk.reasons,
                warnings=risk.warnings,
                safety_rules=self._safety_rules(),
            )

        return ExecutionResponse(
            status="SIMULATED",
            allowed=True,
            mode=request.mode,
            provider=self.provider_name,
            account_type=self.account_type,
            symbol=request.symbol,
            timeframe=request.timeframe,
            signal=request.signal,
            entry_value=entry_value,
            expiration_minutes=request.expiration_minutes,
            risk_score=risk.risk_score,
            risk_decision=risk.decision,
            action=f"SIMULATED_{request.signal}_ORDER",
            result="PENDING_DEMO_RESULT",
            reasons=["Risk Manager aprovou a operação para simulação em conta demo."],
            warnings=risk.warnings,
            safety_rules=self._safety_rules(),
        )

    @staticmethod
    def _safety_rules() -> list[str]:
        return [
            "Conta real bloqueada durante desenvolvimento.",
            "Somente DEMO ou DRY_RUN são permitidos nesta fase.",
            "Nenhuma ordem real é enviada pela Sprint 7.",
            "Toda execução precisa passar pelo Risk Manager.",
            "Stop diário e limite de entrada continuam obrigatórios.",
        ]
