from __future__ import annotations

from typing import Any

from tools.pocket_parser.models import PocketRealtimeTick, Rejection
from tools.pocket_parser.tick_normalizer import normalize_tick


def parse_update_stream(
    payload: Any,
    *,
    source_har: str,
    session_index: int,
    frame_index: int,
    sequence_start: int,
) -> tuple[list[PocketRealtimeTick], list[Rejection]]:
    if not isinstance(payload, list):
        return [], [Rejection("LIVE_STREAM_NESTING_UNSUPPORTED", "updateStream", source_har, session_index, frame_index, "payload root is not list")]
    rows = payload
    ticks: list[PocketRealtimeTick] = []
    rejections: list[Rejection] = []
    seen: set[tuple[str, float, float]] = set()
    for offset, raw in enumerate(rows):
        tick, error = normalize_tick(raw, sequence=sequence_start + offset, source_har=source_har, session_index=session_index)
        if error:
            rejections.append(Rejection(error, "updateStream", source_har, session_index, frame_index, "raw tick rejected"))
            continue
        assert tick is not None
        key = (tick.asset, tick.timestamp, tick.price)
        if key in seen:
            rejections.append(Rejection("DUPLICATE_TICK", "updateStream", source_har, session_index, frame_index, tick.asset))
            continue
        seen.add(key)
        ticks.append(tick)
    return ticks, rejections
