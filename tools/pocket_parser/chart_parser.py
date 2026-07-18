from __future__ import annotations

import json
from typing import Any

from tools.pocket_discovery.sanitizer import sanitize


def audit_update_charts(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []
    updates: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        settings_raw = item.get("settings")
        settings = {}
        if isinstance(settings_raw, str):
            try:
                parsed = json.loads(settings_raw)
                settings = parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                settings = {}
        updates.append(
            sanitize(
                {
                    "chart_id": item.get("chart_id"),
                    "contains_candles": False,
                    "contains_visual_state": bool(settings),
                    "symbol": settings.get("symbol"),
                    "chart_period": settings.get("chartPeriod"),
                    "fast_timeframe": settings.get("fastTimeframe"),
                    "settings_keys": sorted(settings.keys()),
                }
            )
        )
    return updates

