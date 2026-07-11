class PolariumLiveSessionError(RuntimeError):
    """Base error for the authorized live session runtime foundation."""


class PolariumLiveSessionAuthorizationError(PolariumLiveSessionError):
    """Raised when no safe authorized session source is available."""


class PolariumLiveSessionStartError(PolariumLiveSessionError):
    """Raised when a configured live message source cannot start safely."""
