from __future__ import annotations

from typing import Any

from tools.pocket_parser.models import PocketRealtimeTick
from tools.pocket_parser.utils import finite_positive_float, finite_timestamp


def normalize_tick(raw: Any, *, sequence: int, source_har: str, session_index: int) -> tuple[PocketRealtimeTick | None, str | None]:
    if not isinstance(raw, list) or len(raw) < 3:
        return None, "UNKNOWN_TICK_SCHEMA"
    asset = raw[0]
    if not isinstance(asset, str) or not asset:
        return None, "MISSING_ASSET"
    timestamp = finite_timestamp(raw[1])
    if timestamp is None:
        return None, "INVALID_TIMESTAMP"
    price = finite_positive_float(raw[2])
    if price is None:
        return None, "INVALID_PRICE"
    return (
        PocketRealtimeTick(
            asset=asset,
            price=price,
            timestamp=timestamp,
            source_event="updateStream",
            sequence=sequence,
            source_har=source_har,
            session_index=session_index,
        ),
        None,
    )

