from typing import Literal

from pydantic import BaseModel

DirectLoginStatus = Literal[
    "READY",
    "MISSING_CONFIG",
    "DRY_RUN",
    "LOGIN_FAILED",
    "SESSION_STORED",
    "NOT_AUTHORIZED",
]


class PolariumDirectConfig(BaseModel):
    configured: bool
    login_url_configured: bool
    email_configured: bool
    password_configured: bool
    websocket_url_configured: bool
    login_url: str | None = None
    websocket_url: str | None = None
    message: str
    safety_rules: list[str] = []


class PolariumDirectProbeRequest(BaseModel):
    dry_run: bool = True
    force_demo: bool = True


class PolariumDirectProbeResponse(BaseModel):
    success: bool
    status: DirectLoginStatus
    dry_run: bool
    token_stored: bool = False
    token_type: str | None = None
    response_keys: list[str] = []
    http_status: int | None = None
    message: str
    warnings: list[str] = []


class PolariumDirectSessionState(BaseModel):
    has_session: bool
    status: DirectLoginStatus
    token_type: str | None = None
    response_keys: list[str] = []
    message: str
    safety_rules: list[str] = []
