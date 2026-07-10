from typing import Any, Literal

from pydantic import BaseModel, Field

DiagnosticStatus = Literal["OK", "WARN", "FAIL", "SKIPPED"]


class DiagnosticCheck(BaseModel):
    name: str
    status: DiagnosticStatus
    message: str
    detail: dict[str, Any] = Field(default_factory=dict)


class OAuthDiagnosticResponse(BaseModel):
    module: str = "oauth"
    status: DiagnosticStatus
    checks: list[DiagnosticCheck]
    next_action: str


class WebSocketDiagnosticRequest(BaseModel):
    ws_url: str | None = None
    bearer_token: str | None = None
    timeout_seconds: float = Field(default=4.0, ge=1.0, le=15.0)
    send_probe: bool = False


class WebSocketDiagnosticResponse(BaseModel):
    module: str = "websocket"
    status: DiagnosticStatus
    ws_url: str
    connected: bool
    close_code: int | None = None
    close_reason: str | None = None
    first_message_preview: str | None = None
    checks: list[DiagnosticCheck]
    next_action: str


class StreamDiagnosticRequest(BaseModel):
    payloads: list[dict[str, Any]] = Field(default_factory=list)


class StreamDiagnosticResponse(BaseModel):
    module: str = "stream"
    status: DiagnosticStatus
    events_detected: dict[str, int]
    balance_payload_detected: bool
    candle_payload_detected: bool
    price_payload_detected: bool
    checks: list[DiagnosticCheck]
    next_action: str


class DiagnosticSummaryResponse(BaseModel):
    version: str
    status: DiagnosticStatus
    checks: list[DiagnosticCheck]
    next_action: str
