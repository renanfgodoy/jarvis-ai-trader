from __future__ import annotations

import math
from typing import Any

from tools.pocket_parser.models import SUPPORTED_PERIODS, MarketType


def timeframe_for_period(period: int) -> str:
    if period not in SUPPORTED_PERIODS:
        raise ValueError("UNSUPPORTED_PERIOD")
    return SUPPORTED_PERIODS[period]


def display_name_for_asset(asset: str) -> str:
    name = asset.replace("_otc", " OTC").replace("_", " ")
    return name.upper() if len(name) <= 12 else name


def market_type_for_asset(asset: str) -> MarketType:
    return "OTC" if asset.lower().endswith("_otc") else "REGULAR"


def finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def finite_positive_float(value: Any) -> float | None:
    number = finite_float(value)
    if number is None or number <= 0:
        return None
    return number


def finite_timestamp(value: Any) -> float | None:
    number = finite_float(value)
    if number is None or number <= 0:
        return None
    return number

