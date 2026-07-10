from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

RecorderStatus = Literal["OK", "WARN", "FAIL", "SKIPPED"]


class WsFrameInput(BaseModel):
    raw: str = Field(..., description="Linhas copiadas da aba Network > WebSocket > Messages/Frames do DevTools.")
    redact: bool = True


class WsRecorderFinding(BaseModel):
    name: str
    status: RecorderStatus
    message: str
    detail: dict[str, Any] = Field(default_factory=dict)


class WsMessageSummary(BaseModel):
    index: int
    direction: str = "UNKNOWN"
    name: str | None = None
    microservice_name: str | None = None
    request_id: str | None = None
    active_id: int | None = None
    has_balance: bool = False
    has_candle: bool = False
    has_price: bool = False
    has_auth_hint: bool = False
    preview: dict[str, Any] = Field(default_factory=dict)


class WsRecordingResponse(BaseModel):
    module: str = "ws_session_recorder"
    status: RecorderStatus
    total_lines: int
    parsed_messages: int
    detected_events: dict[str, int]
    first_messages: list[WsMessageSummary]
    auth_candidates: list[WsMessageSummary]
    balance_candidates: list[WsMessageSummary]
    candle_candidates: list[WsMessageSummary]
    price_candidates: list[WsMessageSummary]
    findings: list[WsRecorderFinding]
    next_action: str


class WsRecorderConsoleSnippetResponse(BaseModel):
    module: str = "ws_session_recorder_snippet"
    status: RecorderStatus = "OK"
    title: str
    warning: str
    snippet: str
