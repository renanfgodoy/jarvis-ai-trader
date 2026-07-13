from __future__ import annotations


class ProviderError(Exception):
    error_code = "PROVIDER_ERROR"


class ProviderDisabledError(ProviderError):
    error_code = "PROVIDER_DISABLED"


class ProviderCredentialsMissingError(ProviderError):
    error_code = "PROVIDER_CREDENTIALS_MISSING"


class ProviderConnectionError(ProviderError):
    error_code = "PROVIDER_CONNECTION_FAILED"


class ProviderRequestError(ProviderError):
    error_code = "PROVIDER_REQUEST_FAILED"


class ProviderValidationError(ProviderError):
    error_code = "PROVIDER_VALIDATION_FAILED"
