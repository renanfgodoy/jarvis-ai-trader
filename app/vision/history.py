from __future__ import annotations

from threading import Lock

from app.vision.enums import VisionTradeDecision
from app.vision.models import VisionAnalysisRequest, VisionAnalysisResult, VisionHistoryItem


class VisionHistoryRepository:
    def __init__(self) -> None:
        self._items: dict[str, VisionHistoryItem] = {}
        self._lock = Lock()

    def save(self, *, request: VisionAnalysisRequest, result: VisionAnalysisResult) -> VisionHistoryItem:
        item = VisionHistoryItem(
            analysis_id=result.analysis_id,
            image_hash=request.image_hash,
            asset_informed=request.asset,
            asset_detected=result.asset_detected,
            timeframe_informed=request.timeframe,
            timeframe_detected=result.timeframe_detected,
            expiration=request.expiration,
            decision=result.decision,
            trend=result.trend,
            market_state=result.market_state,
            risk=result.risk,
            confidence=result.confidence,
            summary=result.summary,
            warnings=result.warnings,
            limitations=result.limitations,
            model=result.model,
            processing_time_ms=result.processing_time_ms,
            created_at=result.created_at,
        )
        with self._lock:
            self._items[item.analysis_id] = item
        return item

    def list(self, *, limit: int = 20, offset: int = 0, decision: VisionTradeDecision | None = None, asset: str | None = None) -> list[VisionHistoryItem]:
        with self._lock:
            items = sorted(self._items.values(), key=lambda item: item.created_at, reverse=True)
        if decision is not None:
            items = [item for item in items if item.decision == decision]
        if asset:
            normalized = asset.strip().lower()
            items = [
                item
                for item in items
                if (item.asset_informed and item.asset_informed.lower() == normalized)
                or (item.asset_detected and item.asset_detected.lower() == normalized)
            ]
        return items[offset : offset + limit]

    def get(self, analysis_id: str) -> VisionHistoryItem | None:
        with self._lock:
            return self._items.get(analysis_id)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


vision_history_repository = VisionHistoryRepository()
