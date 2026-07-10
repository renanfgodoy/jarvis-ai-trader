from __future__ import annotations

from typing import Final

CANDLE_GENERATED: Final = "candle-generated"
CANDLES_GENERATED: Final = "candles-generated"
DIGITAL_OPTION_CLIENT_PRICE_GENERATED: Final = "digital-option-client-price-generated"
FIRST_CANDLES: Final = "first-candles"
TIME_SYNC: Final = "timeSync"
SUBSCRIBE_MESSAGE: Final = "subscribeMessage"
UNSUBSCRIBE_MESSAGE: Final = "unsubscribeMessage"

SUPPORTED_EVENTS: Final[frozenset[str]] = frozenset(
    {
        CANDLE_GENERATED,
        CANDLES_GENERATED,
        DIGITAL_OPTION_CLIENT_PRICE_GENERATED,
        FIRST_CANDLES,
        TIME_SYNC,
        SUBSCRIBE_MESSAGE,
        UNSUBSCRIBE_MESSAGE,
    }
)

PARSABLE_CANDLE_EVENTS: Final[frozenset[str]] = frozenset(
    {
        CANDLE_GENERATED,
        FIRST_CANDLES,
    }
)
