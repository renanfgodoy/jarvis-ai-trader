from modules.trading.contracts import TradingMarket, TradingStrategy
from modules.trading.exceptions import TradingValidationException
from modules.trading.models import TradingRequest


SUPPORTED_MARKETS: tuple[TradingMarket, ...] = ("OTC", "Forex", "Crypto")
SUPPORTED_STRATEGIES: tuple[TradingStrategy, ...] = ("Trend", "Price Action", "Support Resistance", "SMC", "ICT")
SUPPORTED_TIMEFRAMES = ("M1", "M5", "M15", "H1")


class TradingValidator:
    def validate_request(self, request: TradingRequest) -> None:
        if request.market not in SUPPORTED_MARKETS:
            raise TradingValidationException(f"unsupported market: {request.market}")
        if not request.symbol.strip():
            raise TradingValidationException("symbol is required")
        if request.timeframe not in SUPPORTED_TIMEFRAMES:
            raise TradingValidationException(f"unsupported timeframe: {request.timeframe}")
        if request.strategy not in SUPPORTED_STRATEGIES:
            raise TradingValidationException(f"unsupported strategy: {request.strategy}")
        if not request.message.strip():
            raise TradingValidationException("message is required")
