class PolariumMessageSourceError(RuntimeError):
    """Base error for Polarium live message source adapters."""


class AuthorizedSourceUnavailableError(PolariumMessageSourceError):
    """Raised when the authorized source cannot safely open a live connection."""
