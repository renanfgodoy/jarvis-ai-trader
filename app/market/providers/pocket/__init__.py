"""Pocket Option read-only provider architecture.

This package is intentionally isolated from the main Friday runtime. It only
supports fake/replay transports in this sprint.
"""

from app.market.providers.pocket.adapter import (
    FakePocketProviderAdapter,
    PocketProviderAdapter,
    build_pocket_provider_adapter,
)
from app.market.providers.pocket.builders import FakePocketProviderBuilder, PocketProviderBuilder
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.runtime import PocketMarketRuntime

__all__ = [
    "FakePocketProviderAdapter",
    "FakePocketProviderBuilder",
    "PocketMarketRuntime",
    "PocketProviderAdapter",
    "PocketProviderBuilder",
    "PocketProviderConfig",
    "build_pocket_provider_adapter",
]
