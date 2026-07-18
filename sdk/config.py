from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleConfig:
    enabled: bool = True
    debug: bool = False
    strict_validation: bool = True
    auto_register: bool = False
    auto_initialize: bool = False
