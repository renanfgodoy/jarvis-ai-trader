from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from app.core.config import settings
from app.market.runtime import controlled_market_runtime_feed
from app.market.runtime_feed import RuntimeFeedResult

router = APIRouter(prefix="/runtime", tags=["Development Runtime"])


@router.post("/feed")
def feed_runtime_message(message: dict[str, Any] = Body(...)) -> dict:
    """Development Runtime Only: feed one sanitized market message."""

    if not settings.is_development_runtime_enabled:
        raise HTTPException(status_code=403, detail="Development runtime feed is disabled in production.")

    result = controlled_market_runtime_feed.feed(message)
    if result.errors and result.event_name is None:
        raise HTTPException(status_code=400, detail=list(result.errors))
    return _result_to_response(result)


def _result_to_response(result: RuntimeFeedResult) -> dict:
    return {
        "success": result.success,
        "development_only": result.development_only,
        "processed": result.processed,
        "stored": result.stored,
        "ignored": result.ignored,
        "updated": result.updated,
        "unsupported": result.unsupported,
        "rejected": result.rejected,
        "errors": list(result.errors),
        "event_name": result.event_name,
        "warning": "Development Runtime Only. Sanitized messages only. No WebSocket, Connector, OAuth, credentials, cookies, Authorization, Bearer tokens, or HAR payloads.",
    }
