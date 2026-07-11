from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.market.browser_bridge import MAX_PAYLOAD_BYTES
from app.market.runtime import authorized_browser_bridge_runtime, controlled_candle_stream_simulator

router = APIRouter(prefix="/polarium/browser-bridge", tags=["Polarium Authorized Browser Bridge"])

BRIDGE_HEADER = "x-friday-trade-bridge"
BRIDGE_HEADER_VALUE = "POLARIUM_AUTHORIZED_BROWSER"
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}


@router.post("/message")
async def ingest_browser_bridge_message(request: Request) -> dict[str, Any]:
    _ensure_local_request(request)
    _ensure_bridge_header(request)
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        raise HTTPException(status_code=415, detail="Browser Bridge accepts only application/json.")

    body = await request.body()
    if len(body) > MAX_PAYLOAD_BYTES:
        result = authorized_browser_bridge_runtime.ingest({}, payload_size=len(body))
        raise HTTPException(status_code=413, detail=result.sanitized())

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Browser Bridge payload must be a JSON object.")

    if controlled_candle_stream_simulator.is_running:
        controlled_candle_stream_simulator.stop()

    result = authorized_browser_bridge_runtime.ingest(payload, payload_size=len(body))
    if not result.accepted:
        raise HTTPException(status_code=400, detail=result.sanitized())
    return result.sanitized()


@router.get("/status")
def get_browser_bridge_status(request: Request) -> dict[str, Any]:
    _ensure_local_request(request)
    return authorized_browser_bridge_runtime.status().sanitized()


def _ensure_local_request(request: Request) -> None:
    client_host = request.client.host if request.client else None
    if client_host not in LOCAL_HOSTS:
        raise HTTPException(status_code=403, detail="Browser Bridge accepts only local requests.")


def _ensure_bridge_header(request: Request) -> None:
    if request.headers.get(BRIDGE_HEADER) != BRIDGE_HEADER_VALUE:
        raise HTTPException(status_code=403, detail="Browser Bridge local header is required.")
