from __future__ import annotations

from typing import Any

from app.market.events import event_types
from app.market.events.models import MarketEventMetadata, MarketEventParseError, MarketEventRouteResult
from app.market.events.parsers.candle_generated import CandleGeneratedParseFailure, parse_candle_generated
from app.market.events.parsers.first_candles import parse_first_candles


def route_market_event(message: dict[str, Any]) -> MarketEventRouteResult:
    event_name = _event_name(message)
    metadata = MarketEventMetadata(
        source="polarium",
        event_name=event_name,
        request_id=_request_id(message),
    )

    if event_name is None:
        return MarketEventRouteResult(
            status="invalid",
            metadata=metadata,
            errors=(
                MarketEventParseError(
                    code="missing_event_name",
                    message="Expected market event name in name or msg.name.",
                    path="$.name",
                ),
            ),
            raw_event=message,
        )

    if event_name not in event_types.SUPPORTED_EVENTS:
        return MarketEventRouteResult(
            status="unsupported",
            metadata=metadata,
            errors=(
                MarketEventParseError(
                    code="unsupported_event",
                    message=f"Unsupported market event: {event_name}.",
                    path="$.name",
                ),
            ),
            raw_event=message,
        )

    if event_name == event_types.CANDLE_GENERATED:
        try:
            candles = parse_candle_generated(message)
        except CandleGeneratedParseFailure as exc:
            return MarketEventRouteResult(status="invalid", metadata=metadata, errors=exc.errors, raw_event=message)
        return MarketEventRouteResult(status="parsed", metadata=metadata, candles=candles)

    if event_name == event_types.FIRST_CANDLES:
        candles, errors = parse_first_candles(message)
        status = "parsed" if candles else "invalid"
        return MarketEventRouteResult(status=status, metadata=metadata, candles=candles, errors=errors, raw_event=None if candles else message)

    return MarketEventRouteResult(
        status="unsupported",
        metadata=metadata,
        errors=(
            MarketEventParseError(
                code="event_not_parsed",
                message=f"Event is known but has no candle parser: {event_name}.",
                path="$.name",
            ),
        ),
        raw_event=message,
    )


def _event_name(message: dict[str, Any]) -> str | None:
    name = message.get("name")
    if isinstance(name, str) and name != "sendMessage":
        return name
    msg = message.get("msg")
    if isinstance(msg, dict) and isinstance(msg.get("name"), str):
        return msg["name"]
    return name if isinstance(name, str) else None


def _request_id(message: dict[str, Any]) -> str | None:
    request_id = message.get("request_id")
    if request_id is None:
        return None
    return str(request_id)
