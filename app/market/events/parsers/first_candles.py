from __future__ import annotations

from typing import Any

from app.market.events import event_types
from app.market.events.models import MarketEventParseError, NormalizedMarketCandle
from app.market.events.parsers.candle_generated import _as_float, _as_int, _as_symbol, _is_int_like, _is_number

REQUIRED_CANDLE_FIELDS = ("from", "to", "open", "close", "min", "max")


def parse_first_candles(message: dict[str, Any]) -> tuple[tuple[NormalizedMarketCandle, ...], tuple[MarketEventParseError, ...]]:
    body = _extract_body(message)
    if not body:
        return (), (
            MarketEventParseError(
                code="missing_body",
                message="Expected first-candles payload at msg.body.",
                path="$.msg.body",
            ),
        )

    candles = body.get("candles")
    if isinstance(candles, list):
        return _parse_candles_list(body, candles)

    active_id = body.get("active_id")
    body_symbol = _as_symbol(body.get("symbol"))
    candles_by_size = body.get("candles_by_size")
    if not isinstance(candles_by_size, dict):
        return (), (
            MarketEventParseError(
                code="missing_candles_collection",
                message="Expected first-candles msg.body.candles or msg.body.candles_by_size collection.",
                path="$.msg.body",
            ),
        )

    normalized: list[NormalizedMarketCandle] = []
    errors: list[MarketEventParseError] = []
    for raw_size, candle in candles_by_size.items():
        size_path = f"$.msg.body.candles_by_size.{raw_size}"
        if not _is_size_key(raw_size):
            errors.append(
                MarketEventParseError(
                    code="invalid_size",
                    message="Expected candles_by_size key to be integer-compatible.",
                    path=size_path,
                )
            )
            continue
        if not isinstance(candle, dict):
            errors.append(
                MarketEventParseError(
                    code="invalid_candle",
                    message="Expected candle item to be an object.",
                    path=size_path,
                )
            )
            continue
        item_errors = _validate_candle(candle, size_path)
        if item_errors:
            errors.extend(item_errors)
            continue
        normalized.append(
            NormalizedMarketCandle(
                active_id=_as_int(active_id) if _is_int_like(active_id) else None,
                symbol=_as_symbol(candle.get("symbol")) or body_symbol,
                raw_size=_as_int(raw_size),
                timeframe=None,
                start_timestamp=_as_int(candle["from"]),
                end_timestamp=_as_int(candle["to"]),
                open=_as_float(candle["open"]),
                close=_as_float(candle["close"]),
                low_candidate=_as_float(candle["min"]),
                high_candidate=_as_float(candle["max"]),
                volume=_as_float(candle.get("volume", 0)),
                source="polarium",
                source_event=event_types.FIRST_CANDLES,
                source_verified=True,
                mapping_verified=False,
                mapping_notes=(
                    "candles_by_size key is provider-native and is not mapped to a visual timeframe yet.",
                    "first-candles response may not include active_id; keep it None unless observed in payload.",
                    "min is preserved as a low candidate, not a verified low mapping.",
                    "max is preserved as a high candidate, not a verified high mapping.",
                ),
            )
        )
    return tuple(normalized), tuple(errors)


def _parse_candles_list(body: dict[str, Any], candles: list[Any]) -> tuple[tuple[NormalizedMarketCandle, ...], tuple[MarketEventParseError, ...]]:
    normalized: list[NormalizedMarketCandle] = []
    errors: list[MarketEventParseError] = []
    body_active_id = body.get("active_id")
    body_raw_size = body.get("size")
    body_symbol = _as_symbol(body.get("symbol"))

    for index, candle in enumerate(candles):
        path = f"$.msg.body.candles.{index}"
        if not isinstance(candle, dict):
            errors.append(
                MarketEventParseError(
                    code="invalid_candle",
                    message="Expected candle item to be an object.",
                    path=path,
                )
            )
            continue
        candle_with_defaults = dict(candle)
        if "active_id" not in candle_with_defaults and body_active_id is not None:
            candle_with_defaults["active_id"] = body_active_id
        if "size" not in candle_with_defaults and body_raw_size is not None:
            candle_with_defaults["size"] = body_raw_size
        item_errors = _validate_candle_list_item(candle_with_defaults, path)
        if item_errors:
            errors.extend(item_errors)
            continue
        normalized.append(
            NormalizedMarketCandle(
                active_id=_as_int(candle_with_defaults["active_id"]) if _is_int_like(candle_with_defaults.get("active_id")) else None,
                symbol=_as_symbol(candle_with_defaults.get("symbol")) or body_symbol,
                raw_size=_as_int(candle_with_defaults["size"]),
                timeframe=None,
                start_timestamp=_as_int(candle_with_defaults["from"]),
                end_timestamp=_as_int(candle_with_defaults["to"]),
                open=_as_float(candle_with_defaults["open"]),
                close=_as_float(candle_with_defaults["close"]),
                low_candidate=_as_float(candle_with_defaults["min"]),
                high_candidate=_as_float(candle_with_defaults["max"]),
                volume=_as_float(candle_with_defaults.get("volume", 0)),
                source="polarium",
                source_event=event_types.FIRST_CANDLES,
                source_verified=True,
                mapping_verified=False,
                mapping_notes=(
                    "first-candles candles list is provider-native and is not mapped to a visual timeframe yet.",
                    "min is preserved as a low candidate, not a verified low mapping.",
                    "max is preserved as a high candidate, not a verified high mapping.",
                ),
            )
        )
    return tuple(normalized), tuple(errors)


def _extract_body(message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return {}
    body = msg.get("body")
    if not isinstance(body, dict):
        return {}
    return body


def _validate_candle(candle: dict[str, Any], path: str) -> tuple[MarketEventParseError, ...]:
    errors: list[MarketEventParseError] = []
    for field in REQUIRED_CANDLE_FIELDS:
        if field not in candle:
            errors.append(
                MarketEventParseError(
                    code="missing_field",
                    message=f"Missing required first-candles field: {field}.",
                    path=f"{path}.{field}",
                )
            )
            continue
        if field in {"from", "to"} and not _is_int_like(candle[field]):
            errors.append(
                MarketEventParseError(
                    code="invalid_integer",
                    message=f"Expected integer-compatible value for {field}.",
                    path=f"{path}.{field}",
                )
            )
        if field in {"open", "close", "min", "max"} and not _is_number(candle[field]):
            errors.append(
                MarketEventParseError(
                    code="invalid_number",
                    message=f"Expected numeric value for {field}.",
                    path=f"{path}.{field}",
                )
            )
    if "volume" in candle and not _is_number(candle["volume"]):
        errors.append(
            MarketEventParseError(
                code="invalid_number",
                message="Expected numeric value for volume.",
                path=f"{path}.volume",
            )
        )
    if "symbol" in candle and _as_symbol(candle.get("symbol")) is None:
        errors.append(
            MarketEventParseError(
                code="invalid_symbol",
                message="Expected sanitized market symbol when symbol is present.",
                path=f"{path}.symbol",
            )
        )
    return tuple(errors)


def _validate_candle_list_item(candle: dict[str, Any], path: str) -> tuple[MarketEventParseError, ...]:
    errors = list(_validate_candle(candle, path))
    if "size" not in candle:
        errors.append(
            MarketEventParseError(
                code="missing_field",
                message="Missing required first-candles field: size.",
                path=f"{path}.size",
            )
        )
    elif not _is_int_like(candle["size"]):
        errors.append(
            MarketEventParseError(
                code="invalid_integer",
                message="Expected integer-compatible value for size.",
                path=f"{path}.size",
            )
        )
    return tuple(errors)


def _is_size_key(value: Any) -> bool:
    if isinstance(value, int) and not isinstance(value, bool):
        return True
    if isinstance(value, str) and value.isdigit():
        return True
    return False
