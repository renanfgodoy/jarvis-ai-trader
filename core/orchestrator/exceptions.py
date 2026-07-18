class ExecutionException(Exception):
    """Base error for Core Orchestrator failures."""


class PipelineException(ExecutionException):
    """Raised when the execution pipeline cannot proceed."""


class ValidationException(ExecutionException):
    """Raised when execution input or context is invalid."""


class StageException(ExecutionException):
    """Raised when a pipeline stage fails."""


class ConfigurationException(ExecutionException):
    """Raised when orchestrator configuration is invalid."""
