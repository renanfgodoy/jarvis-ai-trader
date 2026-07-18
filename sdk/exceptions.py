class ModuleException(Exception):
    """Base exception for the Friday Module SDK."""


class ModuleValidationException(ModuleException):
    """Raised when a module SDK contract is invalid."""


class ModuleManifestException(ModuleValidationException):
    """Raised when a module manifest is invalid."""


class ModuleRegistryException(ModuleException):
    """Raised when module registry operations fail."""


class ModuleLoaderException(ModuleException):
    """Raised when a module cannot be loaded safely."""
