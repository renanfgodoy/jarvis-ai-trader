from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/market/providers", tags=["Retired Broker Providers"])

BROKER_PROVIDERS_RETIRED_RESPONSE = {
    "code": "BROKER_PROVIDER_FEATURE_RETIRED",
    "message": "A Friday agora utiliza análise de mercado por imagem.",
}


@router.get("")
def retired_market_providers() -> JSONResponse:
    return JSONResponse(BROKER_PROVIDERS_RETIRED_RESPONSE, status_code=410)


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def retired_market_provider_path(path: str) -> JSONResponse:
    return JSONResponse({**BROKER_PROVIDERS_RETIRED_RESPONSE, "path": path}, status_code=410)
