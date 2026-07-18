from __future__ import annotations

from app.vision.enums import VisionImageQuality, VisionMarketState, VisionRiskLevel, VisionTradeDecision, VisionTrend
from app.vision.models import VisionAnalysisRequest, VisionAnalysisResult


class FakeVisionClient:
    def __init__(self, *, decision: VisionTradeDecision = VisionTradeDecision.WAIT) -> None:
        self.decision = decision

    async def analyze(
        self,
        *,
        image_bytes: bytes,
        mime_type: str,
        context: VisionAnalysisRequest,
    ) -> VisionAnalysisResult:
        return VisionAnalysisResult(
            decision=self.decision,
            asset_detected=context.asset,
            timeframe_detected=context.timeframe,
            expiration_considered=context.expiration,
            trend=VisionTrend.UNCLEAR,
            market_state=VisionMarketState.UNCLEAR,
            risk=VisionRiskLevel.HIGH,
            confidence=42,
            image_quality=VisionImageQuality.ACCEPTABLE,
            chart_visible=True,
            candles_visible=True,
            summary="Leitura fake controlada para testes da Friday Vision.",
            market_reading="Contexto visual tratado como insuficiente para uma entrada real.",
            entry_condition="Aguardar confirmação visual clara antes de qualquer decisão.",
            invalidation_condition="Desconsiderar a leitura se o gráfico estiver ilegível ou mudar de contexto.",
            support_zones=("Não avaliadas pelo cliente fake.",),
            resistance_zones=("Não avaliadas pelo cliente fake.",),
            warnings=("Cliente fake não deve ser usado como validação real.",),
            limitations=("Sem chamada ao provedor multimodal real.",),
            model="fake-vision-client",
            processing_time_ms=0,
        )
