from sdk.models import ModuleResponse

from modules.trading.models import TradingResponse, TradingScenario


class DecisionEngine:
    def build_response(self, scenario: TradingScenario, execution: ModuleResponse) -> TradingResponse:
        decision = "OBSERVE"
        confidence = 62
        support = "Zona anterior relevante"
        resistance = "Zona superior próxima"

        if scenario.bias == "bullish continuation watch":
            trend = "BULLISH"
            confidence = 72
            decision = "OBSERVE"
            support = "Pullback curto"
            resistance = "Topo recente"
        elif scenario.bias == "near resistance":
            trend = "SIDEWAYS"
            confidence = 68
            decision = "WAIT"
            support = "Base da consolidação"
            resistance = "Resistência próxima"
        elif scenario.bias == "volatile consolidation":
            trend = "CHOPPY"
            confidence = 55
            decision = "DO_NOT_TRADE"
            support = "Faixa inferior"
            resistance = "Faixa superior"
        elif scenario.bias == "liquidity sweep watch":
            trend = "UNCLEAR"
            confidence = 58
            decision = "WAIT"
            support = "Liquidez inferior"
            resistance = "Liquidez superior"
        else:
            trend = "NEUTRAL"

        analysis = (
            f"Mock inteligente: {scenario.context}. "
            f"Leitura conservadora baseada em market, symbol, timeframe e strategy. "
            "Nenhuma cotação real, corretora ou IA externa foi utilizada."
        )

        return TradingResponse(
            status=execution.status,
            trend=trend,
            support=support,
            resistance=resistance,
            decision=decision,
            confidence=confidence,
            risk=scenario.risk,
            analysis=analysis,
            execution=execution,
            metadata={
                **dict(execution.metadata),
                "scenario": scenario.context,
                "scenario_bias": scenario.bias,
                "intelligent_mock": True,
            },
        )
