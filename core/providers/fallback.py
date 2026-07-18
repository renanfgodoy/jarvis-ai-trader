from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FallbackPolicy:
    enabled: bool = False
    fallback_provider: str | None = None

    def next_provider(self, current_provider: str) -> str | None:
        if not self.enabled or not self.fallback_provider:
            return None
        if self.fallback_provider == current_provider:
            return None
        return self.fallback_provider
