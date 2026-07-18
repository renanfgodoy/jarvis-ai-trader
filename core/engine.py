from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineDescriptor:
    name: str
    responsibility: str


class CoreEngine:
    name = "core"
    responsibility = "Orchestrates modules and providers through stable contracts."

    def describe(self) -> str:
        return self.responsibility

