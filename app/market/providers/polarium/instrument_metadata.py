from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolariumInstrumentMetadata:
    active_id: int
    symbol: str
    market_type: str | None = None
    display_name: str | None = None

    def sanitized(self) -> dict:
        return {
            "active_id": self.active_id,
            "symbol": self.symbol,
            "market_type": self.market_type,
            "display_name": self.display_name,
        }


class PolariumInstrumentMetadataMap:
    """Read-only active_id -> symbol map observed from the authorized session."""

    def __init__(self) -> None:
        self._items: dict[int, PolariumInstrumentMetadata] = {}

    def observe(self, message: dict[str, Any]) -> tuple[PolariumInstrumentMetadata, ...]:
        observed: list[PolariumInstrumentMetadata] = []
        for item in _walk_dicts(message):
            metadata = _metadata_from_dict(item)
            if metadata is None:
                continue
            self._items[metadata.active_id] = metadata
            observed.append(metadata)
        return tuple(observed)

    def symbol_for(self, active_id: int) -> str | None:
        metadata = self._items.get(active_id)
        return metadata.symbol if metadata else None

    def metadata_for(self, active_id: int) -> PolariumInstrumentMetadata | None:
        return self._items.get(active_id)

    def sanitized(self) -> list[dict]:
        return [item.sanitized() for item in sorted(self._items.values(), key=lambda value: value.active_id)]


def _metadata_from_dict(value: dict[str, Any]) -> PolariumInstrumentMetadata | None:
    active_id = _as_int(value.get("active_id")) or _as_int(value.get("activeId"))
    if active_id is None:
        return None
    symbol = _as_safe_string(value.get("symbol")) or _as_safe_string(value.get("ticker"))
    display_name = _as_safe_string(value.get("display_name")) or _as_safe_string(value.get("displayName")) or _as_safe_string(value.get("name")) or _as_safe_string(value.get("title"))
    if symbol is None:
        symbol = display_name
    if symbol is None:
        return None
    return PolariumInstrumentMetadata(
        active_id=active_id,
        symbol=symbol,
        market_type=_as_safe_string(value.get("market_type")) or _as_safe_string(value.get("marketType")) or _as_safe_string(value.get("type")),
        display_name=display_name,
    )


def _walk_dicts(value: Any) -> tuple[dict[str, Any], ...]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for item in value.values():
            found.extend(_walk_dicts(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(_walk_dicts(item))
    return tuple(found)


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _as_safe_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.strip().split())
    if not normalized or len(normalized) > 80:
        return None
    lowered = normalized.lower()
    if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password")):
        return None
    return normalized
