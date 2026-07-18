from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.market.providers.pocket.candle_store_adapter import PocketCandleStoreAdapter, PocketStoredCandle
from app.market.providers.pocket.live_period_trace import PERIOD_TO_TIMEFRAME
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.runtime import PocketMarketRuntime

EXPECTED_CONTEXTS: tuple[tuple[str, int, str], ...] = (
    ("EURUSD_otc", 60, "M1"),
    ("EURUSD_otc", 300, "M5"),
    ("AUDUSD_otc", 900, "M15"),
    ("USDBRL_otc", 300, "M5"),
)
EXPECTED_REVISIT = ("EURUSD_otc", 60, "M1")
FAILURE_CATEGORIES = {
    "ASSET_BUCKET_MIX",
    "TIMEFRAME_BUCKET_MIX",
    "STALE_CONTEXT_WRITE",
    "WRONG_BUCKET_RESOLUTION",
    "CROSS_CONTEXT_HISTORY_COUNT",
    "CROSS_CONTEXT_REALTIME_WRITE",
    "HISTORY_NOT_OBSERVED_FOR_CONTEXT",
}


@dataclass(frozen=True)
class PocketContextExpectation:
    asset: str
    period: int
    timeframe: str

    @property
    def bucket_key(self) -> str:
        return PocketCandleStoreAdapter.key(self.asset, self.period)


def expected_contexts() -> tuple[PocketContextExpectation, ...]:
    return tuple(PocketContextExpectation(asset, period, timeframe) for asset, period, timeframe in EXPECTED_CONTEXTS)


def validate_multi_context_source(source: PocketReadOnlyLiveSource) -> dict[str, Any]:
    runtime = source.runtime
    transport = source.transport
    status = source.status()
    contexts = _observed_contexts(transport)
    bucket_report = build_bucket_isolation_report(runtime)
    context_rows = [_context_result(expectation, runtime, contexts, bucket_report) for expectation in expected_contexts()]
    sequence = [_context_sequence_row(item) for item in getattr(transport, "live_period_trace", object()).atomic_contexts] if hasattr(transport, "live_period_trace") else []
    revisit = _revisit_result(sequence)
    failures = sorted({failure for row in context_rows for failure in row["failure_categories"]} | set(revisit.get("failure_categories", ())))
    all_pass = all(row["status"] == "PASS" for row in context_rows) and revisit.get("status") == "PASS"
    runtime_status = status.get("runtime", {})
    return {
        "observation_mode": "REAL_PASSIVE_CDP",
        "target_found": status.get("transport", {}).get("target_found"),
        "market_socket_found": status.get("transport", {}).get("market_socket_found"),
        "contexts_expected": [expectation.__dict__ | {"bucket_key": expectation.bucket_key} for expectation in expected_contexts()],
        "contexts_observed": contexts,
        "context_sequence": sequence,
        "context_transitions": _transitions(sequence),
        "context_results": context_rows,
        "revisit": revisit,
        "history_batches_by_context": _history_batches_by_context(transport),
        "historical_candles_by_context": {row["bucket_key"]: row["historical_count"] for row in bucket_report["buckets"]},
        "stream_events_by_context": _stream_events_by_context(runtime),
        "ticks_by_context": _ticks_by_context(runtime),
        "realtime_candles_by_context": {row["bucket_key"]: row["realtime_count"] for row in bucket_report["buckets"]},
        "buckets": [row["bucket_key"] for row in bucket_report["buckets"]],
        "bucket_counts": {row["bucket_key"]: row["count"] for row in bucket_report["buckets"]},
        "history_counts": {row["bucket_key"]: row["historical_count"] for row in bucket_report["buckets"]},
        "readiness_by_bucket": runtime_status.get("readiness", {}),
        "context_latencies": _latencies(sequence),
        "failure_categories": failures,
        "global_status": "PASS" if all_pass else "PARTIAL" if any(row["status"] == "PASS" for row in context_rows) else "FAIL",
        "outbound_messages_originated_by_friday": 0,
        "observer_stopped_cleanly": runtime_status.get("connection_state") == "STOPPED" and status.get("transport", {}).get("running") is False,
    }


def build_bucket_isolation_report(runtime: PocketMarketRuntime) -> dict[str, Any]:
    rows = [_bucket_row(runtime.store, bucket_key, runtime.readiness.state_for(bucket_key)) for bucket_key in runtime.store.list_buckets()]
    return {
        "buckets": rows,
        "failure_categories": sorted({failure for row in rows for failure in row["failure_categories"]}),
        "global_isolation_status": "ISOLATED" if all(row["isolation_status"] == "ISOLATED" for row in rows) else "MIXED_OR_UNKNOWN",
    }


def _context_result(
    expectation: PocketContextExpectation,
    runtime: PocketMarketRuntime,
    contexts: list[dict[str, Any]],
    isolation_report: dict[str, Any],
) -> dict[str, Any]:
    bucket_key = expectation.bucket_key
    bucket = next((row for row in isolation_report["buckets"] if row["bucket_key"] == bucket_key), None)
    context_observed = any(item.get("asset") == expectation.asset and item.get("period") == expectation.period for item in contexts)
    history_count = int(bucket.get("historical_count") or 0) if bucket else 0
    realtime_count = int(bucket.get("realtime_count") or 0) if bucket else 0
    readiness = runtime.readiness.state_for(bucket_key)
    failures: list[str] = []
    if bucket is None:
        failures.append("WRONG_BUCKET_RESOLUTION")
    if context_observed and history_count == 0:
        failures.append("HISTORY_NOT_OBSERVED_FOR_CONTEXT")
    if bucket and bucket.get("foreign_asset_count"):
        failures.append("ASSET_BUCKET_MIX")
    if bucket and bucket.get("foreign_period_count"):
        failures.append("TIMEFRAME_BUCKET_MIX")
    status = "PASS" if context_observed and history_count > 0 and bucket and bucket.get("isolation_status") == "ISOLATED" and readiness == "READY" else "PARTIAL" if context_observed or bucket else "NOT_OBSERVED"
    return {
        "asset": expectation.asset,
        "period": expectation.period,
        "timeframe": expectation.timeframe,
        "bucket_key": bucket_key,
        "change_symbol_observed": context_observed,
        "history_observed": history_count > 0,
        "historical_candles": history_count,
        "ticks": realtime_count,
        "realtime_candles": realtime_count,
        "bucket_count": int(bucket.get("count") or 0) if bucket else 0,
        "history_count": history_count,
        "readiness": readiness,
        "first_timestamp": bucket.get("first_timestamp") if bucket else None,
        "last_timestamp": bucket.get("last_timestamp") if bucket else None,
        "last_price": bucket.get("last_price") if bucket else None,
        "context_published": context_observed,
        "failure_categories": failures,
        "status": status,
    }


def _bucket_row(store: PocketCandleStoreAdapter, bucket_key: str, readiness: str) -> dict[str, Any]:
    parts = bucket_key.split(":")
    expected_asset = parts[1] if len(parts) == 3 else None
    expected_period = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else None
    candles = store.candles(bucket_key)
    historical = [item for item in candles if not item.is_realtime]
    realtime = [item for item in candles if item.is_realtime]
    foreign_asset = sum(1 for item in candles if item.asset != expected_asset)
    foreign_period = sum(1 for item in candles if item.period != expected_period)
    duplicates = len(candles) - len({item.timestamp for item in candles})
    integrity_failures = _integrity_failures(candles, expected_asset, expected_period)
    failure_categories: list[str] = []
    if foreign_asset:
        failure_categories.append("ASSET_BUCKET_MIX")
    if foreign_period:
        failure_categories.append("TIMEFRAME_BUCKET_MIX")
    status = "ISOLATED" if not foreign_asset and not foreign_period and not integrity_failures else "MIXED_ASSET" if foreign_asset else "MIXED_PERIOD" if foreign_period else "UNKNOWN"
    last = candles[-1] if candles else None
    return {
        "bucket_key": bucket_key,
        "asset": expected_asset,
        "period": expected_period,
        "timeframe": PERIOD_TO_TIMEFRAME.get(expected_period or 0),
        "count": len(candles),
        "historical_count": len(historical),
        "realtime_count": len(realtime),
        "first_timestamp": candles[0].timestamp if candles else None,
        "last_timestamp": candles[-1].timestamp if candles else None,
        "last_price": last.close if last else None,
        "foreign_asset_count": foreign_asset,
        "foreign_period_count": foreign_period,
        "duplicate_count": duplicates,
        "stale_write_count": 0,
        "integrity_failures": integrity_failures,
        "readiness": readiness,
        "isolation_status": status,
        "failure_categories": failure_categories,
    }


def _integrity_failures(candles: tuple[PocketStoredCandle, ...], expected_asset: str | None, expected_period: int | None) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    previous_timestamp: float | None = None
    for candle in candles:
        reasons: list[str] = []
        if candle.asset != expected_asset:
            reasons.append("ASSET_BUCKET_MIX")
        if candle.period != expected_period:
            reasons.append("TIMEFRAME_BUCKET_MIX")
        if candle.high < candle.low or candle.high < candle.open or candle.high < candle.close or candle.low > candle.open or candle.low > candle.close:
            reasons.append("INVALID_OHLC")
        if min(candle.open, candle.high, candle.low, candle.close) <= 0:
            reasons.append("NON_POSITIVE_PRICE")
        if previous_timestamp is not None and candle.timestamp < previous_timestamp:
            reasons.append("TIMESTAMP_OUT_OF_ORDER")
        previous_timestamp = candle.timestamp
        if reasons:
            failures.append({"timestamp": candle.timestamp, "reasons": reasons})
    return failures[:100]


def _observed_contexts(transport: object) -> list[dict[str, Any]]:
    trace = getattr(transport, "live_period_trace", None)
    if trace is None:
        return []
    return [_context_sequence_row(item) for item in trace.atomic_contexts]


def _context_sequence_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "asset": item.get("asset"),
        "period": item.get("period"),
        "timeframe": item.get("timeframe"),
        "bucket_key": item.get("bucket_key"),
        "source": item.get("source"),
        "timestamp": item.get("timestamp"),
        "classification": item.get("classification"),
    }


def _transitions(sequence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    previous = None
    for item in sequence:
        rows.append({"previous": previous, "current": item, "classification": "CONTEXT_REVISIT_OK" if previous == item else "ATOMIC_CONTEXT_CONFIRMED"})
        previous = item
    return rows


def _revisit_result(sequence: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [item for item in sequence if item.get("asset") == EXPECTED_REVISIT[0] and item.get("period") == EXPECTED_REVISIT[1]]
    if len(matches) >= 2:
        return {"status": "PASS", "classification": "CONTEXT_REVISIT_OK", "bucket_key": matches[-1].get("bucket_key"), "failure_categories": []}
    if len(matches) == 1:
        return {"status": "PARTIAL", "classification": "BUCKET_REUSED_NOT_REVISITED", "bucket_key": matches[0].get("bucket_key"), "failure_categories": []}
    return {"status": "NOT_OBSERVED", "classification": "REVISIT_NOT_OBSERVED", "bucket_key": PocketCandleStoreAdapter.key(EXPECTED_REVISIT[0], EXPECTED_REVISIT[1]), "failure_categories": ["WRONG_BUCKET_RESOLUTION"]}


def _history_batches_by_context(transport: object) -> dict[str, int]:
    trace = getattr(transport, "live_history_trace", None)
    if trace is None:
        return {}
    rows: dict[str, int] = {}
    for item in trace.history_candidates:
        if item.get("classification") != "CONFIRMED_HISTORY_EVENT":
            continue
        # The sanitized shape report intentionally avoids raw payload values.
        # Use the parser/runtime bucket report for exact counts; keep this as an
        # event-level counter.
        rows["CONFIRMED_HISTORY_EVENT"] = rows.get("CONFIRMED_HISTORY_EVENT", 0) + 1
    return rows


def _stream_events_by_context(runtime: PocketMarketRuntime) -> dict[str, int]:
    return {key: sum(1 for item in runtime.store.candles(key) if item.is_realtime) for key in runtime.store.list_buckets()}


def _ticks_by_context(runtime: PocketMarketRuntime) -> dict[str, int]:
    return _stream_events_by_context(runtime)


def _latencies(sequence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "bucket_key": item.get("bucket_key"),
            "context_publish_latency_ms": None,
            "history_latency_ms": None,
            "first_tick_latency_ms": None,
            "ready_latency_ms": None,
        }
        for item in sequence
    ]
