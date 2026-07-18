from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModuleManifest:
    name: str
    display_name: str
    description: str
    version: str = "1.0"
    identity: str = "jarvis.default"
    provider: str = "mock"
    language: str = "pt-BR"
    permissions: tuple[str, ...] = ()
    core_version: str = "1.0"
    enabled: bool = True
    metadata: dict[str, str] = field(default_factory=dict)
