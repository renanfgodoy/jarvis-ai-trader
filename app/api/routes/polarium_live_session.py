from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.connector.polarium.live_session.runtime import polarium_live_session_manager
from app.connector.polarium.live_session.status import to_sanitized_status

router = APIRouter(prefix="/polarium/live-session", tags=["Polarium Live Session"])


@router.post("/start")
async def start_polarium_live_session(request: Request) -> dict:
    await _reject_request_body(request)
    status = polarium_live_session_manager.start()
    payload = to_sanitized_status(status)
    if status.state == "ERROR":
        raise HTTPException(status_code=409, detail=payload)
    return payload


@router.post("/stop")
async def stop_polarium_live_session(request: Request) -> dict:
    await _reject_request_body(request)
    return to_sanitized_status(polarium_live_session_manager.stop())


@router.get("/status")
def get_polarium_live_session_status() -> dict:
    return to_sanitized_status(polarium_live_session_manager.status())


async def _reject_request_body(request: Request) -> None:
    body = await request.body()
    if body.strip():
        raise HTTPException(status_code=400, detail="Polarium live-session endpoints do not accept request bodies or credentials.")
