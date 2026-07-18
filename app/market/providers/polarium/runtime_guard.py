from __future__ import annotations

from typing import Any, Literal

InboundDecision = Literal["allow", "drop", "forbidden"]

ALLOWED_OUTBOUND = {
    ("subscribeMessage", "candles-generated"),
    ("unsubscribeMessage", "candles-generated"),
    ("subscribeMessage", "candle-generated"),
    ("unsubscribeMessage", "candle-generated"),
    ("sendMessage", "get-first-candles"),
    ("sendMessage", "get-candles"),
}
ALLOWED_INBOUND = {
    "authenticated",
    "timeSync",
    "first-candles",
    "candles",
    "candle-generated",
    "candles-generated",
}
FORBIDDEN_TERMS = (
    "order",
    "buy",
    "sell",
    "position",
    "portfolio",
    "balance",
    "account",
    "payment",
    "deposit",
    "withdrawal",
)


class PolariumRuntimeGuardViolation(RuntimeError):
    pass


class PolariumRuntimeGuard:
    """Read-only allowlist for Polarium market messages."""

    def validate_outbound(self, message: dict[str, Any]) -> None:
        if _contains_forbidden_name(message):
            raise PolariumRuntimeGuardViolation("FORBIDDEN_OUTBOUND")
        envelope = (_message_name(message), _inner_name(message))
        if envelope not in ALLOWED_OUTBOUND:
            raise PolariumRuntimeGuardViolation("OUTBOUND_NOT_ALLOWED")
        if envelope[1] == "candles-generated":
            active_id = _active_id(message)
            filters = _routing_filters(message)
            if active_id is None or "size" in filters:
                raise PolariumRuntimeGuardViolation("INVALID_CANDLES_GENERATED_SUBSCRIPTION")
        if envelope[1] == "candle-generated":
            active_id = _active_id(message)
            size = _size(message)
            if active_id is None or size not in {60, 300, 900}:
                raise PolariumRuntimeGuardViolation("INVALID_CANDLE_GENERATED_SUBSCRIPTION")
        if envelope[1] == "get-candles":
            active_id = _active_id(message)
            size = _size(message)
            if active_id is None or size not in {60, 300, 900}:
                raise PolariumRuntimeGuardViolation("INVALID_GET_CANDLES_REQUEST")

    def classify_inbound(self, message: dict[str, Any]) -> InboundDecision:
        if _contains_forbidden_name(message):
            return "forbidden"
        name = _event_name(message)
        return "allow" if name in ALLOWED_INBOUND else "drop"


def _event_name(message: dict[str, Any]) -> str | None:
    name = _message_name(message)
    if name and name != "sendMessage":
        return name
    return _inner_name(message) or name


def _message_name(message: dict[str, Any]) -> str | None:
    value = message.get("name")
    return value if isinstance(value, str) else None


def _inner_name(message: dict[str, Any]) -> str | None:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return None
    value = msg.get("name")
    return value if isinstance(value, str) else None


def _routing_filters(message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return {}
    params = msg.get("params")
    if not isinstance(params, dict):
        return {}
    filters = params.get("routingFilters")
    return filters if isinstance(filters, dict) else {}


def _body(message: dict[str, Any]) -> dict[str, Any]:
    msg = message.get("msg")
    if not isinstance(msg, dict):
        return {}
    body = msg.get("body")
    return body if isinstance(body, dict) else {}


def _active_id(message: dict[str, Any]) -> int | None:
    return _as_int(_routing_filters(message).get("active_id")) or _as_int(_body(message).get("active_id"))


def _size(message: dict[str, Any]) -> int | None:
    return _as_int(_routing_filters(message).get("size")) or _as_int(_body(message).get("size"))


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _contains_forbidden_name(message: dict[str, Any]) -> bool:
    names = [_message_name(message) or "", _inner_name(message) or ""]
    lowered = " ".join(names).lower()
    return any(term in lowered for term in FORBIDDEN_TERMS)
