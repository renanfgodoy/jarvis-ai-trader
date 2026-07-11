from __future__ import annotations

from typing import Any

from app.market.pipeline.models import PipelineResult
from app.market.pipeline.processor import MarketPipelineProcessor
from app.market.store import CandleStore


class MarketPipeline:
    """Tiny facade for passive market message processing."""

    def __init__(self, candle_store: CandleStore | None = None) -> None:
        self.processor = MarketPipelineProcessor(candle_store=candle_store)

    @property
    def candle_store(self) -> CandleStore:
        return self.processor.candle_store

    def process(self, message: dict[str, Any]) -> PipelineResult:
        return self.processor.process(message)
