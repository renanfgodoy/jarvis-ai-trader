from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from app.market.providers.polarium.bootstrap_payload_trace import BootstrapPayloadTraceDiagnostic
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.store import CandleStore
from app.market.store.types import CandleSeriesKey, CandleStoreWriteResult


def request(active_id: int, raw_size: int, request_id: str) -> dict:
    return {
        "name": "sendMessage",
        "request_id": request_id,
        "msg": {"name": "get-first-candles", "body": {"active_id": active_id, "size": raw_size}},
    }


def history(
    active_id: int,
    raw_size: int,
    request_id: str,
    *,
    count: int,
    symbol: str = "EUR/USD OTC",
    start: int = 1_783_720_200,
    duplicate_timestamp: bool = False,
) -> dict:
    return {
        "name": "first-candles",
        "request_id": request_id,
        "msg": {
            "body": {
                "active_id": active_id,
                "size": raw_size,
                "symbol": symbol,
                "candles": [
                    {
                        "from": start if duplicate_timestamp else start + index * raw_size,
                        "to": (start if duplicate_timestamp else start + index * raw_size) + raw_size,
                        "open": 1.1,
                        "close": 1.2 + index / 10_000,
                        "min": 1.0,
                        "max": 1.3,
                        "volume": 0,
                        "size": raw_size,
                    }
                    for index in range(count)
                ],
            }
        },
    }


def diagnostic(tmp_path: Path) -> BootstrapPayloadTraceDiagnostic:
    return BootstrapPayloadTraceDiagnostic(
        report_json=tmp_path / "bootstrap_payload_report.json",
        report_txt=tmp_path / "bootstrap_payload_report.txt",
    )


def read_report(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "bootstrap_payload_report.json").read_text(encoding="utf-8"))


def test_bootstrap_payload_trace_reports_payload_empty(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_payload_trace=diag)

    runtime.process_message(request(76, 60, "req-empty"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(76, 60, "req-empty", count=0), origin="SERVER_INBOUND", now_ms=2_000)

    record = read_report(tmp_path)["records"][0]
    assert record["category"] == "PAYLOAD_EMPTY"
    assert record["candles_in_payload"] == 0
    assert record["candles_after_parser"] == 0
    assert record["history_after"] == 0


def test_bootstrap_payload_trace_reports_single_candle_payload(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_payload_trace=diag)

    runtime.process_message(request(2298, 300, "req-single"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(2298, 300, "req-single", count=1, symbol="XAU/USD OTC"), origin="SERVER_INBOUND", now_ms=2_000)

    record = read_report(tmp_path)["records"][0]
    assert record["category"] == "PAYLOAD_SINGLE_CANDLE"
    assert record["symbol"] == "XAU/USD OTC"
    assert record["candles_in_payload"] == 1
    assert record["candles_after_parser"] == 1
    assert record["candles_written"] == 1


def test_bootstrap_payload_trace_reports_successful_hundred_candle_payload(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_payload_trace=diag)

    runtime.process_message(request(76, 60, "req-hundred"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(76, 60, "req-hundred", count=100), origin="SERVER_INBOUND", now_ms=2_000)

    record = read_report(tmp_path)["records"][0]
    assert record["category"] == "SUCCESS"
    assert record["candles_in_payload"] == 100
    assert record["candles_after_parser"] == 100
    assert record["candles_after_validation"] == 100
    assert record["candles_written"] == 100
    assert record["bucket_before"] == 0
    assert record["bucket_after"] == 100
    assert record["history_after"] == 100


def test_bootstrap_payload_trace_reports_parser_reducing_duplicate_timestamps(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_payload_trace=diag)

    runtime.process_message(request(76, 60, "req-parser"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(76, 60, "req-parser", count=2, duplicate_timestamp=True), origin="SERVER_INBOUND", now_ms=2_000)

    record = read_report(tmp_path)["records"][0]
    assert record["category"] == "PARSER_DROPPED"
    assert record["candles_in_payload"] == 2
    assert record["candles_after_parser"] == 1


def test_bootstrap_payload_trace_reports_validation_reducing_bad_m5_timestamp(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_payload_trace=diag)

    runtime.process_message(request(2298, 300, "req-validation"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(2298, 300, "req-validation", count=1, start=1_783_720_000), origin="SERVER_INBOUND", now_ms=2_000)

    record = read_report(tmp_path)["records"][0]
    assert record["category"] == "VALIDATION_DROPPED"
    assert record["candles_in_payload"] == 1
    assert record["candles_after_validation"] == 0


def test_bootstrap_payload_trace_reports_duplicate_filter(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_payload_trace=diag)
    payload = history(2298, 60, "req-dup-a", count=1, symbol="XAU/USD OTC", start=1_783_720_200)

    runtime.process_message(request(2298, 60, "req-dup-a"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(payload, origin="SERVER_INBOUND", now_ms=2_000)
    runtime.process_message(request(2298, 60, "req-dup-b"), origin="PAGE_NATIVE", now_ms=3_000)
    payload["request_id"] = "req-dup-b"
    runtime.process_message(payload, origin="SERVER_INBOUND", now_ms=4_000)

    record = read_report(tmp_path)["records"][-1]
    assert record["category"] == "DUPLICATE_FILTER"
    assert record["candles_written"] == 0
    assert record["candles_ignored"] == 1
    assert record["duplicate_count"] == 1
    assert record["history_before"] == 1
    assert record["history_after"] == 1


def test_bootstrap_payload_trace_reports_store_dropped_from_write_results(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    event = _Event(
        event_name="first-candles",
        active_id=2298,
        symbol="BTC/USD OTC",
        candles=(_Candle(active_id=2298, symbol="BTC/USD OTC", raw_size=900, start_timestamp=1_783_720_800),),
    )

    diag.observe_success(
        message=history(2298, 900, "req-store", count=1, symbol="BTC/USD OTC", start=1_783_720_800),
        event=event,
        store_results=(
            CandleStoreWriteResult(
                status="rejected",
                key=CandleSeriesKey(provider="POLARIUM", active_id=2298, raw_size=900),
                start_timestamp=1_783_720_800,
                reason="Sanitized rejection.",
            ),
        ),
        request_id="req-store",
        requested_active_id=2298,
        requested_raw_size=900,
        bucket_before=0,
        bucket_after=0,
        history_before=0,
        history_after=0,
        readiness_before="BOOTSTRAPPING",
        readiness_after="BOOTSTRAPPING",
        now_ms=1_000,
    )

    assert read_report(tmp_path)["records"][0]["category"] == "STORE_DROPPED"


@pytest.mark.parametrize(
    ("active_id", "symbol", "raw_size", "request_id"),
    (
        (76, "EUR/USD OTC", 60, "req-eurusd-m1"),
        (2298, "XAU/USD OTC", 300, "req-xauusd-m5"),
        (85, "BTC/USD OTC", 900, "req-btcusd-m15"),
    ),
)
def test_bootstrap_payload_trace_covers_assets_and_timeframes(
    tmp_path: Path,
    active_id: int,
    symbol: str,
    raw_size: int,
    request_id: str,
) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_payload_trace=diag)

    start = 1_783_720_800 if raw_size == 900 else 1_783_720_200 if raw_size == 300 else 1_783_720_020
    runtime.process_message(request(active_id, raw_size, request_id), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(active_id, raw_size, request_id, count=3, symbol=symbol, start=start), origin="SERVER_INBOUND", now_ms=2_000)

    record = read_report(tmp_path)["records"][0]
    assert record["active_id"] == active_id
    assert record["symbol"] == symbol
    assert record["raw_size"] == raw_size
    assert record["candles_in_payload"] == 3
    assert record["category"] == "SUCCESS"


@dataclass(frozen=True)
class _Candle:
    active_id: int
    symbol: str | None
    raw_size: int
    start_timestamp: int


@dataclass(frozen=True)
class _Event:
    event_name: str
    active_id: int
    symbol: str | None
    candles: tuple[_Candle, ...]
