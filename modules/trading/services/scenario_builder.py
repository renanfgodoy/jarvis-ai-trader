from modules.trading.models import TradingRequest, TradingScenario


class ScenarioBuilder:
    def build(self, request: TradingRequest) -> TradingScenario:
        symbol = request.symbol.strip().upper()
        bias = self._bias_for(symbol=symbol, market=request.market, strategy=request.strategy)
        risk = "HIGH" if request.market == "Crypto" else "MEDIUM" if request.timeframe == "M1" else "LOW"
        context = f"{request.market} {symbol} {request.timeframe} using {request.strategy}"
        return TradingScenario(
            market=request.market,
            symbol=symbol,
            timeframe=request.timeframe,
            strategy=request.strategy,
            bias=bias,
            context=context,
            risk=risk,
        )

    def _bias_for(self, *, symbol: str, market: str, strategy: str) -> str:
        if "BTC" in symbol or market == "Crypto":
            return "volatile consolidation"
        if strategy == "Support Resistance" or "XAU" in symbol:
            return "near resistance"
        if strategy == "Trend" and ("EUR" in symbol or market == "OTC"):
            return "bullish continuation watch"
        if strategy in {"SMC", "ICT"}:
            return "liquidity sweep watch"
        return "neutral price action"
