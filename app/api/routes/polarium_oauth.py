from fastapi import APIRouter, Query

from app.models.polarium_oauth import (
    PolariumOAuthCallbackResponse,
    PolariumOAuthConfig,
    PolariumOAuthSessionState,
    PolariumOAuthTokenExchangeRequest,
    PolariumOAuthTokenExchangeResponse,
    PolariumPkceStartRequest,
    PolariumPkceStartResponse,
)
from app.services.polarium_oauth_lab import PolariumOAuthLabService

router = APIRouter(prefix="/polarium/oauth", tags=["Polarium OAuth Lab"])


@router.get("/config", response_model=PolariumOAuthConfig)
def oauth_config() -> PolariumOAuthConfig:
    return PolariumOAuthLabService().config()


@router.post("/start", response_model=PolariumPkceStartResponse)
def oauth_start(payload: PolariumPkceStartRequest) -> PolariumPkceStartResponse:
    return PolariumOAuthLabService().start(
        redirect_uri=payload.redirect_uri,
        scope=payload.scope,
        remember_verifier=payload.remember_verifier,
    )


@router.get("/callback", response_model=PolariumOAuthCallbackResponse)
def oauth_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> PolariumOAuthCallbackResponse:
    return PolariumOAuthLabService().callback(code=code, state=state, error=error)


@router.post("/exchange", response_model=PolariumOAuthTokenExchangeResponse)
async def oauth_exchange(payload: PolariumOAuthTokenExchangeRequest) -> PolariumOAuthTokenExchangeResponse:
    return await PolariumOAuthLabService().exchange(
        code=payload.code,
        state=payload.state,
        code_verifier=payload.code_verifier,
        redirect_uri=payload.redirect_uri,
        dry_run=payload.dry_run,
    )


@router.get("/session", response_model=PolariumOAuthSessionState)
def oauth_session() -> PolariumOAuthSessionState:
    return PolariumOAuthLabService().session()


@router.post("/logout")
def oauth_logout() -> dict:
    return PolariumOAuthLabService().logout()
