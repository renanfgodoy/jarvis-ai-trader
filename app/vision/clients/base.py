from __future__ import annotations

from typing import Protocol

from app.vision.models import VisionAnalysisRequest, VisionAnalysisResult


class VisionAIClient(Protocol):
    async def analyze(
        self,
        *,
        image_bytes: bytes,
        mime_type: str,
        context: VisionAnalysisRequest,
    ) -> VisionAnalysisResult:
        ...
