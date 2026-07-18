from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PocketRuntimeMetrics:
    events_received: int = 0
    events_processed: int = 0
    events_rejected: int = 0
    history_batches: int = 0
    historical_candles_written: int = 0
    historical_candles_rejected: int = 0
    ticks_received: int = 0
    ticks_processed: int = 0
    ticks_rejected: int = 0
    realtime_candles_created: int = 0
    realtime_candles_updated: int = 0
    duplicate_candles: int = 0
    unknown_events: int = 0
    guard_blocks: int = 0

