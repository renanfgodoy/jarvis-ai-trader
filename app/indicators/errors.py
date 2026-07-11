from __future__ import annotations


class IndicatorEngineError(Exception):
    """Base error for passive indicator engine failures."""


class IndicatorAlreadyRegisteredError(IndicatorEngineError):
    """Raised when an indicator name is registered twice."""


class IndicatorNotFoundError(IndicatorEngineError):
    """Raised when an indicator is not present in the registry."""


class IndicatorInputError(IndicatorEngineError):
    """Raised when a request cannot be executed with the available candles."""
