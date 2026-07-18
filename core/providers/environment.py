from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderEnvironment:
    name: str = "development"
    debug: bool = True
    external_providers_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("provider environment name is required")

    @property
    def normalized_name(self) -> str:
        return self.name.strip().lower()

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.normalized_name,
            "debug": self.debug,
            "external_providers_allowed": self.external_providers_allowed,
        }
