from __future__ import annotations

import json
from pathlib import Path

from app.market.providers.polarium.bootstrap_diagnostic import HistoricalBootstrapDiagnostic
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.store import CandleStore


def page_native_get_first_candles(active_id: int, raw_size: int, request_id: str) -> dict:
    return {
        "name": "sendMessage",
        "request_id": request_id,
        "msg": {
            "name": "get-first-candles",
            "body": {"active_id": active_id, "size": raw_size},
        },
    }


def first_candles_response(active_id: int, raw_size: int, request_id: str, *, start: int = 1_783_720_200) -> dict:
    return {
        "name": "first-candles",
        "request_id": request_id,
        "msg": {
            "body": {
                "active_id": active_id,
                "size": raw_size,
                "candles": [
                    {
                        "from": start,
                        "to": start + raw_size,
                        "open": 5.41,
                        "close": 5.42,
                        "min": 5.40,
                        "max": 5.43,
                        "volume": 0,
                        "size": raw_size,
                    }
                ],
            }
        },
    }


def realtime_payload(active_id: int, raw_size: int, *, start: int = 1_783_720_200) -> dict:
    return {
        "name": "candle-generated",
        "msg": {
            "body": {
                "active_id": active_id,
                "size": raw_size,
                "from": start,
                "to": start + raw_size,
                "open": 5.41,
                "close": 5.42,
                "min": 5.40,
                "max": 5.43,
                "volume": 0,
            }
        },
    }


def diagnostic(tmp_path: Path) -> HistoricalBootstrapDiagnostic:
    return HistoricalBootstrapDiagnostic(
        report_json=tmp_path / "bootstrap_report.json",
        report_txt=tmp_path / "bootstrap_report.txt",
    )


def test_historical_bootstrap_diagnostic_audits_request_response_and_generates_reports(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_diagnostic=diag)

    runtime.process_message(page_native_get_first_candles(2298, 300, "req-m5"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(first_candles_response(2298, 300, "req-m5"), origin="SERVER_INBOUND", now_ms=2_000)

    report = json.loads((tmp_path / "bootstrap_report.json").read_text(encoding="utf-8"))
    record = report["records"][0]

    assert (tmp_path / "bootstrap_report.txt").exists()
    assert record["request_id"] == "req-m5"
    assert record["active_id"] == 2298
    assert record["raw_size_requested"] == 300
    assert record["raw_size_resolved"] == 300
    assert record["request_sent"] is True
    assert record["response_received"] is True
    assert record["response_type"] == "first-candles"
    assert record["candles_found"] == 1
    assert record["candles_accepted"] == 1
    assert record["history_count_before"] == 0
    assert record["history_count_after"] == 1


def test_historical_bootstrap_diagnostic_sanitizes_sensitive_data(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_request(
        active_id=76,
        raw_size=60,
        request_id="req-safe",
        request_sent=True,
        session_context={
            "symbol": "bearer secret token cookie authorization",
            "display_name": "EUR/USD OTC",
            "market_type": "POLARIUM_AUTHORIZED_MARKET",
        },
        now_ms=1_000,
    )

    rendered = (tmp_path / "bootstrap_report.json").read_text(encoding="utf-8").lower()

    assert "bearer secret token cookie authorization" not in rendered
    assert "headers" not in rendered
    assert '"payload":' not in rendered


def test_historical_bootstrap_diagnostic_classifies_timestamp_rejection(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_diagnostic=diag)

    runtime.process_message(page_native_get_first_candles(2298, 300, "req-bad-time"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(first_candles_response(2298, 300, "req-bad-time", start=1_783_720_000), origin="SERVER_INBOUND", now_ms=2_000)

    report = json.loads((tmp_path / "bootstrap_report.json").read_text(encoding="utf-8"))
    record = report["records"][0]

    assert record["category"] == "TIMESTAMP_REJECTED"
    assert record["failure_step"] == "TEMPORAL_VALIDATION"
    assert record["candles_accepted"] == 0
    assert record["history_count_after"] == 0


def test_historical_bootstrap_diagnostic_classifies_no_response_timeout(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_request(
        active_id=2298,
        raw_size=300,
        request_id="req-timeout",
        request_sent=True,
        session_context={"symbol": "XAU/USD OTC", "display_name": "XAU/USD OTC", "history_state": "BOOTSTRAPPING"},
        now_ms=1_000,
    )
    diag.observe_timeout(
        request_id="req-timeout",
        active_id=2298,
        raw_size=300,
        session_context={"symbol": "XAU/USD OTC", "display_name": "XAU/USD OTC", "history_state": "BOOTSTRAPPING"},
        expired=True,
        now_ms=12_000,
    )

    record = json.loads((tmp_path / "bootstrap_report.json").read_text(encoding="utf-8"))["records"][0]

    assert record["category"] == "NO_RESPONSE"
    assert record["timeout"] is True
    assert record["expired_request"] is True


def test_historical_bootstrap_diagnostic_marks_realtime_without_history_as_realtime_only(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), bootstrap_diagnostic=diag)

    runtime.process_message(realtime_payload(2298, 300), origin="SERVER_INBOUND", now_ms=1_000)

    record = json.loads((tmp_path / "bootstrap_report.json").read_text(encoding="utf-8"))["records"][0]
    context = runtime.status().sanitized()["session_context"]

    assert record["category"] == "REALTIME_ONLY"
    assert record["realtime_seen"] is True
    assert context["history_count"] == 0


def test_historical_bootstrap_diagnostic_preserves_m1_m5_m15_regression(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store, bootstrap_diagnostic=diag)

    for raw_size, start in ((60, 1_783_720_020), (300, 1_783_720_200), (900, 1_783_720_800)):
        request_id = f"req-{raw_size}"
        runtime.process_message(page_native_get_first_candles(2298, raw_size, request_id), origin="PAGE_NATIVE", now_ms=raw_size)
        runtime.process_message(first_candles_response(2298, raw_size, request_id, start=start), origin="SERVER_INBOUND", now_ms=raw_size + 1)
        assert len(store.series(active_id=2298, raw_size=raw_size)) == 1

    report = json.loads((tmp_path / "bootstrap_report.json").read_text(encoding="utf-8"))

    assert report["summary"]["total_bootstraps"] == 3
    assert all(record["response_received"] for record in report["records"])
