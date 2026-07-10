from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

InspectorStatus = Literal["OK", "WARN", "FAIL", "SKIPPED"]


class InspectorFinding(BaseModel):
    name: str
    status: InspectorStatus
    message: str
    detail: dict[str, Any] = Field(default_factory=dict)


class HarInspectRequest(BaseModel):
    har: dict[str, Any]
    redact: bool = True


class HarInspectResponse(BaseModel):
    module: str = "session_inspector"
    status: InspectorStatus
    total_entries: int
    oauth_authorize_found: bool
    oauth_token_found: bool
    websocket_found: bool
    bearer_found: bool
    cookie_auth_found: bool
    findings: list[InspectorFinding]
    next_action: str


class ClientStorageProbeRequest(BaseModel):
    local_storage_keys: list[str] = Field(default_factory=list)
    session_storage_keys: list[str] = Field(default_factory=list)
    cookie_names: list[str] = Field(default_factory=list)
    origin: str | None = None


class ClientStorageProbeResponse(BaseModel):
    module: str = "client_storage_probe"
    status: InspectorStatus
    findings: list[InspectorFinding]
    next_action: str
