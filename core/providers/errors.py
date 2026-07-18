class ProviderEngineError(Exception):
    """Base error for Provider Engine failures."""


class ProviderNotFoundError(ProviderEngineError, KeyError):
    """Raised when a provider is not registered."""


class DuplicateProviderError(ProviderEngineError, ValueError):
    """Raised when a provider or builder is registered twice."""


class InvalidProviderError(ProviderEngineError):
    """Raised when a provider does not implement the required contract."""


class ProviderCapabilityError(ProviderEngineError):
    """Raised when a provider lacks a required capability."""


class InvalidProviderConfigError(ProviderEngineError):
    """Raised when provider configuration is invalid."""


class InvalidProviderResponseError(ProviderEngineError):
    """Raised when a provider response is structurally invalid."""


class ProviderInvocationError(ProviderEngineError):
    """Raised when provider invocation fails."""
