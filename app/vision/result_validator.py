from __future__ import annotations

from pydantic import ValidationError

from app.vision.enums import VisionTradeDecision
from app.vision.exceptions import VisionProviderError
from app.vision.models import VisionAnalysisResult


class VisionResultValidator:
    def validate(self, payload: dict, *, model: str, processing_time_ms: int) -> VisionAnalysisResult:
        try:
            result = VisionAnalysisResult.model_validate(
                {
                    **payload,
                    "model": model,
                    "processing_time_ms": processing_time_ms,
                }
            )
        except ValidationError as exc:
            raise VisionProviderError("Invalid provider response.", error_code="VISION_INVALID_PROVIDER_RESPONSE") from exc

        if result.decision in {VisionTradeDecision.CALL, VisionTradeDecision.PUT}:
            required = [result.market_reading, result.entry_condition, result.invalidation_condition]
            if any(not item.strip() for item in required) or not result.warnings or not result.limitations:
                raise VisionProviderError("Actionable response lacks required safeguards.", error_code="VISION_INVALID_PROVIDER_RESPONSE")
        if not result.chart_visible or not result.candles_visible:
            if result.decision != VisionTradeDecision.DO_NOT_TRADE:
                raise VisionProviderError("Invisible chart must not produce trade decision.", error_code="VISION_INVALID_PROVIDER_RESPONSE")
        return result
