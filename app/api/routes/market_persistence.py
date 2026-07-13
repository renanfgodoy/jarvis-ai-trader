from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.market.persistence import CandleIntegrityAuditor
from app.market.runtime import market_candle_persistence, market_candle_store

router = APIRouter(prefix="/market/persistence", tags=["Market Persistence"])


@router.get("/status")
def get_market_persistence_status() -> dict:
    return {"market_persistence": market_candle_persistence.status().sanitized()}


@router.get("/audit")
def get_market_persistence_audit() -> dict:
    return CandleIntegrityAuditor(market_candle_store).audit().sanitized()


@router.delete("/candles")
def clear_market_persistence_candles(confirm: bool = Query(default=False)) -> dict:
    if settings.environment == "production":
        raise HTTPException(status_code=403, detail={"error_code": "MARKET_PERSISTENCE_CLEANUP_DISABLED"})
    if not confirm:
        raise HTTPException(status_code=400, detail={"error_code": "CONFIRMATION_REQUIRED"})
    result = market_candle_persistence.cleanup(market_candle_store)
    return {
        "removed_candles_count": result.removed_candles_count,
        "removed_series_count": result.removed_series_count,
        "market_persistence": market_candle_persistence.status().sanitized(),
    }
