from fastapi import APIRouter

from app.models.polarium_ws_recorder import WsFrameInput, WsRecorderConsoleSnippetResponse, WsRecordingResponse
from app.services.polarium_ws_recorder import PolariumWsRecorderService

router = APIRouter(prefix="/polarium/ws-recorder", tags=["Polarium WS Session Recorder"])


@router.post("/analyze", response_model=WsRecordingResponse)
def analyze_ws_frames(payload: WsFrameInput) -> WsRecordingResponse:
    return PolariumWsRecorderService().analyze_frames(payload)


@router.get("/snippet", response_model=WsRecorderConsoleSnippetResponse)
def get_console_snippet() -> WsRecorderConsoleSnippetResponse:
    return PolariumWsRecorderService().console_snippet()
