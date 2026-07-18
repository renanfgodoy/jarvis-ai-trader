from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/market/chart", tags=["Retired Broker Chart"])

BROKER_CHART_RETIRED_RESPONSE = {
    "code": "BROKER_CHART_FEATURE_RETIRED",
    "message": "A Friday agora utiliza análise de mercado por imagem.",
}


@router.get("")
def retired_market_chart() -> JSONResponse:
    return JSONResponse(BROKER_CHART_RETIRED_RESPONSE, status_code=410)


@router.get("/series")
def retired_market_chart_series() -> JSONResponse:
    return JSONResponse(BROKER_CHART_RETIRED_RESPONSE, status_code=410)
