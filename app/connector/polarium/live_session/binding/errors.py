from __future__ import annotations

SESSION_NOT_AVAILABLE = "SESSION_NOT_AVAILABLE"
SESSION_NOT_AUTHORIZED = "SESSION_NOT_AUTHORIZED"
SESSION_EXPIRED = "SESSION_EXPIRED"
INVALID_SESSION_HANDLE = "INVALID_SESSION_HANDLE"
UNSUPPORTED_SESSION = "UNSUPPORTED_SESSION"
BINDING_FAILED = "BINDING_FAILED"


class AuthorizedSessionBindingError(RuntimeError):
    """Base error for sanitized authorized session binding failures."""

    def __init__(self, code: str, reason: str) -> None:
        super().__init__(code)
        self.code = code
        self.reason = reason

    def sanitized(self) -> dict[str, str]:
        return {"code": self.code, "reason": self.reason}


class SessionNotAvailableError(AuthorizedSessionBindingError):
    def __init__(self, reason: str = "AUTHORIZED_SESSION_UNAVAILABLE") -> None:
        super().__init__(SESSION_NOT_AVAILABLE, reason)


class SessionNotAuthorizedError(AuthorizedSessionBindingError):
    def __init__(self, reason: str = "AUTHORIZED_SESSION_UNAVAILABLE") -> None:
        super().__init__(SESSION_NOT_AUTHORIZED, reason)


class SessionExpiredError(AuthorizedSessionBindingError):
    def __init__(self, reason: str = "AUTHORIZED_SESSION_EXPIRED") -> None:
        super().__init__(SESSION_EXPIRED, reason)


class InvalidSessionHandleError(AuthorizedSessionBindingError):
    def __init__(self, reason: str = "INVALID_SESSION_HANDLE") -> None:
        super().__init__(INVALID_SESSION_HANDLE, reason)


class UnsupportedSessionError(AuthorizedSessionBindingError):
    def __init__(self, reason: str = "UNSUPPORTED_SESSION") -> None:
        super().__init__(UNSUPPORTED_SESSION, reason)


class BindingFailedError(AuthorizedSessionBindingError):
    def __init__(self, reason: str = "BINDING_FAILED") -> None:
        super().__init__(BINDING_FAILED, reason)
