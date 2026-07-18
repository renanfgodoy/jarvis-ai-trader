class PromptEngineError(Exception):
    """Base error for Prompt Engine failures."""


class InvalidPromptRequestError(PromptEngineError):
    """Raised when a prompt request is structurally invalid."""


class PromptTemplateNotFoundError(PromptEngineError):
    """Raised when a template id is not registered."""


class PromptTemplateVersionNotFoundError(PromptEngineError):
    """Raised when a template version is not registered."""


class DuplicatePromptTemplateError(PromptEngineError):
    """Raised when a template id and version are registered twice."""


class InvalidPromptMessageError(PromptEngineError):
    """Raised when a prompt message has an invalid role or content."""


class PromptSizeLimitExceededError(PromptEngineError):
    """Raised when prompt input or output exceeds configured limits."""


class PromptBuildError(PromptEngineError):
    """Raised when a template cannot build a prompt package."""
