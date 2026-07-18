from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.orchestrator import CoreOrchestrator, ExecutionRequest
from modules.trading import TradingModule, TradingRequest


router = APIRouter(prefix="/core/demo", tags=["Core Demo"])


class CoreDemoExecutionRequest(BaseModel):
    module: str = Field(default="documents", min_length=1)
    identity: str = Field(default="jarvis.default", min_length=1)
    provider: str = Field(default="mock", min_length=1)
    language: str = Field(default="pt-BR", min_length=2)
    message: str = Field(min_length=1, max_length=8000)
    market: str | None = None
    symbol: str | None = None
    timeframe: str | None = None
    strategy: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    request_id: str | None = None


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return _serialize(asdict(value))
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(item) for item in value]
    return value


@router.post("/execute")
def execute_core_demo(payload: CoreDemoExecutionRequest) -> dict[str, Any]:
    if payload.provider.strip().lower() != "mock":
        raise HTTPException(status_code=400, detail="CORE_DEMO_ONLY_MOCK_PROVIDER_ALLOWED")

    if payload.module.strip().lower() == "trading":
        trading_response = TradingModule().execute(
            TradingRequest(
                market=payload.market or "OTC",
                symbol=payload.symbol or "EURUSD",
                timeframe=payload.timeframe or "M1",
                strategy=payload.strategy or "Trend",
                message=payload.message,
                metadata={
                    **payload.metadata,
                    "source": "friday_core_demo",
                    "developer_console": True,
                },
            )
        )
        return _serialize(trading_response)

    request = ExecutionRequest(
        request_id=payload.request_id or f"core-demo-{uuid4().hex}",
        module=payload.module,
        input=payload.message,
        identity=payload.identity,
        provider="mock",
        language=payload.language,
        metadata={
            **payload.metadata,
            "source": "friday_core_demo",
            "developer_console": True,
        },
    )
    response = CoreOrchestrator().execute(request)
    return _serialize(response)
