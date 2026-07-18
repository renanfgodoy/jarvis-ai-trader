from sdk import ModuleRequest

from modules.trading.models import TradingRequest, TradingResponse
from modules.trading.services.decision_engine import DecisionEngine
from modules.trading.services.prompt_builder import PromptBuilder
from modules.trading.services.scenario_builder import ScenarioBuilder
from modules.trading.validators import TradingValidator


class TradingAnalyzer:
    def __init__(
        self,
        scenario_builder: ScenarioBuilder | None = None,
        prompt_builder: PromptBuilder | None = None,
        decision_engine: DecisionEngine | None = None,
        validator: TradingValidator | None = None,
    ) -> None:
        self.scenario_builder = scenario_builder or ScenarioBuilder()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.decision_engine = decision_engine or DecisionEngine()
        self.validator = validator or TradingValidator()

    def analyze(self, module, request: TradingRequest) -> TradingResponse:
        self.validator.validate_request(request)
        scenario = self.scenario_builder.build(request)
        prompt = self.prompt_builder.build(request, scenario)
        execution = module.run_sdk(
            ModuleRequest(
                module="trading",
                payload=prompt,
                identity=module.manifest().identity,
                provider=module.manifest().provider,
                language=module.manifest().language,
                metadata={
                    **dict(request.metadata),
                    "market": request.market,
                    "symbol": scenario.symbol,
                    "timeframe": request.timeframe,
                    "strategy": request.strategy,
                    "scenario_bias": scenario.bias,
                },
            )
        )
        return self.decision_engine.build_response(scenario, execution)
