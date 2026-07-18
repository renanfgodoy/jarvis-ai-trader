from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    enabled: bool = False
    max_attempts: int = 1
    interval_seconds: float = 0.0
    recoverable_errors: tuple[type[Exception], ...] = (TimeoutError,)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        if not self.enabled:
            return False
        if attempt >= self.max_attempts:
            return False
        return isinstance(error, self.recoverable_errors)
