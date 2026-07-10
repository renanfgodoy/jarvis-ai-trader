from fastapi import APIRouter

from app.models.polarium_direct import (
    PolariumDirectConfig,
    PolariumDirectProbeRequest,
    PolariumDirectProbeResponse,
    PolariumDirectSessionState,
)
from app.services.polarium_direct_login_lab import PolariumDirectLoginLabService

router = APIRouter(prefix="/polarium/direct", tags=["Polarium Direct Login Lab"])


@router.get("/config", response_model=PolariumDirectConfig)
def direct_config() -> PolariumDirectConfig:
    return PolariumDirectLoginLabService().config()


@router.post("/probe", response_model=PolariumDirectProbeResponse)
async def direct_probe(payload: PolariumDirectProbeRequest) -> PolariumDirectProbeResponse:
    return await PolariumDirectLoginLabService().probe(dry_run=payload.dry_run, force_demo=payload.force_demo)


@router.get("/session", response_model=PolariumDirectSessionState)
def direct_session() -> PolariumDirectSessionState:
    return PolariumDirectLoginLabService().session()


@router.post("/logout")
def direct_logout() -> dict:
    return PolariumDirectLoginLabService().logout()
