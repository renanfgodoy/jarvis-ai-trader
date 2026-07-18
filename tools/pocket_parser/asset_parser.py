from __future__ import annotations

from typing import Any

from tools.pocket_parser.models import PocketAssetChanged, PocketAssetInfo
from tools.pocket_parser.utils import display_name_for_asset, market_type_for_asset, timeframe_for_period


def parse_change_symbol(payload: Any, timestamp: float | None = None) -> PocketAssetChanged:
    if not isinstance(payload, dict):
        raise ValueError("INVALID_PAYLOAD")
    asset = payload.get("asset")
    period = payload.get("period")
    if not isinstance(asset, str) or not asset:
        raise ValueError("MISSING_ASSET")
    if not isinstance(period, int):
        raise ValueError("MISSING_PERIOD")
    timeframe = timeframe_for_period(period)
    market_type = market_type_for_asset(asset)
    return PocketAssetChanged(
        asset=asset,
        display_name=display_name_for_asset(asset),
        market_type=market_type,
        is_otc=market_type == "OTC",
        period=period,
        timeframe=timeframe,
        timestamp=timestamp,
    )


def parse_update_assets(payload: Any) -> list[PocketAssetInfo]:
    if not isinstance(payload, list):
        return []
    assets: list[PocketAssetInfo] = []
    for row in payload:
        if not isinstance(row, list) or len(row) < 3:
            continue
        symbol = row[1] if isinstance(row[1], str) else None
        display_name = row[2] if isinstance(row[2], str) else None
        if not symbol or not display_name:
            continue
        supported_periods = tuple(
            int(item.get("time"))
            for item in (row[15] if len(row) > 15 and isinstance(row[15], list) else [])
            if isinstance(item, dict) and isinstance(item.get("time"), int)
        )
        numeric_fields = tuple(index for index, value in enumerate(row) if isinstance(value, (int, float)) and not isinstance(value, bool))
        boolean_fields = tuple(index for index, value in enumerate(row) if isinstance(value, bool))
        is_otc = symbol.lower().endswith("_otc")
        assets.append(
            PocketAssetInfo(
                symbol=symbol.lstrip("#"),
                display_name=display_name,
                is_otc=is_otc,
                market_type="OTC" if is_otc else "REGULAR",
                is_available=None,
                payout=None,
                supported_periods=supported_periods,
                raw_fields_detected=tuple(f"index_{index}:{type(value).__name__}" for index, value in enumerate(row)),
                unknown_numeric_fields=numeric_fields,
                unknown_boolean_fields=boolean_fields,
            )
        )
    return assets

