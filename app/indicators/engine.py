from __future__ import annotations

from app.indicators.errors import IndicatorEngineError, IndicatorInputError
from app.indicators.models import IndicatorRequest, IndicatorResult
from app.indicators.registry import IndicatorRegistry
from app.market.store import CandleStore


class IndicatorEngine:
    """Passive engine that runs registered indicators against Candle Store data."""

    def __init__(self, candle_store: CandleStore, registry: IndicatorRegistry | None = None) -> None:
        self.candle_store = candle_store
        self.registry = registry or IndicatorRegistry()

    def run(self, request: IndicatorRequest) -> IndicatorResult:
        try:
            _validate_request(request)
            indicator = self.registry.get(request.name)
            candles = self.candle_store.latest(
                active_id=request.active_id,
                raw_size=request.raw_size,
                limit=request.limit,
            )
            if len(candles) < indicator.min_candles:
                raise IndicatorInputError(
                    f"Indicator {indicator.name} requires {indicator.min_candles} candle(s); got {len(candles)}."
                )
            value = indicator.calculate(candles=candles, parameters=request.parameters)
        except IndicatorEngineError as exc:
            return IndicatorResult(
                success=False,
                request=request,
                candles_used=0,
                value=None,
                errors=(str(exc),),
            )

        return IndicatorResult(
            success=True,
            request=request,
            candles_used=len(candles),
            value=value,
            errors=(),
        )


def _validate_request(request: IndicatorRequest) -> None:
    if not request.name.strip():
        raise IndicatorInputError("Indicator name is required.")
    if request.limit <= 0:
        raise IndicatorInputError("Indicator request limit must be greater than zero.")
