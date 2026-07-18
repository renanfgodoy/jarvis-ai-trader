from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock

from app.core.config import settings
from app.vision.clients import FakeVisionClient, OpenAIVisionClient, VisionAIClient
from app.vision.diagnostics import vision_diagnostics
from app.vision.exceptions import VisionProviderError, VisionRateLimitError
from app.vision.history import VisionHistoryRepository, vision_history_repository
from app.vision.image_processor import VisionImageProcessor
from app.vision.models import ProcessedVisionImage, VisionAnalysisRequest, VisionAnalysisResult


@dataclass
class VisionAnalyzeInput:
    image_bytes: bytes
    filename: str | None
    content_type: str | None
    asset: str | None
    timeframe: str
    expiration: str
    strategy_mode: str
    user_notes: str | None
    request_id: str
    user_id: str


class VisionRateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._timestamps: dict[str, list[float]] = {}
        self._in_flight: set[str] = set()
        self._completed_request_ids: dict[tuple[str, str], float] = {}

    def begin(self, *, user_id: str, request_id: str) -> None:
        now = time.time()
        with self._lock:
            key = (user_id, request_id)
            if key in self._completed_request_ids and now - self._completed_request_ids[key] < settings.friday_vision_cooldown_seconds:
                raise VisionRateLimitError("Duplicate request.", error_code="VISION_DUPLICATE_REQUEST")
            if user_id in self._in_flight:
                raise VisionRateLimitError("Analysis already in progress.", error_code="VISION_ANALYSIS_IN_PROGRESS")
            window_start = now - 3600
            timestamps = [item for item in self._timestamps.get(user_id, []) if item >= window_start]
            if len(timestamps) >= settings.friday_vision_max_analyses_per_hour:
                raise VisionRateLimitError("Rate limit exceeded.", error_code="VISION_PROVIDER_RATE_LIMIT")
            last = timestamps[-1] if timestamps else 0
            if now - last < settings.friday_vision_cooldown_seconds:
                raise VisionRateLimitError("Cooldown active.", error_code="VISION_COOLDOWN_ACTIVE")
            timestamps.append(now)
            self._timestamps[user_id] = timestamps
            self._in_flight.add(user_id)

    def finish(self, *, user_id: str, request_id: str) -> None:
        with self._lock:
            self._in_flight.discard(user_id)
            self._completed_request_ids[(user_id, request_id)] = time.time()

    def clear(self) -> None:
        with self._lock:
            self._timestamps.clear()
            self._in_flight.clear()
            self._completed_request_ids.clear()


class VisionAnalysisService:
    def __init__(
        self,
        *,
        image_processor: VisionImageProcessor | None = None,
        history: VisionHistoryRepository | None = None,
        rate_limiter: VisionRateLimiter | None = None,
        client: VisionAIClient | None = None,
    ) -> None:
        self.image_processor = image_processor or VisionImageProcessor()
        self.history = history or vision_history_repository
        self.rate_limiter = rate_limiter or vision_rate_limiter
        self.client = client

    async def analyze(self, payload: VisionAnalyzeInput) -> VisionAnalysisResult:
        if not settings.friday_vision_enabled:
            raise VisionProviderError("Friday Vision is disabled.", error_code="VISION_DISABLED")
        self.rate_limiter.begin(user_id=payload.user_id, request_id=payload.request_id)
        processed: ProcessedVisionImage | None = None
        provider_called = False
        started = time.perf_counter()
        try:
            processed = self.image_processor.process(
                image_bytes=payload.image_bytes,
                filename=payload.filename,
                content_type=payload.content_type,
            )
            request = VisionAnalysisRequest(
                asset=payload.asset,
                timeframe=payload.timeframe,
                expiration=payload.expiration,
                strategy_mode=payload.strategy_mode,
                user_notes=payload.user_notes,
                image_hash=processed.metadata.image_hash,
                image_width=processed.metadata.width,
                image_height=processed.metadata.height,
                mime_type=processed.mime_type,
            )
            client = self.client or self._build_client()
            provider_called = True
            result = await client.analyze(image_bytes=processed.image_bytes, mime_type=processed.mime_type, context=request)
            if settings.friday_vision_save_history:
                self.history.save(request=request, result=result)
            vision_diagnostics.record(
                {
                    "request_id": payload.request_id,
                    "analysis_id": result.analysis_id,
                    "image_hash_prefix": processed.metadata.image_hash[:12],
                    "mime_type": processed.mime_type,
                    "image_width": processed.metadata.width,
                    "image_height": processed.metadata.height,
                    "provider": settings.friday_vision_provider,
                    "model": result.model,
                    "provider_called": provider_called,
                    "provider_success": True,
                    "provider_latency_ms": result.processing_time_ms,
                    "decision": result.decision,
                    "risk": result.risk,
                    "confidence": result.confidence,
                    "history_saved": settings.friday_vision_save_history,
                    "image_saved": settings.friday_vision_save_images,
                    "error_code": None,
                }
            )
            return result
        except Exception as exc:
            vision_diagnostics.record(
                {
                    "request_id": payload.request_id,
                    "analysis_id": None,
                    "image_hash_prefix": processed.metadata.image_hash[:12] if processed else None,
                    "mime_type": processed.mime_type if processed else None,
                    "image_width": processed.metadata.width if processed else None,
                    "image_height": processed.metadata.height if processed else None,
                    "provider": settings.friday_vision_provider,
                    "model": settings.friday_vision_model,
                    "provider_called": provider_called,
                    "provider_success": False,
                    "provider_latency_ms": int((time.perf_counter() - started) * 1000),
                    "decision": None,
                    "risk": None,
                    "confidence": None,
                    "history_saved": False,
                    "image_saved": False,
                    "error_code": getattr(exc, "error_code", "VISION_INTERNAL_ERROR"),
                }
            )
            raise
        finally:
            self.rate_limiter.finish(user_id=payload.user_id, request_id=payload.request_id)

    def _build_client(self) -> VisionAIClient:
        provider = settings.friday_vision_provider.strip().lower()
        if provider == "openai":
            return OpenAIVisionClient()
        if provider == "fake":
            return FakeVisionClient()
        raise VisionProviderError("Unsupported provider.", error_code="VISION_PROVIDER_UNAVAILABLE")


vision_rate_limiter = VisionRateLimiter()
vision_analysis_service = VisionAnalysisService()
