from __future__ import annotations

import json
from pathlib import Path

from app.market.providers.polarium.history_count_diagnostic import HistoryCountDiagnostic
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.store import CandleStore
from app.market.store.types import CandleSeriesKey, CandleStoreWriteResult


def request(active_id: int, raw_size: int, request_id: str) -> dict:
    return {
        "name": "sendMessage",
        "request_id": request_id,
        "msg": {"name": "get-first-candles", "body": {"active_id": active_id, "size": raw_size}},
    }


def history(active_id: int, raw_size: int, request_id: str, *, start: int, close: float = 5.42) -> dict:
    return {
        "name": "first-candles",
        "request_id": request_id,
        "msg": {
            "body": {
                "active_id": active_id,
                "size": raw_size,
                "symbol": "XAU/USD OTC",
                "candles": [
                    {
                        "from": start,
                        "to": start + raw_size,
                        "open": 5.41,
                        "close": close,
                        "min": 5.40,
                        "max": 5.43,
                        "volume": 0,
                        "size": raw_size,
                    }
                ],
            }
        },
    }


def diagnostic(tmp_path: Path) -> HistoryCountDiagnostic:
    return HistoryCountDiagnostic(
        report_json=tmp_path / "history_count_report.json",
        report_txt=tmp_path / "history_count_report.txt",
    )


def read_report(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "history_count_report.json").read_text(encoding="utf-8"))


def test_history_count_diagnostic_reports_append_and_history_increment(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), history_count_diagnostic=diag)

    runtime.process_message(request(2298, 300, "req-m5"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(2298, 300, "req-m5", start=1_783_720_200), origin="SERVER_INBOUND", now_ms=2_000)

    report = read_report(tmp_path)
    record = report["records"][0]

    assert (tmp_path / "history_count_report.txt").exists()
    assert record["merge_type"] == "append"
    assert record["append_count"] == 1
    assert record["bucket_before"] == 0
    assert record["bucket_after"] == 1
    assert record["history_before"] == 0
    assert record["history_after"] == 1
    assert record["readiness_count_before"] == 0
    assert record["readiness_count_after"] == 1


def test_history_count_diagnostic_reports_replace_without_history_increment(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), history_count_diagnostic=diag)

    runtime.process_message(request(2298, 300, "req-first"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(2298, 300, "req-first", start=1_783_720_200, close=5.42), origin="SERVER_INBOUND", now_ms=2_000)
    runtime.process_message(request(2298, 300, "req-update"), origin="PAGE_NATIVE", now_ms=3_000)
    runtime.process_message(history(2298, 300, "req-update", start=1_783_720_200, close=5.43), origin="SERVER_INBOUND", now_ms=4_000)

    records = read_report(tmp_path)["records"]

    assert records[-1]["merge_type"] == "replace"
    assert records[-1]["category"] == "MERGE_REPLACED"
    assert records[-1]["replace_count"] == 1
    assert records[-1]["bucket_before"] == 1
    assert records[-1]["bucket_after"] == 1
    assert records[-1]["history_before"] == 1
    assert records[-1]["history_after"] == 1


def test_history_count_diagnostic_reports_duplicate_filter(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), history_count_diagnostic=diag)

    runtime.process_message(request(2298, 60, "req-a"), origin="PAGE_NATIVE", now_ms=1_000)
    payload = history(2298, 60, "req-a", start=1_783_720_020)
    runtime.process_message(payload, origin="SERVER_INBOUND", now_ms=2_000)
    runtime.process_message(request(2298, 60, "req-b"), origin="PAGE_NATIVE", now_ms=3_000)
    payload["request_id"] = "req-b"
    runtime.process_message(payload, origin="SERVER_INBOUND", now_ms=4_000)

    record = read_report(tmp_path)["records"][-1]

    assert record["category"] == "DUPLICATE_FILTER"
    assert record["merge_type"] == "ignored"
    assert record["ignored_count"] == 1
    assert record["deduplicated_count"] == 1


def test_history_count_diagnostic_classifies_history_not_incremented_from_store_evidence(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    result = CandleStoreWriteResult(
        status="added",
        key=CandleSeriesKey(provider="POLARIUM", active_id=2298, raw_size=300),
        start_timestamp=1_783_720_200,
        reason="New candle added to series.",
    )
    event = type(
        "Event",
        (),
        {
            "event_name": "first-candles",
            "candles": (
                type("Candle", (), {"active_id": 2298, "symbol": "XAU/USD OTC", "raw_size": 300})(),
            ),
        },
    )()

    diag.observe_history_event(
        event=event,
        store_results=(result,),
        bucket_before={(2298, 300): 1},
        bucket_after={(2298, 300): 2},
        history_before={(2298, 300): 1},
        history_after={(2298, 300): 1},
        readiness_before={(2298, 300): {"state": "LIMITED", "history_count": 1}},
        readiness_after={(2298, 300): {"state": "LIMITED", "history_count": 1}},
        now_ms=1_000,
    )

    assert read_report(tmp_path)["records"][0]["category"] == "HISTORY_NOT_INCREMENTED"


def test_history_count_diagnostic_classifies_store_key_mismatch(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    result = CandleStoreWriteResult(
        status="added",
        key=CandleSeriesKey(provider="POLARIUM", active_id=76, raw_size=300),
        start_timestamp=1_783_720_200,
        reason="New candle added to series.",
    )
    event = type(
        "Event",
        (),
        {
            "event_name": "first-candles",
            "candles": (
                type("Candle", (), {"active_id": 2298, "symbol": "XAU/USD OTC", "raw_size": 300})(),
            ),
        },
    )()

    diag.observe_history_event(
        event=event,
        store_results=(result,),
        bucket_before={(2298, 300): 0},
        bucket_after={(2298, 300): 0},
        history_before={(2298, 300): 0},
        history_after={(2298, 300): 0},
        readiness_before={(2298, 300): {"state": "BOOTSTRAPPING", "history_count": 0}},
        readiness_after={(2298, 300): {"state": "BOOTSTRAPPING", "history_count": 0}},
        now_ms=1_000,
    )

    assert read_report(tmp_path)["records"][0]["category"] == "STORE_KEY_MISMATCH"


def test_history_count_diagnostic_sanitizes_sensitive_reason(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    result = CandleStoreWriteResult(
        status="rejected",
        key=CandleSeriesKey(provider="POLARIUM", active_id=2298, raw_size=300),
        start_timestamp=1_783_720_200,
        reason="token cookie authorization bearer",
    )
    event = type(
        "Event",
        (),
        {
            "event_name": "first-candles",
            "candles": (
                type("Candle", (), {"active_id": 2298, "symbol": "XAU/USD OTC", "raw_size": 300})(),
            ),
        },
    )()

    diag.observe_history_event(
        event=event,
        store_results=(result,),
        bucket_before={(2298, 300): 0},
        bucket_after={(2298, 300): 0},
        history_before={(2298, 300): 0},
        history_after={(2298, 300): 0},
        readiness_before={(2298, 300): {"state": "BOOTSTRAPPING", "history_count": 0}},
        readiness_after={(2298, 300): {"state": "BOOTSTRAPPING", "history_count": 0}},
        now_ms=1_000,
    )

    rendered = (tmp_path / "history_count_report.json").read_text(encoding="utf-8").lower()

    assert "token cookie authorization bearer" not in rendered
    assert "sanitized_reason" in rendered


def test_history_count_diagnostic_preserves_m1_m5_m15(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store, history_count_diagnostic=diag)

    for raw_size, start in ((60, 1_783_720_020), (300, 1_783_720_200), (900, 1_783_720_800)):
        request_id = f"req-{raw_size}"
        runtime.process_message(request(2298, raw_size, request_id), origin="PAGE_NATIVE", now_ms=raw_size)
        runtime.process_message(history(2298, raw_size, request_id, start=start), origin="SERVER_INBOUND", now_ms=raw_size + 1)

    report = read_report(tmp_path)

    assert len(store.series(active_id=2298, raw_size=60)) == 1
    assert len(store.series(active_id=2298, raw_size=300)) == 1
    assert len(store.series(active_id=2298, raw_size=900)) == 1
    assert report["summary"]["total_records"] == 3
