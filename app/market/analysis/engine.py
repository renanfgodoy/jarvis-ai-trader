from __future__ import annotations

from datetime import datetime, timezone

from app.market.analysis.context import AnalysisContext
from app.market.analysis.health import MarketHealthEvaluator
from app.market.analysis.models import MarketAnalysis, MarketMetadata, MarketSnapshot
from app.market.analysis.normalizer import MarketDataNormalizer
from app.market.analysis.statistics import MarketStatisticsBuilder


class MarketAnalysisEngine:
    analysis_version = "ai-market-analysis-v1"

    def __init__(
        self,
        *,
        normalizer: MarketDataNormalizer | None = None,
        statistics_builder: MarketStatisticsBuilder | None = None,
        health_evaluator: MarketHealthEvaluator | None = None,
    ) -> None:
        self.normalizer = normalizer or MarketDataNormalizer()
        self.statistics_builder = statistics_builder or MarketStatisticsBuilder()
        self.health_evaluator = health_evaluator or MarketHealthEvaluator()

    def analyze(self, context: AnalysisContext) -> MarketAnalysis:
        normalized = self.normalizer.normalize(context)
        statistics = self.build_statistics(normalized)
        snapshot = self.build_snapshot(normalized)
        health = self.build_health(normalized)
        metadata = self.build_metadata(normalized)
        provider_context = normalized.provider_context
        market_type = provider_context.metadata.get("market_type")

        return MarketAnalysis(
            provider=provider_context.provider,
            symbol=normalized.history.symbol,
            asset=provider_context.asset,
            market_type=str(market_type) if market_type is not None else None,
            timeframe=provider_context.timeframe,
            period=normalized.history.period,
            candles=normalized.history.candles,
            ticks=normalized.ticks,
            snapshot=snapshot,
            statistics=statistics,
            metadata=metadata,
            health=health,
            created_at=metadata.generated_at,
            analysis_version=self.analysis_version,
        )

    def build_snapshot(self, context: AnalysisContext) -> MarketSnapshot:
        candle = context.history.candles[-1] if context.history.candles else None
        tick = context.ticks[-1] if context.ticks else None
        current_price = tick.price if tick is not None else candle.close if candle is not None else context.provider_context.last_price

        return MarketSnapshot(
            current_price=current_price,
            last_open=candle.open if candle is not None else None,
            last_close=candle.close if candle is not None else None,
            last_high=candle.high if candle is not None else None,
            last_low=candle.low if candle is not None else None,
            last_volume=candle.volume if candle is not None else None,
        )

    def build_statistics(self, context: AnalysisContext):
        return self.statistics_builder.build(context.history.candles, context.ticks)

    def build_health(self, context: AnalysisContext):
        return self.health_evaluator.evaluate(context)

    def build_metadata(self, context: AnalysisContext) -> MarketMetadata:
        generated_at = int(datetime.now(timezone.utc).timestamp())
        provider_version = context.provider_context.metadata.get("provider_version")
        return MarketMetadata(
            provider_name=context.provider_context.provider,
            provider_version=str(provider_version) if provider_version is not None else None,
            analysis_engine_version=self.analysis_version,
            generated_at=generated_at,
            timezone="UTC",
        )
