from modules.trading.models import TradingRequest, TradingScenario


class PromptBuilder:
    def build(self, request: TradingRequest, scenario: TradingScenario) -> str:
        prompt_name = self.select_prompt(request.market)
        return (
            f"Prompt: {prompt_name}\n"
            f"Market: {scenario.market}\n"
            f"Symbol: {scenario.symbol}\n"
            f"Timeframe: {scenario.timeframe}\n"
            f"Strategy: {scenario.strategy}\n"
            f"Scenario: {scenario.context}\n"
            f"Bias: {scenario.bias}\n"
            f"User message: {request.message}"
        )

    def select_prompt(self, market: str) -> str:
        if market == "OTC":
            return "otc.md"
        if market == "Forex":
            return "forex.md"
        if market == "Crypto":
            return "crypto.md"
        return "default.md"
