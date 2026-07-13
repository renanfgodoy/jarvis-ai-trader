from __future__ import annotations

from typing import Any

from app.market.events import event_types
from app.market.events.models import MarketEventParseError, NormalizedMarketCandle

REQUIRED_FIELDS = ("active_id", "size", "from", "to", "open", "close", "min", "max")


def parse_candle_generated(message: dict[str, Any]) -> tuple[NormalizedMarketCandle, ...]:
    body = _extract_body(message)
    errors = _validate_body(body, "$.msg.body")
    if errors:
        raise CandleGeneratedParseFailure(errors)

    return (
        NormalizedMarketCandle(
            active_id=_as_int(body["active_id"]),
            symbol=_as_symbol(body.get("symbol")),
            raw_size=_as_int(body["size"]),
            timeframe=None,
            start_timestamp=_as_int(body["from"]),
            end_timestamp=_as_int(body["to"]),
            open=_as_float(body["open"]),
            close=_as_float(body["close"]),
            low_candidate=_as_float(body["min"]),
            high_candidate=_as_float(body["max"]),
            volume=_as_float(body.get("volume", 0)),
            source="polarium",
            source_event=event_types.CANDLE_GENERATED,
            source_verified=True,
            mapping_verified=False,
            mapping_notes=(
                "active_id is provider-native and is not mapped to a visual symbol yet.",
                "size is provider-native and is not mapped to a visual timeframe yet.",
                "min is preserved as a low candidate, not a verified low mapping.",
                "max is preserved as a high candidate, not a verified high mapping.",
            ),
        ),
    )


class CandleGeneratedParseFailure(ValueError):
    def __init__(self, errors: tuple[MarketEventParseError, ...]) -> None:
        super().__init__("Invalid candle-generated payload")
        self.errors = errors


def _extract_body(message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return {}
    body = msg.get("body")
    if not isinstance(body, dict):
        return {}
    return body


def _validate_body(body: dict[str, Any], path: str) -> tuple[MarketEventParseError, ...]:
    if not body:
        return (
            MarketEventParseError(
                code="missing_body",
                message="Expected candle-generated payload at msg.body.",
                path=path,
            ),
        )

    errors: list[MarketEventParseError] = []
    for field in REQUIRED_FIELDS:
        if field not in body:
            errors.append(
                MarketEventParseError(
                    code="missing_field",
                    message=f"Missing required candle field: {field}.",
                    path=f"{path}.{field}",
                )
            )
            continue
        if field in {"active_id", "size", "from", "to"} and not _is_int_like(body[field]):
            errors.append(
                MarketEventParseError(
                    code="invalid_integer",
                    message=f"Expected integer-compatible value for {field}.",
                    path=f"{path}.{field}",
                )
            )
        if field in {"open", "close", "min", "max"} and not _is_number(body[field]):
            errors.append(
                MarketEventParseError(
                    code="invalid_number",
                    message=f"Expected numeric value for {field}.",
                    path=f"{path}.{field}",
                )
            )
    if "volume" in body and not _is_number(body["volume"]):
        errors.append(
            MarketEventParseError(
                code="invalid_number",
                message="Expected numeric value for volume.",
                path=f"{path}.volume",
            )
        )
    if "symbol" in body and _as_symbol(body.get("symbol")) is None:
        errors.append(
            MarketEventParseError(
                code="invalid_symbol",
                message="Expected sanitized market symbol when symbol is present.",
                path=f"{path}.symbol",
            )
        )
    return tuple(errors)


def _is_int_like(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _as_int(value: Any) -> int:
    return int(value)


def _as_float(value: Any) -> float:
    return float(value)


def _as_symbol(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = " ".join(value.strip().split())
    if len(stripped) < 2 or len(stripped) > 40:
        return None
    lowered = stripped.lower()
    if any(marker in lowered for marker in ("token", "cookie", "authorization", "bearer", "ssid", "password", "credential")):
        return None
    if not any(char.isalpha() for char in stripped):
        return None
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/._ -")
    if any(char not in allowed for char in stripped):
        return None
    return stripped
