class IdentityEngineError(Exception):
    """Base error for Identity Engine failures."""


class InvalidIdentityProfileError(IdentityEngineError):
    """Raised when an identity profile is structurally invalid."""


class InvalidIdentityRequestError(IdentityEngineError):
    """Raised when an identity request is structurally invalid."""


class IdentityNotFoundError(IdentityEngineError):
    """Raised when an identity id is not registered."""


class IdentityVersionNotFoundError(IdentityEngineError):
    """Raised when an identity version is not registered."""


class DuplicateIdentityError(IdentityEngineError):
    """Raised when an identity id and version are registered twice."""


class IdentityBuildError(IdentityEngineError):
    """Raised when an identity result cannot be built."""
