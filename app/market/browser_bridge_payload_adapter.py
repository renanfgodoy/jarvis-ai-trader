from __future__ import annotations

from typing import Any

POLARIUM_AUTHORIZED_BROWSER_SOURCE = "POLARIUM_AUTHORIZED_BROWSER"
POLARIUM_AUTHORIZED_BROWSER_LABEL = "POLARIUM AUTHORIZED BROWSER LIVE"
CANDLE_GENERATED_REQUIRED = ("active_id", "size", "from", "to", "open", "close", "min", "max")
FIRST_CANDLES_REQUIRED = ("from", "to", "open", "close", "min", "max")

FIELD_ALIASES = {
    "active_id": ("active_id", "activeId", "active", "asset_id"),
    "size": ("size", "raw_size", "rawSize", "timeframe_size"),
    "from": ("from", "timestamp", "start_timestamp", "startTimestamp", "start", "at"),
    "to": ("to", "end_timestamp", "endTimestamp", "end"),
    "open": ("open", "o"),
    "close": ("close", "c"),
    "min": ("min", "low", "l"),
    "max": ("max", "high", "h"),
    "volume": ("volume", "v"),
}


def adapt_browser_bridge_payload(event_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Convert sanitized Browser Bridge payloads to the MarketPipeline contract."""

    message = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    if event_name == "candle-generated":
        body = _canonical_candle_generated_body(message)
    elif event_name == "first-candles":
        body = _canonical_first_candles_body(message)
    else:
        body = _extract_candidate_body(event_name, message)

    return {
        "name": event_name,
        "source": POLARIUM_AUTHORIZED_BROWSER_SOURCE,
        "data_classification": POLARIUM_AUTHORIZED_BROWSER_LABEL,
        "msg": {"body": body},
    }


def _canonical_candle_generated_body(message: dict[str, Any]) -> dict[str, Any]:
    candidate = _extract_candidate_body("candle-generated", message)
    canonical = _canonical_fields(candidate, CANDLE_GENERATED_REQUIRED)
    if "volume" in candidate:
        canonical["volume"] = candidate["volume"]
    else:
        volume = _first_present(candidate, FIELD_ALIASES["volume"])
        if volume is not None:
            canonical["volume"] = volume
    return canonical


def _canonical_first_candles_body(message: dict[str, Any]) -> dict[str, Any]:
    candidate = _extract_candidate_body("first-candles", message)
    candles_by_size = candidate.get("candles_by_size")
    if not isinstance(candles_by_size, dict):
        return dict(candidate)

    canonical: dict[str, Any] = {"candles_by_size": {}}
    active_id = _first_present(candidate, FIELD_ALIASES["active_id"])
    if active_id is not None:
        canonical["active_id"] = active_id

    for raw_size, candle in candles_by_size.items():
        if not isinstance(candle, dict):
            canonical["candles_by_size"][raw_size] = candle
            continue
        normalized = _canonical_fields(candle, FIRST_CANDLES_REQUIRED)
        volume = _first_present(candle, FIELD_ALIASES["volume"])
        if volume is not None:
            normalized["volume"] = volume
        canonical["candles_by_size"][raw_size] = normalized
    return canonical


def _extract_candidate_body(event_name: str, message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if isinstance(msg, dict):
        body = msg.get("body")
        if isinstance(body, dict):
            return dict(body)
        if event_name == "first-candles" and isinstance(msg.get("candles_by_size"), dict):
            return dict(msg)
        if _looks_like_market_candle(msg):
            return dict(msg)

    data = message.get("data")
    if isinstance(data, dict) and _looks_like_market_candle(data):
        return dict(data)

    params = message.get("params")
    if isinstance(params, dict) and _looks_like_market_candle(params):
        return dict(params)

    if event_name == "first-candles" and isinstance(message.get("candles_by_size"), dict):
        return dict(message)
    return {key: value for key, value in message.items() if key not in {"source", "data_classification", "event_name", "name"}}


def _canonical_fields(source: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    for field in fields:
        value = _first_present(source, FIELD_ALIASES[field])
        if value is not None:
            canonical[field] = value
    return canonical


def _first_present(source: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in source:
            return source[name]
    return None


def _looks_like_market_candle(value: dict[str, Any]) -> bool:
    has_price = any(name in value for name in FIELD_ALIASES["open"]) and any(name in value for name in FIELD_ALIASES["close"])
    has_range = any(name in value for name in FIELD_ALIASES["min"]) and any(name in value for name in FIELD_ALIASES["max"])
    has_time = any(name in value for name in FIELD_ALIASES["from"]) and any(name in value for name in FIELD_ALIASES["to"])
    return has_price and has_range and has_time
