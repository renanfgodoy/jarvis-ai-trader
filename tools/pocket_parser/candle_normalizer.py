from __future__ import annotations

from typing import Any

from tools.pocket_parser.models import PocketNormalizedCandle
from tools.pocket_parser.utils import finite_positive_float, finite_timestamp, timeframe_for_period

CANDLE_SCHEMA = "TIMESTAMP_OPEN_CLOSE_HIGH_LOW_VOLUME"


def normalize_candle(
    raw: Any,
    *,
    asset: str,
    period: int,
    source_event: str,
    source_har: str,
    session_index: int,
) -> tuple[PocketNormalizedCandle | None, str | None]:
    if not isinstance(raw, list) or len(raw) < 5:
        return None, "UNKNOWN_CANDLE_SCHEMA"
    timestamp = finite_timestamp(raw[0])
    if timestamp is None:
        return None, "INVALID_TIMESTAMP"
    open_price = finite_positive_float(raw[1])
    close_price = finite_positive_float(raw[2])
    high_price = finite_positive_float(raw[3])
    low_price = finite_positive_float(raw[4])
    if None in {open_price, close_price, high_price, low_price}:
        return None, "INVALID_PRICE"
    if high_price < low_price or high_price < open_price or high_price < close_price or low_price > open_price or low_price > close_price:
        return None, "INVALID_OHLC"
    volume = None
    if len(raw) > 5:
        volume = finite_positive_float(raw[5])
    try:
        timeframe = timeframe_for_period(period)
    except ValueError:
        return None, "UNSUPPORTED_PERIOD"
    return (
        PocketNormalizedCandle(
            provider="POCKET",
            symbol=asset,
            period=period,
            timeframe=timeframe,
            timestamp=timestamp,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume,
            is_closed=True,
            source_event=source_event,
            source_har=source_har,
            session_index=session_index,
        ),
        None,
    )

