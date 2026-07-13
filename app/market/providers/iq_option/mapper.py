from __future__ import annotations

from typing import Any

from app.market.providers.models import MarketAsset, ProviderCandle

PROVIDER_NAME = "IQ_OPTION"
MARKET_TYPE_OTC = "OTC"
MARKET_TYPE_REGULAR = "REGULAR"
SUPPORTED_MARKET_TYPES = {MARKET_TYPE_OTC, MARKET_TYPE_REGULAR}
SUPPORTED_RAW_SIZES = {60, 300, 900}
CURRENCY_CODES = {"AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD", "USD"}


def display_name_for_symbol(symbol: str, *, market_type: str | None = None) -> str:
    is_otc = market_type == MARKET_TYPE_OTC or symbol_is_otc(symbol)
    base = symbol.removesuffix("-OTC").removesuffix("-op")
    if len(base) == 6 and base[:3] in CURRENCY_CODES and base[3:] in CURRENCY_CODES:
        label = f"{base[:3]}/{base[3:]}"
    else:
        label = base.replace("-", " ")
    return f"{label} OTC" if is_otc and not label.endswith("OTC") else label


def map_assets(open_time_payload: dict[str, Any] | list[dict[str, Any]], *, market_type: str = MARKET_TYPE_OTC) -> tuple[MarketAsset, ...]:
    if market_type not in SUPPORTED_MARKET_TYPES:
        raise ValueError("UNSUPPORTED_MARKET_TYPE")
    if isinstance(open_time_payload, list):
        return tuple(
            MarketAsset(
                symbol=str(asset["symbol"]),
                display_name=str(asset.get("display_name") or display_name_for_symbol(str(asset.get("raw_symbol") or asset["symbol"]), market_type=market_type)),
                market_type=market_type,
                is_otc=market_type == MARKET_TYPE_OTC or symbol_is_otc(str(asset.get("raw_symbol") or asset["symbol"])),
                is_open=bool(asset.get("is_open")),
                provider=PROVIDER_NAME,
            )
            for asset in sorted(open_time_payload, key=lambda item: str(item.get("symbol", "")))
            if isinstance(asset, dict) and isinstance(asset.get("symbol"), str) and bool(asset.get("is_open"))
        )
    seen: set[str] = set()
    assets: list[MarketAsset] = []
    want_otc = market_type == MARKET_TYPE_OTC
    for category in ("digital", "turbo", "binary"):
        category_payload = open_time_payload.get(category)
        if not isinstance(category_payload, dict):
            continue
        for symbol, metadata in category_payload.items():
            if not isinstance(symbol, str) or symbol in seen:
                continue
            if not isinstance(metadata, dict):
                continue
            is_otc = symbol_is_otc(symbol)
            if is_otc != want_otc:
                continue
            if not bool(metadata.get("open")):
                continue
            seen.add(symbol)
            assets.append(
                MarketAsset(
                    symbol=symbol,
                    display_name=display_name_for_symbol(symbol, market_type=market_type),
                    market_type=market_type,
                    is_otc=is_otc,
                    is_open=bool(metadata.get("open")),
                    provider=PROVIDER_NAME,
                )
            )
    return tuple(sorted(assets, key=lambda item: item.symbol))


def map_candles(symbol: str, raw_size: int, raw_candles: list[dict[str, Any]], *, market_type: str | None = None) -> tuple[ProviderCandle, ...]:
    if raw_size not in SUPPORTED_RAW_SIZES:
        raise ValueError("UNSUPPORTED_TIMEFRAME")
    deduped: dict[int, ProviderCandle] = {}
    for item in raw_candles:
        if not isinstance(item, dict):
            continue
        timestamp = _as_int(item.get("from") or item.get("at") or item.get("timestamp"))
        if timestamp is None:
            continue
        open_price = _as_float(item.get("open"))
        close = _as_float(item.get("close"))
        low = _as_float(item.get("min") if item.get("min") is not None else item.get("low"))
        high = _as_float(item.get("max") if item.get("max") is not None else item.get("high"))
        if None in {open_price, close, low, high}:
            continue
        volume = _as_float(item.get("volume"))
        resolved_market_type = market_type or (MARKET_TYPE_OTC if symbol_is_otc(symbol) else MARKET_TYPE_REGULAR)
        deduped[timestamp] = ProviderCandle(
            provider=PROVIDER_NAME,
            market_type=resolved_market_type,
            symbol=symbol,
            raw_size=raw_size,
            start_timestamp=timestamp,
            end_timestamp=timestamp + raw_size,
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume,
            is_otc=resolved_market_type == MARKET_TYPE_OTC or symbol_is_otc(symbol),
            source_verified=True,
        )
    return tuple(deduped[timestamp] for timestamp in sorted(deduped))


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def symbol_is_otc(symbol: str) -> bool:
    return symbol.endswith("-OTC") or "-OTC-" in symbol
