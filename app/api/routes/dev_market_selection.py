from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.market.runtime import polarium_cdp_live_source

router = APIRouter(prefix="/api/dev", tags=["Development Market Selection"])


class SelectMarketRequest(BaseModel):
    active_id: int = Field(..., gt=0)
    raw_size: int = Field(..., gt=0)


@router.post("/select-market")
async def select_market(request: SelectMarketRequest) -> dict:
    if not settings.is_development_runtime_enabled:
        raise HTTPException(status_code=403, detail={"error_code": "DEVELOPMENT_ENDPOINT_DISABLED"})
    if not settings.polarium_programmatic_selection_enabled:
        raise HTTPException(status_code=403, detail={"error_code": "PROGRAMMATIC_SELECTION_DISABLED"})
    if request.raw_size not in {60, 300, 900}:
        raise HTTPException(status_code=400, detail={"error_code": "UNSUPPORTED_RAW_SIZE"})

    result = await polarium_cdp_live_source.select_market(active_id=request.active_id, raw_size=request.raw_size)
    payload = result.sanitized()
    if not result.accepted:
        status_code = 400 if result.error_code == "INVALID_MARKET_CONTEXT" else 409
        raise HTTPException(status_code=status_code, detail=payload)
    return payload
