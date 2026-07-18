from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionConfig:
    strict_validation: bool = True
    enable_hooks: bool = True
    enable_events: bool = True
    pipeline_version: str = "1.0"
    debug: bool = False
    trace_enabled: bool = True
    default_template_id: str = "core.generic_analysis"
    default_template_version: str = "1.0"
    default_language: str = "pt-BR"
    default_response_format: str = "text"
    default_provider_capabilities: tuple[str, ...] = ("chat",)
