from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/market/provider-v2", tags=["Retired Broker Provider V2"])


@router.get("/status")
def retired_provider_v2_status() -> JSONResponse:
    return JSONResponse({
        "code": "BROKER_CHART_FEATURE_RETIRED",
        "message": "A Friday agora utiliza análise de mercado por imagem.",
    }, status_code=410)
