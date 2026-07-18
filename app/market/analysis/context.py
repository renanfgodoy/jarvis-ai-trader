from __future__ import annotations

from dataclasses import dataclass

from app.market.providers.base.models import ProviderAssets, ProviderContext, ProviderHistory, ProviderTick


@dataclass(frozen=True, slots=True)
class AnalysisContext:
    provider_context: ProviderContext
    history: ProviderHistory
    ticks: tuple[ProviderTick, ...] = ()
    assets: ProviderAssets | None = None
