from __future__ import annotations

from typing import Any

DISCOVERY_SCOPE = "BINARY_TURBO"
DISCOVERY_CATEGORIES = ("turbo", "binary")


def list_binary_turbo_assets(client: Any, *, market_type: str) -> list[dict[str, Any]]:
    if market_type not in {"OTC", "REGULAR"}:
        raise ValueError("UNSUPPORTED_MARKET_TYPE")
    payload = client.get_all_init_v2()
    if not isinstance(payload, dict):
        return []
    candle_symbols = _candle_symbols(client)
    want_otc = market_type == "OTC"
    assets: dict[str, dict[str, Any]] = {}
    for category in DISCOVERY_CATEGORIES:
        category_payload = payload.get(category)
        if not isinstance(category_payload, dict):
            continue
        actives = category_payload.get("actives")
        if not isinstance(actives, dict):
            continue
        for item in actives.values():
            if not isinstance(item, dict):
                continue
            raw_symbol = _symbol_from_active(item)
            if raw_symbol is None:
                continue
            is_otc = _symbol_is_otc(raw_symbol)
            if is_otc != want_otc:
                continue
            is_open = _active_is_open(item)
            if not is_open:
                continue
            symbol = _resolve_candle_symbol(raw_symbol, candle_symbols)
            if symbol is None:
                continue
            existing = assets.get(symbol)
            if existing is not None and existing["category"] == "turbo":
                continue
            assets[symbol] = {
                "symbol": symbol,
                "raw_symbol": raw_symbol,
                "category": category,
                "is_open": True,
                "market_type": market_type,
                "discovery_scope": DISCOVERY_SCOPE,
            }
    return [assets[symbol] for symbol in sorted(assets)]


def _symbol_from_active(active: dict[str, Any]) -> str | None:
    raw_name = active.get("name")
    if not isinstance(raw_name, str) or not raw_name:
        return None
    name = raw_name.split(".")[-1]
    return name if name else None


def _active_is_open(active: dict[str, Any]) -> bool:
    if active.get("enabled") is not True:
        return False
    return active.get("is_suspended") is not True


def _symbol_is_otc(symbol: str) -> bool:
    return symbol.endswith("-OTC") or "-OTC-" in symbol


def _candle_symbols(client: Any) -> set[str]:
    get_all_actives = getattr(client, "get_all_ACTIVES_OPCODE", None)
    if not callable(get_all_actives):
        return set()
    payload = get_all_actives()
    if not isinstance(payload, dict):
        return set()
    return {symbol for symbol in payload if isinstance(symbol, str)}


def _resolve_candle_symbol(raw_symbol: str, candle_symbols: set[str]) -> str | None:
    if raw_symbol in candle_symbols:
        return raw_symbol
    candidates = []
    if raw_symbol.endswith("-OTC"):
        candidates.append(raw_symbol.removesuffix("-OTC"))
    if raw_symbol.endswith("-op"):
        candidates.append(raw_symbol.removesuffix("-op"))
    if raw_symbol.endswith("-OTC-op"):
        candidates.append(raw_symbol.removesuffix("-OTC-op"))
        candidates.append(f"{raw_symbol.removesuffix('-OTC-op')}-OTC")
    for candidate in candidates:
        if candidate in candle_symbols:
            return candidate
    return None
