from __future__ import annotations

from typing import Any

from tools.pocket_parser.candle_normalizer import normalize_candle
from tools.pocket_parser.models import PocketHistoryBatch, Rejection
from tools.pocket_parser.utils import timeframe_for_period


def parse_history_batch(
    payload: Any,
    *,
    source_har: str,
    session_index: int,
    frame_index: int,
) -> tuple[PocketHistoryBatch | None, list[Rejection]]:
    rejections: list[Rejection] = []
    if not isinstance(payload, dict):
        return None, [_reject("UNSUPPORTED_PAYLOAD", source_har, session_index, frame_index, "payload is not dict")]
    asset = payload.get("asset")
    period = payload.get("period")
    if not isinstance(asset, str) or not asset:
        return None, [_reject("MISSING_ASSET", source_har, session_index, frame_index, "asset missing")]
    if not isinstance(period, int):
        return None, [_reject("UNSUPPORTED_PERIOD", source_har, session_index, frame_index, "period missing")]
    try:
        timeframe = timeframe_for_period(period)
    except ValueError:
        return None, [_reject("UNSUPPORTED_PERIOD", source_har, session_index, frame_index, str(period))]
    raw_candles = payload.get("candles")
    if not isinstance(raw_candles, list):
        return None, [_reject("UNKNOWN_CANDLE_SCHEMA", source_har, session_index, frame_index, "candles missing")]
    by_timestamp = {}
    for raw in raw_candles:
        candle, error = normalize_candle(raw, asset=asset, period=period, source_event="updateHistoryNewFast", source_har=source_har, session_index=session_index)
        if error:
            rejections.append(_reject(error, source_har, session_index, frame_index, "raw candle rejected"))
            continue
        assert candle is not None
        by_timestamp[candle.timestamp] = candle
    candles = tuple(sorted(by_timestamp.values(), key=lambda item: item.timestamp))
    return (
        PocketHistoryBatch(
            asset=asset,
            period=period,
            timeframe=timeframe,
            candles=candles,
            history_count=len(payload.get("history") or []),
            first_timestamp=candles[0].timestamp if candles else None,
            last_timestamp=candles[-1].timestamp if candles else None,
            source_event="updateHistoryNewFast",
        ),
        rejections,
    )


def _reject(code: str, source_har: str, session_index: int, frame_index: int, detail: str) -> Rejection:
    return Rejection(code=code, event_name="updateHistoryNewFast", source_har=source_har, session_index=session_index, frame_index=frame_index, detail=detail)

