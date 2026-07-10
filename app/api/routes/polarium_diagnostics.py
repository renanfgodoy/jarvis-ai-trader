from fastapi import APIRouter

from app.models.polarium_diagnostics import (
    DiagnosticSummaryResponse,
    OAuthDiagnosticResponse,
    StreamDiagnosticRequest,
    StreamDiagnosticResponse,
    WebSocketDiagnosticRequest,
    WebSocketDiagnosticResponse,
)
from app.services.polarium_diagnostics import PolariumDiagnosticService

router = APIRouter(prefix="/polarium/diagnostics", tags=["Polarium Diagnostics"])


@router.get("/summary", response_model=DiagnosticSummaryResponse)
def diagnostics_summary() -> DiagnosticSummaryResponse:
    return PolariumDiagnosticService().summary()


@router.get("/oauth", response_model=OAuthDiagnosticResponse)
def oauth_diagnostic() -> OAuthDiagnosticResponse:
    return PolariumDiagnosticService().oauth()


@router.post("/websocket", response_model=WebSocketDiagnosticResponse)
async def websocket_diagnostic(payload: WebSocketDiagnosticRequest) -> WebSocketDiagnosticResponse:
    return await PolariumDiagnosticService().websocket(payload)


@router.post("/stream", response_model=StreamDiagnosticResponse)
def stream_diagnostic(payload: StreamDiagnosticRequest) -> StreamDiagnosticResponse:
    return PolariumDiagnosticService().stream(payload.payloads)
