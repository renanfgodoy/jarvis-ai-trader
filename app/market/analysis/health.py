from __future__ import annotations

from app.market.analysis.context import AnalysisContext
from app.market.analysis.models import MarketHealth, MarketState


class MarketHealthEvaluator:
    def evaluate(self, context: AnalysisContext) -> MarketHealth:
        warnings: list[str] = []
        errors: list[str] = []
        total_candles = len(context.history.candles)
        total_ticks = len(context.ticks)

        if context.provider_context.connection_state == "error":
            errors.append("PROVIDER_ERROR")
        if total_candles == 0:
            warnings.append("NO_CANDLES")
        if total_ticks == 0:
            warnings.append("NO_TICKS")

        history_ready = context.provider_context.history_state.upper() == "READY" or total_candles >= context.provider_context.history_count > 0
        tick_ready = total_ticks > 0

        if errors:
            status: MarketState = "ERROR"
            quality_score = 0.0
        elif total_candles == 0 and total_ticks == 0:
            status = "EMPTY"
            quality_score = 0.0
        elif not history_ready:
            status = "LIMITED"
            quality_score = 0.45 if total_candles else 0.2
        elif context.provider_context.history_state.upper() == "BOOTSTRAPPING":
            status = "BOOTSTRAPPING"
            quality_score = 0.35
        else:
            status = "READY"
            quality_score = 1.0 if tick_ready else 0.85

        return MarketHealth(
            status=status,
            warnings=tuple(warnings),
            errors=tuple(errors),
            quality_score=quality_score,
            history_ready=history_ready,
            tick_ready=tick_ready,
        )
