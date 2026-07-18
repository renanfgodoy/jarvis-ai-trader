from __future__ import annotations

from typing import Any

from app.market.providers.polarium.models import (
    POLARIUM_PLURAL_EVENT,
    POLARIUM_SINGULAR_EVENT,
    POLARIUM_SUPPORTED_SIZES,
    PolariumMarketCandle,
    PolariumMarketEvent,
)

POLARIUM_HISTORY_EVENTS = {"first-candles", "candles"}


class PolariumMarketEventParseError(ValueError):
    pass


class PolariumMarketFeedParser:
    def parse(
        self,
        message: dict[str, Any],
        *,
        default_active_id: int | None = None,
        default_raw_size: int | None = None,
    ) -> PolariumMarketEvent:
        event_name = _event_name(message)
        if event_name == POLARIUM_PLURAL_EVENT:
            return _parse_candles_generated(message)
        if event_name == POLARIUM_SINGULAR_EVENT:
            return _parse_candle_generated(message)
        if event_name in POLARIUM_HISTORY_EVENTS:
            return _parse_history_candles(
                message,
                event_name=event_name,
                default_active_id=default_active_id,
                default_raw_size=default_raw_size,
            )
        raise PolariumMarketEventParseError("UNSUPPORTED_MARKET_EVENT")


def _parse_candles_generated(message: dict[str, Any]) -> PolariumMarketEvent:
    body = _message_body(message)
    active_id = _as_int(body.get("active_id")) or _find_first_int(message, {"active_id", "activeId"})
    if active_id is None:
        raise PolariumMarketEventParseError("MISSING_ACTIVE_ID")
    close = _as_float(body.get("value"))
    if close is None:
        raise PolariumMarketEventParseError("MISSING_NUMERIC_FIELD:value")
    candles_by_size = body.get("candles") or _find_first_dict(message, {"candles"})
    if not isinstance(candles_by_size, dict):
        raise PolariumMarketEventParseError("MISSING_CANDLES")
    symbol = _find_symbol(message)
    candles = []
    for raw_size in POLARIUM_SUPPORTED_SIZES:
        candle = candles_by_size.get(str(raw_size)) or candles_by_size.get(raw_size)
        if isinstance(candle, dict):
            candles.append(_parse_candle(active_id=active_id, symbol=symbol, raw_size=raw_size, candle=candle, close_override=close))
    if not candles:
        raise PolariumMarketEventParseError("NO_SUPPORTED_TIMEFRAMES")
    return PolariumMarketEvent(
        event_name=POLARIUM_PLURAL_EVENT,
        active_id=active_id,
        symbol=symbol,
        timestamp=_as_int(body.get("at")),
        bid=_as_float(body.get("bid")),
        ask=_as_float(body.get("ask")),
        value=_as_float(body.get("value")),
        candles=tuple(candles),
    )


def _parse_candle_generated(message: dict[str, Any]) -> PolariumMarketEvent:
    body = _message_body(message)
    active_id = _as_int(body.get("active_id"))
    raw_size = _as_int(body.get("size"))
    if active_id is None or raw_size is None:
        raise PolariumMarketEventParseError("MISSING_ACTIVE_ID_OR_SIZE")
    symbol = _find_symbol(message)
    candle = _parse_candle(active_id=active_id, symbol=symbol, raw_size=raw_size, candle=body)
    return PolariumMarketEvent(
        event_name=POLARIUM_SINGULAR_EVENT,
        active_id=active_id,
        symbol=symbol,
        timestamp=_as_int(body.get("at")) or _as_int(body.get("from")),
        bid=None,
        ask=None,
        value=None,
        candles=(candle,),
    )


def _parse_history_candles(
    message: dict[str, Any],
    *,
    event_name: str,
    default_active_id: int | None = None,
    default_raw_size: int | None = None,
) -> PolariumMarketEvent:
    body = _message_body(message)
    active_id = _as_int(body.get("active_id")) or _find_first_int(message, {"active_id", "activeId"}) or default_active_id
    if active_id is None:
        raise PolariumMarketEventParseError("MISSING_ACTIVE_ID")
    symbol = _find_symbol(message)
    candles: list[PolariumMarketCandle] = []
    raw_list = body.get("candles")
    if isinstance(raw_list, list):
        for candle in raw_list:
            if not isinstance(candle, dict):
                continue
            raw_size = _as_int(candle.get("size")) or _as_int(body.get("size")) or default_raw_size
            if raw_size in POLARIUM_SUPPORTED_SIZES:
                candles.append(_parse_candle(active_id=active_id, symbol=symbol or _find_symbol(candle), raw_size=raw_size, candle=candle, validate_history_alignment=True))
    else:
        candles_by_size = _history_candles_by_size(body)
        if isinstance(candles_by_size, dict):
            sizes = (default_raw_size,) if default_raw_size in POLARIUM_SUPPORTED_SIZES else POLARIUM_SUPPORTED_SIZES
            for raw_size in sizes:
                candle = candles_by_size.get(str(raw_size)) or candles_by_size.get(raw_size)
                if isinstance(candle, dict):
                    candles.append(_parse_candle(active_id=active_id, symbol=symbol or _find_symbol(candle), raw_size=raw_size, candle=candle, validate_history_alignment=True))
    if not candles:
        raise PolariumMarketEventParseError("NO_SUPPORTED_HISTORY_CANDLES")
    candles = _sorted_unique_candles(candles)
    return PolariumMarketEvent(
        event_name=event_name,
        active_id=active_id,
        symbol=symbol,
        timestamp=_as_int(body.get("at")) or candles[-1].start_timestamp,
        bid=_as_float(body.get("bid")),
        ask=_as_float(body.get("ask")),
        value=_as_float(body.get("value")),
        candles=tuple(candles),
    )


def _parse_candle(
    *,
    active_id: int,
    symbol: str | None,
    raw_size: int,
    candle: dict[str, Any],
    close_override: float | None = None,
    validate_history_alignment: bool = False,
) -> PolariumMarketCandle:
    start = _as_int(candle.get("from"))
    if start is None:
        raise PolariumMarketEventParseError("MISSING_CANDLE_START")
    if validate_history_alignment and raw_size in {300, 900} and start % raw_size != 0:
        raise PolariumMarketEventParseError("DROP_INVALID_HISTORICAL_TIMESTAMP")
    end = _as_int(candle.get("to")) or start + raw_size
    open_price = _required_float(candle, "open")
    close = close_override if close_override is not None else _required_float(candle, "close")
    raw_low = _required_float(candle, "min", "low")
    raw_high = _required_float(candle, "max", "high")
    low = min(raw_low, open_price, close)
    high = max(raw_high, open_price, close)
    if high < low:
        raise PolariumMarketEventParseError("INVALID_OHLC_RANGE")
    return PolariumMarketCandle(
        active_id=active_id,
        symbol=symbol,
        raw_size=raw_size,
        start_timestamp=start,
        end_timestamp=end,
        open=open_price,
        close=close,
        low=low,
        high=high,
        volume=_as_float(candle.get("volume")) or 0.0,
    )


def _event_name(message: dict[str, Any]) -> str | None:
    name = message.get("name")
    if isinstance(name, str) and name != "sendMessage":
        return name
    msg = message.get("msg")
    if isinstance(msg, dict) and isinstance(msg.get("name"), str):
        return msg["name"]
    return name if isinstance(name, str) else None


def _message_body(message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return message if any(key in message for key in ("active_id", "candles", "candles_by_size", "data")) else {}
    body = msg.get("body")
    if isinstance(body, dict):
        return body
    result = msg.get("result")
    if isinstance(result, dict):
        return result
    data = msg.get("data")
    if isinstance(data, dict):
        return data
    if any(key in msg for key in ("active_id", "candles", "candles_by_size", "data", "value", "bid", "ask")):
        return msg
    return {}


def _required_float(candle: dict[str, Any], *names: str) -> float:
    for name in names:
        value = _as_float(candle.get(name))
        if value is not None:
            return value
    raise PolariumMarketEventParseError(f"MISSING_NUMERIC_FIELD:{'/'.join(names)}")


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _find_symbol(value: Any) -> str | None:
    if isinstance(value, dict):
        for key in ("symbol", "ticker", "display_name", "displayName"):
            parsed = _as_symbol(value.get(key))
            if parsed is not None:
                return parsed
        for item in value.values():
            parsed = _find_symbol(item)
            if parsed is not None:
                return parsed
    if isinstance(value, list):
        for item in value:
            parsed = _find_symbol(item)
            if parsed is not None:
                return parsed
    return None


def _as_symbol(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = " ".join(value.strip().split())
    if not parsed or len(parsed) > 80:
        return None
    lowered = parsed.lower()
    if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password")):
        return None
    return parsed


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _find_first_int(value: Any, keys: set[str]) -> int | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys:
                parsed = _as_int(item)
                if parsed is not None:
                    return parsed
            parsed = _find_first_int(item, keys)
            if parsed is not None:
                return parsed
    if isinstance(value, list):
        for item in value:
            parsed = _find_first_int(item, keys)
            if parsed is not None:
                return parsed
    return None


def _find_first_dict(value: Any, keys: set[str]) -> dict[str, Any] | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys and isinstance(item, dict):
                return item
            parsed = _find_first_dict(item, keys)
            if parsed is not None:
                return parsed
    if isinstance(value, list):
        for item in value:
            parsed = _find_first_dict(item, keys)
            if parsed is not None:
                return parsed
    return None


def _history_candles_by_size(body: dict[str, Any]) -> dict[str, Any] | None:
    candles_by_size = body.get("candles_by_size") or body.get("candles")
    if isinstance(candles_by_size, dict):
        return candles_by_size
    if any((body.get(str(size)) or body.get(size)) for size in POLARIUM_SUPPORTED_SIZES):
        return body
    return None


def _sorted_unique_candles(candles: list[PolariumMarketCandle]) -> list[PolariumMarketCandle]:
    by_key: dict[tuple[int, int], PolariumMarketCandle] = {}
    for candle in candles:
        by_key[(candle.raw_size, candle.start_timestamp)] = candle
    return [by_key[key] for key in sorted(by_key)]
