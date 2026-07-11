from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.indicators.models import IndicatorValue
from app.market.events.models import NormalizedMarketCandle


class BaseIndicator(ABC):
    """Passive indicator contract.

    Implementations receive candles already stored by the Market Candle Store.
    They must not fetch data, open sockets, emit signals, or execute orders.
    """

    name: str
    min_candles: int = 1

    @abstractmethod
    def calculate(
        self,
        candles: tuple[NormalizedMarketCandle, ...],
        parameters: dict[str, Any] | None = None,
    ) -> IndicatorValue:
        """Return a deterministic value for the provided candle series."""
