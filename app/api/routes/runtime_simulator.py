from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.market.runtime import controlled_candle_stream_simulator
from app.market.runtime_simulator import ControlledCandleSimulatorConfig, ControlledCandleSimulatorStatus

router = APIRouter(prefix="/runtime/simulator", tags=["Development Runtime"])


class StartControlledCandleSimulatorRequest(BaseModel):
    active_id: int = Field(default=76, ge=1)
    raw_size: int = Field(default=60, ge=60, le=60)
    interval_seconds: float = Field(default=1.0, gt=0, le=60)
    tick_seconds: int = Field(default=1, ge=1, le=60)
    start_timestamp: int = Field(default=1_783_721_940, ge=1)
    start_price: float = Field(default=1.162275, gt=0)
    price_step: float = Field(default=0.00001, gt=0)


@router.post("/start")
def start_controlled_candle_simulator(request: StartControlledCandleSimulatorRequest | None = None) -> dict:
    """Development-only controlled simulated candle stream."""

    _ensure_development_runtime()
    payload = request or StartControlledCandleSimulatorRequest()
    status = controlled_candle_stream_simulator.start(
        ControlledCandleSimulatorConfig(
            active_id=payload.active_id,
            raw_size=payload.raw_size,
            interval_seconds=payload.interval_seconds,
            tick_seconds=payload.tick_seconds,
            start_timestamp=payload.start_timestamp,
            start_price=payload.start_price,
            price_step=payload.price_step,
        )
    )
    return _status_to_response(status)


@router.post("/stop")
def stop_controlled_candle_simulator() -> dict:
    """Stop the development-only controlled simulated candle stream."""

    _ensure_development_runtime()
    return _status_to_response(controlled_candle_stream_simulator.stop())


@router.get("/status")
def get_controlled_candle_simulator_status() -> dict:
    """Return the controlled simulated candle stream status."""

    _ensure_development_runtime()
    return _status_to_response(controlled_candle_stream_simulator.status())


def _ensure_development_runtime() -> None:
    if not settings.is_development_runtime_enabled:
        raise HTTPException(status_code=403, detail="Controlled candle stream simulator is disabled in production.")


def _status_to_response(status: ControlledCandleSimulatorStatus) -> dict:
    return {
        "running": status.running,
        "development_only": True,
        "data_classification": status.data_classification,
        "active_id": status.active_id,
        "raw_size": status.raw_size,
        "interval_seconds": status.interval_seconds,
        "tick_seconds": status.tick_seconds,
        "current_start_timestamp": status.current_start_timestamp,
        "current_elapsed_seconds": status.current_elapsed_seconds,
        "current_open": status.current_open,
        "current_close": status.current_close,
        "current_min": status.current_min,
        "current_max": status.current_max,
        "generated_updates": status.generated_updates,
        "generated_candles": status.generated_candles,
        "last_pipeline_success": status.last_pipeline_success,
        "last_pipeline_stored": status.last_pipeline_stored,
        "last_pipeline_updated": status.last_pipeline_updated,
        "last_pipeline_ignored": status.last_pipeline_ignored,
        "warning": "SIMULATED / CONTROLLED DEVELOPMENT DATA. No WebSocket, Connector, OAuth, credentials, Polarium access, real market data, signals, AI, or execution.",
    }
