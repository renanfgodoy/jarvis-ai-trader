from __future__ import annotations

from dataclasses import dataclass

from app.market.chart.models import ChartCandle, ChartSeries, ChartSeriesSummary
from app.market.providers.base import MarketProvider, ProviderCandle, ProviderHistory, ProviderUnsupportedOperation
from app.market.providers.manager import ProviderManager


@dataclass(frozen=True, slots=True)
class ProviderChartReadiness:
    state: str
    history_count: int
    required_history_count: int
    analysis_blocked: bool
    reason: str | None


@dataclass(frozen=True, slots=True)
class ProviderChartSeries:
    provider: str
    symbol: str
    period: int
    timeframe: str
    readiness: ProviderChartReadiness
    candles: tuple[ChartCandle, ...]


@dataclass(frozen=True, slots=True)
class ProviderChartSeriesSummary:
    provider: str
    symbol: str
    period: int
    timeframe: str
    count: int
    latest_time: int | None
    readiness: str


class ChartProviderService:
    def __init__(self, provider_manager: ProviderManager) -> None:
        self._provider_manager = provider_manager

    def get_series(
        self,
        *,
        provider_name: str | None,
        symbol: str | None,
        period: int | None,
        limit: int,
    ) -> ProviderChartSeries:
        provider = self._provider_manager.get_provider(provider_name)
        context = provider.get_context()
        resolved_symbol = symbol or context.symbol or context.asset
        resolved_period = period or context.period
        if not resolved_symbol or resolved_period is None:
            raise ProviderUnsupportedOperation("provider context does not expose a complete chart series")
        history = provider.get_history(resolved_symbol, resolved_period, limit)
        readiness = provider.get_readiness(resolved_symbol, resolved_period)
        return ProviderChartSeries(
            provider=history.provider,
            symbol=history.symbol,
            period=history.period,
            timeframe=_period_to_timeframe(history.period),
            readiness=ProviderChartReadiness(
                state=readiness.state,
                history_count=readiness.history_count,
                required_history_count=readiness.required_history_count,
                analysis_blocked=readiness.analysis_blocked,
                reason=readiness.reason,
            ),
            candles=tuple(_provider_candle_to_chart_candle(candle) for candle in history.candles),
        )

    def get_available_series(self, *, provider_name: str | None = None) -> tuple[ProviderChartSeriesSummary, ...]:
        provider = self._provider_manager.get_provider(provider_name)
        summaries: list[ProviderChartSeriesSummary] = []
        context = provider.get_context()
        if context.symbol and context.period is not None:
            summaries.append(self._summary_for(provider, context.symbol, context.period))
        try:
            for asset in provider.get_assets().assets:
                for period in asset.supported_periods:
                    if context.symbol == asset.symbol and context.period == period:
                        continue
                    summaries.append(self._summary_for(provider, asset.symbol, period))
        except ProviderUnsupportedOperation:
            pass
        return tuple(_deduplicate_summaries(summaries))

    def to_legacy_chart_series(self, provider_series: ProviderChartSeries) -> ChartSeries:
        return ChartSeries(
            provider=provider_series.provider,
            active_id=None,
            symbol=provider_series.symbol,
            raw_size=provider_series.period,
            candles=provider_series.candles,
        )

    def _summary_for(self, provider: MarketProvider, symbol: str, period: int) -> ProviderChartSeriesSummary:
        try:
            history: ProviderHistory = provider.get_history(symbol, period, None)
            count = len(history.candles)
            latest_time = history.timestamp
        except ProviderUnsupportedOperation:
            count = 0
            latest_time = None
        readiness = provider.get_readiness(symbol, period)
        return ProviderChartSeriesSummary(
            provider=provider.provider_name(),
            symbol=symbol,
            period=period,
            timeframe=_period_to_timeframe(period),
            count=count,
            latest_time=latest_time,
            readiness=readiness.state,
        )


def _provider_candle_to_chart_candle(candle: ProviderCandle) -> ChartCandle:
    return ChartCandle(
        time=int(candle.timestamp),
        open=candle.open,
        high=candle.high,
        low=candle.low,
        close=candle.close,
    )


def _period_to_timeframe(period: int) -> str:
    if period == 60:
        return "M1"
    if period == 300:
        return "M5"
    if period == 900:
        return "M15"
    return f"{period}s"


def _deduplicate_summaries(summaries: list[ProviderChartSeriesSummary]) -> list[ProviderChartSeriesSummary]:
    seen: set[tuple[str, str, int]] = set()
    result: list[ProviderChartSeriesSummary] = []
    for summary in summaries:
        key = (summary.provider, summary.symbol, summary.period)
        if key in seen:
            continue
        seen.add(key)
        result.append(summary)
    return result
