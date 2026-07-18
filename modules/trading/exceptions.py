class TradingModuleException(Exception):
    """Base exception for the Trading Module."""


class TradingValidationException(TradingModuleException):
    """Raised when a trading request is invalid."""
