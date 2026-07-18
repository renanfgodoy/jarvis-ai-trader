from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IdentityConfig:
    default_identity: str = "jarvis.default"
    default_language: str = "pt-BR"
    default_version: str = "1.0"
    supported_languages: tuple[str, ...] = ("pt-BR", "en-US", "es-ES")
    supported_modules: tuple[str, ...] = (
        "trading",
        "finance",
        "marketing",
        "seo",
        "documents",
        "automation",
        "sites",
        "crm",
    )
    strict_validation: bool = True
    future_provider_support: bool = True
