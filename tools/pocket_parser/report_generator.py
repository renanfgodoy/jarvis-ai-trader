from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from tools.pocket_parser.candle_normalizer import CANDLE_SCHEMA
from tools.pocket_parser.models import PocketReplayResult
from tools.pocket_parser.offline_store import PocketOfflineStore
from tools.pocket_parser.sanitizer import sanitize
from tools.pocket_parser.validator import assert_report_is_sanitized, write_json

DEFAULT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = DEFAULT_DIR / "pocket_parser_report.json"
REPORT_TXT = DEFAULT_DIR / "pocket_parser_report.txt"
CANDLE_SCHEMA_JSON = DEFAULT_DIR / "pocket_candle_schema_report.json"
CANDLE_SCHEMA_TXT = DEFAULT_DIR / "pocket_candle_schema_report.txt"
TICK_SCHEMA_JSON = DEFAULT_DIR / "pocket_tick_schema_report.json"
TICK_SCHEMA_TXT = DEFAULT_DIR / "pocket_tick_schema_report.txt"
ASSET_SCHEMA_JSON = DEFAULT_DIR / "pocket_asset_schema_report.json"
ASSET_SCHEMA_TXT = DEFAULT_DIR / "pocket_asset_schema_report.txt"
STORE_JSON = DEFAULT_DIR / "pocket_offline_store_report.json"
STORE_TXT = DEFAULT_DIR / "pocket_offline_store_report.txt"


def generate_reports(result: PocketReplayResult, store: PocketOfflineStore) -> dict[str, Path]:
    payload = _main_payload(result, store)
    candle_schema = _candle_schema_payload(result)
    tick_schema = _tick_schema_payload(result)
    asset_schema = _asset_schema_payload(result)
    store_payload = store.report()

    write_json(REPORT_JSON, payload)
    REPORT_TXT.write_text(_main_text(payload), encoding="utf-8")
    write_json(CANDLE_SCHEMA_JSON, candle_schema)
    CANDLE_SCHEMA_TXT.write_text(_schema_text("Pocket candle schema", candle_schema), encoding="utf-8")
    write_json(TICK_SCHEMA_JSON, tick_schema)
    TICK_SCHEMA_TXT.write_text(_schema_text("Pocket tick schema", tick_schema), encoding="utf-8")
    write_json(ASSET_SCHEMA_JSON, asset_schema)
    ASSET_SCHEMA_TXT.write_text(_schema_text("Pocket asset schema", asset_schema), encoding="utf-8")
    write_json(STORE_JSON, store_payload)
    STORE_TXT.write_text(_store_text(store_payload), encoding="utf-8")

    paths = {
        "parser_json": REPORT_JSON,
        "parser_txt": REPORT_TXT,
        "candle_schema_json": CANDLE_SCHEMA_JSON,
        "candle_schema_txt": CANDLE_SCHEMA_TXT,
        "tick_schema_json": TICK_SCHEMA_JSON,
        "tick_schema_txt": TICK_SCHEMA_TXT,
        "asset_schema_json": ASSET_SCHEMA_JSON,
        "asset_schema_txt": ASSET_SCHEMA_TXT,
        "store_json": STORE_JSON,
        "store_txt": STORE_TXT,
    }
    assert_report_is_sanitized(tuple(paths.values()))
    return paths


def _main_payload(result: PocketReplayResult, store: PocketOfflineStore) -> dict[str, Any]:
    candles = [candle for batch in result.history_batches for candle in batch.candles]
    periods = sorted({item.period for item in result.change_symbols} | {batch.period for batch in result.history_batches})
    assets = sorted({item.asset for item in result.change_symbols} | {batch.asset for batch in result.history_batches} | {tick.asset for tick in result.ticks})
    timestamps = [item.timestamp for item in candles] + [tick.timestamp for tick in result.ticks]
    required_buckets = (
        "POCKET:EURUSD_otc:60",
        "POCKET:EURUSD_otc:300",
        "POCKET:AUDUSD_otc:60",
        "POCKET:AUDUSD_otc:900",
        "POCKET:USDBRL_otc:60",
        "POCKET:USDBRL_otc:300",
        "POCKET:USDBRL_otc:900",
    )
    existing_buckets = set(store.list_buckets())
    rejected_by_code: dict[str, int] = {}
    for rejection in result.rejections:
        rejected_by_code[rejection.code] = rejected_by_code.get(rejection.code, 0) + 1
    return {
        "har_paths": result.har_paths,
        "sessions_processed": result.sessions_processed,
        "frames_total": result.frames_total,
        "frames_valid": result.frames_valid,
        "frames_invalid": result.frames_invalid,
        "socketio_events": result.socketio_events,
        "changeSymbol_found": len(result.change_symbols),
        "updateHistoryNewFast_found": len(result.history_batches),
        "updateStream_found": len(result.ticks),
        "updateAssets_found": len(result.assets),
        "updateCharts_found": len(result.chart_updates),
        "candles_found": sum(len(batch.candles) + sum(1 for r in result.rejections if r.event_name == "updateHistoryNewFast") for batch in result.history_batches),
        "candles_accepted": len(candles),
        "candles_rejected": sum(1 for item in result.rejections if item.event_name == "updateHistoryNewFast"),
        "ticks_found": len(result.ticks) + sum(1 for item in result.rejections if item.event_name == "updateStream"),
        "ticks_accepted": len(result.ticks),
        "ticks_rejected": sum(1 for item in result.rejections if item.event_name == "updateStream"),
        "assets_found": len(result.assets),
        "periods_found": periods,
        "assets_processed": assets,
        "buckets_created": store.list_buckets(),
        "required_buckets_present": {key: key in existing_buckets for key in required_buckets},
        "duplicates": _duplicates(result),
        "first_timestamp": min(timestamps) if timestamps else None,
        "last_timestamp": max(timestamps) if timestamps else None,
        "candle_schema": _candle_schema_payload(result)["classification"],
        "tick_schema": _tick_schema_payload(result)["classification"],
        "asset_schema": _asset_schema_payload(result)["classification"],
        "rejected_by_code": rejected_by_code,
        "unknown_events": result.unknown_events,
        "compatibility": _compatibility(result, store),
        "classification": _classification(result, store),
        "gaps": _gaps(result, store),
    }


def _candle_schema_payload(result: PocketReplayResult) -> dict[str, Any]:
    candles = [candle for batch in result.history_batches for candle in batch.candles]
    classifications = "STABLE" if candles and not any(r.code in {"UNKNOWN_CANDLE_SCHEMA", "INVALID_OHLC"} for r in result.rejections) else "CANDLE_SCHEMA_AMBIGUOUS"
    return {
            "classification": classifications,
            "schema": CANDLE_SCHEMA if classifications == "STABLE" else "CANDLE_SCHEMA_AMBIGUOUS",
            "positions": {
                "0": "timestamp",
                "1": "open",
                "2": "close",
                "3": "high",
                "4": "low",
                "5": "volume",
            }
            if classifications == "STABLE"
            else {},
            "validated_candles": len(candles),
            "rejected_candles": sum(1 for item in result.rejections if item.event_name == "updateHistoryNewFast"),
            "validation_rules": ["high>=open", "high>=close", "low<=open", "low<=close", "high>=low", "timestamp_orderable", "positive_prices"],
    }


def _tick_schema_payload(result: PocketReplayResult) -> dict[str, Any]:
    return {
            "classification": "STABLE" if result.ticks else "UNKNOWN_TICK_SCHEMA",
            "schema": "ASSET_TIMESTAMP_PRICE" if result.ticks else "UNKNOWN_TICK_SCHEMA",
            "positions": {"0": "asset", "1": "timestamp", "2": "price"} if result.ticks else {},
            "validated_ticks": len(result.ticks),
            "rejected_ticks": sum(1 for item in result.rejections if item.event_name == "updateStream"),
            "assets": sorted({tick.asset for tick in result.ticks}),
    }


def _asset_schema_payload(result: PocketReplayResult) -> dict[str, Any]:
    symbols = sorted({asset.symbol for asset in result.assets})
    return {
            "classification": "PARTIAL_STABLE" if result.assets else "UNKNOWN_ASSET_SCHEMA",
            "assets_count": len(result.assets),
            "unique_assets_count": len(symbols),
            "sample_symbols": symbols[:20],
            "confirmed_fields": ["symbol", "display_name", "market_type", "supported_periods"],
            "candidate_fields": ["candidate_payout", "candidate_availability"],
            "unknown_fields_policy": "preserved_as_unknown_numeric_fields_and_unknown_boolean_fields",
            "payout": "NOT_PROMOTED",
            "is_available": "NOT_PROMOTED",
    }


def _duplicates(result: PocketReplayResult) -> dict[str, int]:
    seen: set[tuple[int, str, int, float]] = set()
    duplicate_candles = 0
    for batch in result.history_batches:
        for candle in batch.candles:
            key = (candle.session_index, candle.symbol, candle.period, candle.timestamp)
            if key in seen:
                duplicate_candles += 1
            seen.add(key)
    tick_seen: set[tuple[int, str, float, float]] = set()
    duplicate_ticks = 0
    for tick in result.ticks:
        key = (tick.session_index, tick.asset, tick.timestamp, tick.price)
        if key in tick_seen:
            duplicate_ticks += 1
        tick_seen.add(key)
    return {"candles": duplicate_candles, "ticks": duplicate_ticks}


def _compatibility(result: PocketReplayResult, store: PocketOfflineStore) -> str:
    if result.sessions_processed < 2:
        return "PARTIALLY_COMPATIBLE"
    candle_schema = _candle_schema_payload(result)["classification"]
    tick_schema = _tick_schema_payload(result)["classification"]
    if candle_schema == "STABLE" and tick_schema == "STABLE" and len(store.list_buckets()) >= 7:
        return "COMPATIBLE"
    return "PARTIALLY_COMPATIBLE"


def _classification(result: PocketReplayResult, store: PocketOfflineStore) -> str:
    if _candle_schema_payload(result)["classification"] != "STABLE":
        return "LIMITED"
    if _tick_schema_payload(result)["classification"] != "STABLE":
        return "LIMITED"
    if len(store.list_buckets()) >= 7 and result.sessions_processed == 2:
        return "GOOD"
    return "LIMITED"


def _gaps(result: PocketReplayResult, store: PocketOfflineStore) -> list[str]:
    gaps = []
    if _asset_schema_payload(result)["classification"] != "PARTIAL_STABLE":
        gaps.append("Asset schema precisa de mais evidencia.")
    else:
        gaps.append("Payout e disponibilidade ainda nao foram promovidos semanticamente.")
    missing = [key for key, present in _main_payload_required_buckets(store).items() if not present]
    if missing:
        gaps.append(f"Buckets ausentes: {', '.join(missing)}")
    return gaps


def _main_payload_required_buckets(store: PocketOfflineStore) -> dict[str, bool]:
    existing = set(store.list_buckets())
    return {
        key: key in existing
        for key in (
            "POCKET:EURUSD_otc:60",
            "POCKET:EURUSD_otc:300",
            "POCKET:AUDUSD_otc:60",
            "POCKET:AUDUSD_otc:900",
            "POCKET:USDBRL_otc:60",
            "POCKET:USDBRL_otc:300",
            "POCKET:USDBRL_otc:900",
        )
    }


def _main_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Pocket Offline Protocol Parser"]
    for key in (
        "sessions_processed",
        "frames_total",
        "frames_valid",
        "frames_invalid",
        "socketio_events",
        "changeSymbol_found",
        "updateHistoryNewFast_found",
        "updateStream_found",
        "updateAssets_found",
        "updateCharts_found",
        "candles_accepted",
        "candles_rejected",
        "ticks_accepted",
        "ticks_rejected",
        "assets_found",
        "candle_schema",
        "tick_schema",
        "asset_schema",
        "compatibility",
        "classification",
    ):
        lines.append(f"{key}={payload.get(key)}")
    lines.append(f"buckets_created={', '.join(payload.get('buckets_created') or [])}")
    lines.append(f"assets_processed={', '.join(payload.get('assets_processed') or [])}")
    lines.append(f"periods_found={payload.get('periods_found')}")
    lines.append("gaps:")
    lines.extend(f"- {gap}" for gap in payload.get("gaps", []))
    return "\n".join(lines)


def _schema_text(title: str, payload: dict[str, Any]) -> str:
    lines = [title]
    for key, value in payload.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines)


def _store_text(payload: dict[str, Any]) -> str:
    lines = ["Pocket Offline Store", f"bucket_count={payload.get('bucket_count')}"]
    for key, item in (payload.get("buckets") or {}).items():
        lines.append(f"{key} count={item.get('count')} first={item.get('first_timestamp')} last={item.get('last_timestamp')}")
    return "\n".join(lines)
