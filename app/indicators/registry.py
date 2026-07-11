from __future__ import annotations

from app.indicators.base import BaseIndicator
from app.indicators.errors import IndicatorAlreadyRegisteredError, IndicatorNotFoundError


class IndicatorRegistry:
    """In-memory registry for passive indicator implementations."""

    def __init__(self) -> None:
        self._indicators: dict[str, BaseIndicator] = {}

    def register(self, indicator: BaseIndicator) -> None:
        name = _normalize_name(indicator.name)
        if name in self._indicators:
            raise IndicatorAlreadyRegisteredError(f"Indicator already registered: {name}")
        self._indicators[name] = indicator

    def get(self, name: str) -> BaseIndicator:
        normalized = _normalize_name(name)
        try:
            return self._indicators[normalized]
        except KeyError as exc:
            raise IndicatorNotFoundError(f"Indicator not registered: {normalized}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._indicators.keys()))


def _normalize_name(name: str) -> str:
    return name.strip().lower()
