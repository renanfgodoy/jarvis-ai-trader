from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any

from app.market.pipeline import MarketPipeline
from app.market.pipeline.models import PipelineResult

CONTROLLED_SIMULATED_DATA_LABEL = "SIMULATED / CONTROLLED DEVELOPMENT DATA"


@dataclass(frozen=True)
class ControlledCandleSimulatorConfig:
    active_id: int = 76
    raw_size: int = 60
    interval_seconds: float = 1.0
    tick_seconds: int = 1
    start_timestamp: int = 1_783_721_940
    start_price: float = 1.162275
    price_step: float = 0.00001


@dataclass(frozen=True)
class ControlledCandleSimulatorStatus:
    running: bool
    data_classification: str
    active_id: int
    raw_size: int
    interval_seconds: float
    tick_seconds: int
    current_start_timestamp: int
    current_elapsed_seconds: int
    current_open: float
    current_close: float
    current_min: float
    current_max: float
    generated_updates: int
    generated_candles: int
    last_pipeline_success: bool | None
    last_pipeline_stored: int
    last_pipeline_updated: int
    last_pipeline_ignored: int


class ControlledCandleStreamSimulator:
    """Development-only candle stream simulator that feeds the shared pipeline."""

    def __init__(self, pipeline: MarketPipeline) -> None:
        self._pipeline = pipeline
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._config = ControlledCandleSimulatorConfig()
        self._state = _SimulatorState.from_config(self._config)
        self._generated_updates = 0
        self._generated_candles = 0
        self._last_pipeline_result: PipelineResult | None = None

    @property
    def pipeline(self) -> MarketPipeline:
        return self._pipeline

    def start(self, config: ControlledCandleSimulatorConfig | None = None) -> ControlledCandleSimulatorStatus:
        with self._lock:
            if self.is_running:
                return self.status()

            self._config = config or self._config
            self._state = _SimulatorState.from_config(self._config)
            self._generated_updates = 0
            self._generated_candles = 0
            self._last_pipeline_result = None
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, name="controlled-candle-stream-simulator", daemon=True)
            self._thread.start()

        self.advance()
        return self.status()

    def stop(self) -> ControlledCandleSimulatorStatus:
        thread: threading.Thread | None
        with self._lock:
            thread = self._thread
            self._stop_event.set()
            self._thread = None
        if thread and thread.is_alive():
            thread.join(timeout=2)
        return self.status()

    def status(self) -> ControlledCandleSimulatorStatus:
        with self._lock:
            result = self._last_pipeline_result
            return ControlledCandleSimulatorStatus(
                running=self.is_running,
                data_classification=CONTROLLED_SIMULATED_DATA_LABEL,
                active_id=self._config.active_id,
                raw_size=self._config.raw_size,
                interval_seconds=self._config.interval_seconds,
                tick_seconds=self._config.tick_seconds,
                current_start_timestamp=self._state.start_timestamp,
                current_elapsed_seconds=self._state.elapsed_seconds,
                current_open=self._state.open,
                current_close=self._state.close,
                current_min=self._state.minimum,
                current_max=self._state.maximum,
                generated_updates=self._generated_updates,
                generated_candles=self._generated_candles,
                last_pipeline_success=result.success if result else None,
                last_pipeline_stored=result.stored if result else 0,
                last_pipeline_updated=result.updated if result else 0,
                last_pipeline_ignored=result.ignored if result else 0,
            )

    def advance(self) -> tuple[PipelineResult, ...]:
        """Advance one controlled interval. Tests use this to avoid timing flakiness."""

        with self._lock:
            results = [self._emit_current_update()]
            self._state.elapsed_seconds += self._config.tick_seconds
            if self._state.elapsed_seconds >= self._config.raw_size:
                self._roll_to_next_candle()
                results.append(self._emit_current_update())
            return tuple(results)

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self) -> None:
        while not self._stop_event.wait(self._config.interval_seconds):
            self.advance()

    def _emit_current_update(self) -> PipelineResult:
        self._state.apply_next_price(self._config.price_step)
        result = self._pipeline.process(_candle_generated_message(self._config, self._state))
        self._last_pipeline_result = result
        self._generated_updates += 1
        if result.stored:
            self._generated_candles += result.stored
        return result

    def _roll_to_next_candle(self) -> None:
        next_open = self._state.close
        self._state = _SimulatorState(
            start_timestamp=self._state.start_timestamp + self._config.raw_size,
            elapsed_seconds=0,
            open=next_open,
            close=next_open,
            minimum=next_open,
            maximum=next_open,
            sequence=self._state.sequence,
        )


@dataclass
class _SimulatorState:
    start_timestamp: int
    elapsed_seconds: int
    open: float
    close: float
    minimum: float
    maximum: float
    sequence: int

    @classmethod
    def from_config(cls, config: ControlledCandleSimulatorConfig) -> _SimulatorState:
        return cls(
            start_timestamp=config.start_timestamp,
            elapsed_seconds=0,
            open=config.start_price,
            close=config.start_price,
            minimum=config.start_price,
            maximum=config.start_price,
            sequence=0,
        )

    def apply_next_price(self, price_step: float) -> None:
        direction = 1 if self.sequence % 4 in {0, 1} else -1
        self.sequence += 1
        self.close = round(self.close + (direction * price_step), 6)
        self.minimum = min(self.minimum, self.close)
        self.maximum = max(self.maximum, self.close)


def _candle_generated_message(config: ControlledCandleSimulatorConfig, state: _SimulatorState) -> dict[str, Any]:
    return {
        "name": "candle-generated",
        "development_runtime": True,
        "data_classification": CONTROLLED_SIMULATED_DATA_LABEL,
        "msg": {
            "body": {
                "active_id": config.active_id,
                "size": config.raw_size,
                "from": state.start_timestamp,
                "to": state.start_timestamp + config.raw_size,
                "open": state.open,
                "close": state.close,
                "min": state.minimum,
                "max": state.maximum,
                "volume": 0,
            }
        },
    }
