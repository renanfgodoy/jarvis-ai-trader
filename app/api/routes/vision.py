from __future__ import annotations

from email.parser import BytesParser
from email.policy import default
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Query, Request

from app.core.config import settings
from app.vision.enums import VisionTradeDecision
from app.vision.exceptions import VisionError, VisionProviderError, VisionRateLimitError, VisionValidationError
from app.vision.history import vision_history_repository
from app.vision.models import VisionStatus
from app.vision.service import VisionAnalyzeInput, vision_analysis_service

router = APIRouter(prefix="/vision", tags=["Friday Vision"])


@router.get("/status")
def get_vision_status() -> dict:
    return VisionStatus(
        enabled=settings.friday_vision_enabled,
        provider=settings.friday_vision_provider,
        analysis_available=settings.friday_vision_enabled,
        allowed_formats=settings.friday_vision_allowed_formats_tuple,
        max_image_mb=settings.friday_vision_max_image_mb,
        require_auth=settings.friday_vision_require_auth,
    ).model_dump(mode="json")


@router.post("/analyze")
async def analyze_vision(
    request: Request,
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
    x_friday_user: str | None = Header(default=None, alias="X-Friday-User"),
) -> dict:
    user_id = _resolve_user_id(x_friday_user)
    fields = await _parse_multipart_form(request)
    image = fields.get("image")
    if not isinstance(image, dict):
        raise _http_error("VISION_IMAGE_EMPTY", 400)
    try:
        result = await vision_analysis_service.analyze(
            VisionAnalyzeInput(
                image_bytes=image["content"],
                filename=image.get("filename"),
                content_type=image.get("content_type"),
                asset=_optional_text(fields.get("asset")),
                timeframe=_required_text(fields.get("timeframe"), "VISION_INVALID_TIMEFRAME"),
                expiration=_required_text(fields.get("expiration"), "VISION_INVALID_EXPIRATION"),
                strategy_mode=_optional_text(fields.get("strategy_mode")) or "COMPLETE",
                user_notes=_optional_text(fields.get("user_notes")),
                request_id=x_request_id or str(uuid4()),
                user_id=user_id,
            )
        )
    except VisionRateLimitError as exc:
        raise _http_error(exc.error_code, 429) from exc
    except VisionValidationError as exc:
        raise _http_error(exc.error_code, 400) from exc
    except VisionProviderError as exc:
        status_code = 503
        if exc.error_code == "VISION_PROVIDER_NOT_CONFIGURED":
            status_code = 503
        elif exc.error_code == "VISION_PROVIDER_RATE_LIMIT":
            status_code = 429
        elif exc.error_code == "VISION_INVALID_PROVIDER_RESPONSE":
            status_code = 502
        raise _http_error(exc.error_code, status_code) from exc
    except VisionError as exc:
        raise _http_error(exc.error_code, 400) from exc
    except ValueError as exc:
        raise _http_error(str(exc) or "VISION_INVALID_REQUEST", 400) from exc
    return result.model_dump(mode="json")


@router.get("/history")
def get_vision_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    decision: VisionTradeDecision | None = Query(default=None),
    asset: str | None = Query(default=None),
) -> dict:
    return {
        "items": [
            item.model_dump(mode="json")
            for item in vision_history_repository.list(limit=limit, offset=offset, decision=decision, asset=asset)
        ],
        "limit": limit,
        "offset": offset,
    }


@router.get("/history/{analysis_id}")
def get_vision_history_item(analysis_id: str) -> dict:
    item = vision_history_repository.get(analysis_id)
    if item is None:
        raise _http_error("VISION_HISTORY_NOT_FOUND", 404)
    return item.model_dump(mode="json")


def _resolve_user_id(x_friday_user: str | None) -> str:
    if x_friday_user and x_friday_user.strip():
        return x_friday_user.strip()[:120]
    if settings.friday_vision_require_auth and settings.environment == "production":
        raise _http_error("VISION_AUTH_REQUIRED", 401)
    return "local-development-user"


async def _parse_multipart_form(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" not in content_type:
        raise _http_error("VISION_INVALID_MULTIPART", 415)
    boundary = _extract_boundary(content_type)
    body = await request.body()
    if not body:
        raise _http_error("VISION_IMAGE_EMPTY", 400)
    message = BytesParser(policy=default).parsebytes(
        b"Content-Type: multipart/form-data; boundary=" + boundary.encode("utf-8") + b"\r\n\r\n" + body
    )
    fields: dict[str, Any] = {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if filename is not None:
            fields[name] = {
                "filename": filename,
                "content_type": part.get_content_type(),
                "content": payload,
            }
        else:
            fields[name] = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
    return fields


def _extract_boundary(content_type: str) -> str:
    for piece in content_type.split(";"):
        piece = piece.strip()
        if piece.startswith("boundary="):
            return piece.split("=", 1)[1].strip('"')
    raise _http_error("VISION_INVALID_MULTIPART", 415)


def _required_text(value: Any, error_code: str) -> str:
    text = _optional_text(value)
    if not text:
        raise ValueError(error_code)
    return text


def _optional_text(value: Any) -> str | None:
    if value is None or isinstance(value, dict):
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _http_error(error_code: str, status_code: int) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"error_code": error_code})
