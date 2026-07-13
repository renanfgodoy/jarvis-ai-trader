from __future__ import annotations


class IQOptionWorkerError(Exception):
    error_code = "IQ_OPTION_WORKER_ERROR"


class IQOptionWorkerTimeout(IQOptionWorkerError):
    error_code = "IQ_OPTION_WORKER_TIMEOUT"


class IQOptionWorkerInvalidJSON(IQOptionWorkerError):
    error_code = "IQ_OPTION_WORKER_INVALID_JSON"


class IQOptionWorkerRejectedCommand(IQOptionWorkerError):
    error_code = "IQ_OPTION_WORKER_REJECTED_COMMAND"


class IQOptionWorkerFailed(IQOptionWorkerError):
    def __init__(self, error_code: str) -> None:
        self.error_code = error_code
        super().__init__(error_code)
