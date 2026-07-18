from __future__ import annotations

from dataclasses import replace
from math import isfinite

from app.market.analysis.context import AnalysisContext
from app.market.analysis.exceptions import InvalidProviderData
from app.market.providers.base.models import ProviderCandle, ProviderTick


class MarketDataNormalizer:
    def normalize(self, context: AnalysisContext) -> AnalysisContext:
        provider = context.provider_context.provider
        if not provider:
            raise InvalidProviderData("provider is required")
        if context.history.provider != provider:
            raise InvalidProviderData("history provider does not match context provider")

        candles = tuple(sorted((self._normalize_candle(candle) for candle in context.history.candles), key=lambda item: item.timestamp))
        ticks = tuple(sorted((self._normalize_tick(tick) for tick in context.ticks), key=lambda item: item.timestamp))
        return replace(context, history=replace(context.history, candles=candles), ticks=ticks)

    def _normalize_candle(self, candle: ProviderCandle) -> ProviderCandle:
        values = (candle.open, candle.high, candle.low, candle.close)
        if not all(isfinite(value) for value in values):
            raise InvalidProviderData("candle contains non-finite price")
        if candle.high < candle.low:
            raise InvalidProviderData("candle high is lower than low")
        if candle.timestamp < 0:
            raise InvalidProviderData("candle timestamp is invalid")
        return candle

    def _normalize_tick(self, tick: ProviderTick) -> ProviderTick:
        if not isfinite(tick.price):
            raise InvalidProviderData("tick contains non-finite price")
        if tick.timestamp < 0:
            raise InvalidProviderData("tick timestamp is invalid")
        return tick
