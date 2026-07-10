from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

OAuthLabStatus = Literal["READY", "MISSING_CONFIG", "TOKEN_STORED", "EXCHANGE_FAILED", "CALLBACK_RECEIVED"]


class PolariumOAuthConfig(BaseModel):
    configured: bool
    client_id_configured: bool
    authorize_url_configured: bool
    token_url_configured: bool
    redirect_uri: str
    token_url: str
    authorize_url: str | None = None
    message: str


class PolariumPkceStartRequest(BaseModel):
    redirect_uri: str | None = None
    scope: str = "full offline_access"
    remember_verifier: bool = True


class PolariumPkceStartResponse(BaseModel):
    ready: bool
    status: OAuthLabStatus
    state: str
    code_verifier_preview: str
    code_challenge: str
    code_challenge_method: str = "S256"
    redirect_uri: str
    authorize_url: str | None
    message: str
    warnings: list[str] = []


class PolariumOAuthCallbackResponse(BaseModel):
    received: bool
    status: OAuthLabStatus
    code_preview: str | None = None
    state: str | None = None
    message: str


class PolariumOAuthTokenExchangeRequest(BaseModel):
    code: str = Field(min_length=8)
    state: str | None = None
    code_verifier: str | None = None
    redirect_uri: str | None = None
    dry_run: bool = True


class PolariumOAuthTokenExchangeResponse(BaseModel):
    success: bool
    status: OAuthLabStatus
    dry_run: bool
    token_stored: bool = False
    token_type: str | None = None
    expires_in: int | None = None
    scope: str | None = None
    message: str
    warnings: list[str] = []


class PolariumOAuthSessionState(BaseModel):
    has_token: bool = False
    status: OAuthLabStatus = "MISSING_CONFIG"
    token_type: str | None = None
    expires_at: datetime | None = None
    scope: str | None = None
    last_error: str | None = None
    message: str
    safety_rules: list[str] = []
