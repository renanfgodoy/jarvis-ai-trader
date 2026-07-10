from fastapi import APIRouter

from app.models.polarium_session_inspector import (
    ClientStorageProbeRequest,
    ClientStorageProbeResponse,
    HarInspectRequest,
    HarInspectResponse,
)
from app.connector.polarium.diagnostics.session_inspector import PolariumSessionInspectorService

router = APIRouter(prefix="/polarium/session-inspector", tags=["Polarium Session Inspector"])


@router.post("/har", response_model=HarInspectResponse)
def inspect_har(payload: HarInspectRequest) -> HarInspectResponse:
    return PolariumSessionInspectorService().inspect_har(payload)


@router.post("/client-storage", response_model=ClientStorageProbeResponse)
def probe_client_storage(payload: ClientStorageProbeRequest) -> ClientStorageProbeResponse:
    return PolariumSessionInspectorService().probe_client_storage(payload)
