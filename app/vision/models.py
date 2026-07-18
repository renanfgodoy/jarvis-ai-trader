from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.vision.enums import (
    VisionImageQuality,
    VisionMarketState,
    VisionRiskLevel,
    VisionStrategyMode,
    VisionTradeDecision,
    VisionTrend,
)


class VisionImageMetadata(BaseModel):
    filename: str | None = None
    content_type: str
    size_bytes: int
    width: int
    height: int
    image_hash: str
    format: str
    exif_removed: bool = True


class VisionAnalysisRequest(BaseModel):
    asset: str | None = None
    timeframe: str
    expiration: str
    strategy_mode: VisionStrategyMode = VisionStrategyMode.COMPLETE
    user_notes: str | None = None
    image_hash: str
    image_width: int
    image_height: int
    mime_type: str

    @field_validator("timeframe")
    @classmethod
    def validate_timeframe(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"M1", "M5", "M15"}:
            raise ValueError("VISION_INVALID_TIMEFRAME")
        return normalized

    @field_validator("expiration")
    @classmethod
    def validate_expiration(cls, value: str) -> str:
        normalized = " ".join(value.strip().lower().split())
        allowed = {"1 minuto", "5 minutos", "15 minutos"}
        if normalized not in allowed:
            raise ValueError("VISION_INVALID_EXPIRATION")
        return normalized

    @field_validator("asset")
    @classmethod
    def normalize_asset(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        return cleaned or None

    @field_validator("user_notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned[:1000] or None


class VisionAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    decision: VisionTradeDecision
    asset_detected: str | None = None
    timeframe_detected: str | None = None
    expiration_considered: str
    trend: VisionTrend
    market_state: VisionMarketState
    risk: VisionRiskLevel
    confidence: Annotated[int, Field(ge=0, le=100)]
    image_quality: VisionImageQuality
    chart_visible: bool
    candles_visible: bool
    summary: str
    market_reading: str
    entry_condition: str
    invalidation_condition: str
    support_zones: tuple[str, ...] = ()
    resistance_zones: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model: str
    processing_time_ms: int = Field(ge=0)

    @field_validator(
        "summary",
        "market_reading",
        "entry_condition",
        "invalidation_condition",
    )
    @classmethod
    def non_empty_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("VISION_REQUIRED_TEXT_EMPTY")
        return cleaned


class VisionHistoryItem(BaseModel):
    analysis_id: str
    image_hash: str
    asset_informed: str | None
    asset_detected: str | None
    timeframe_informed: str
    timeframe_detected: str | None
    expiration: str
    decision: VisionTradeDecision
    trend: VisionTrend
    market_state: VisionMarketState
    risk: VisionRiskLevel
    confidence: int
    summary: str
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]
    model: str
    processing_time_ms: int
    created_at: datetime


class VisionStatus(BaseModel):
    enabled: bool
    mode: str = "VISION_FIRST"
    provider: str
    analysis_available: bool
    allowed_formats: tuple[str, ...]
    max_image_mb: int
    require_auth: bool


class ProcessedVisionImage(BaseModel):
    metadata: VisionImageMetadata
    image_bytes: bytes
    mime_type: str
