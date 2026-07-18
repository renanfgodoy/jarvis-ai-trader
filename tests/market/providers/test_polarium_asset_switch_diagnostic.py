from __future__ import annotations

import json
from pathlib import Path

from app.market.providers.polarium.asset_switch_diagnostic import AssetSwitchDiagnostic
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.store import CandleStore


def request(active_id: int, raw_size: int, request_id: str) -> dict:
    return {
        "name": "sendMessage",
        "request_id": request_id,
        "msg": {"name": "get-first-candles", "body": {"active_id": active_id, "size": raw_size}},
    }


def metadata(active_id: int, symbol: str) -> dict:
    return {"name": "asset-metadata", "msg": {"body": {"active_id": active_id, "symbol": symbol}}}


def subscribe_without_timeframe(active_id: int) -> dict:
    return {
        "name": "subscribeMessage",
        "msg": {"name": "candles-generated", "params": {"routingFilters": {"active_id": active_id}}},
    }


def history(active_id: int, raw_size: int, request_id: str, *, start: int, count: int = 1, symbol: str = "XAU/USD OTC") -> dict:
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
                        "from": start + index * raw_size,
                        "to": start + (index + 1) * raw_size,
                        "open": 5.41,
                        "close": 5.42,
                        "min": 5.40,
                        "max": 5.43,
                        "volume": 0,
                        "size": raw_size,
                    }
                    for index in range(count)
                ],
            }
        },
    }


def diagnostic(tmp_path: Path) -> AssetSwitchDiagnostic:
    return AssetSwitchDiagnostic(
        report_json=tmp_path / "asset_switch_report.json",
        report_txt=tmp_path / "asset_switch_report.txt",
    )


def read_report(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "asset_switch_report.json").read_text(encoding="utf-8"))


def test_atomic_asset_switch_does_not_publish_partial_selection_without_raw_size(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), asset_switch_diagnostic=diag)

    runtime.process_message(metadata(1857, "XAU/USD OTC"), origin="PAGE_NATIVE", now_ms=500)
    runtime.process_message(subscribe_without_timeframe(1857), origin="PAGE_NATIVE", now_ms=1_000)

    context = runtime.status().sanitized()["session_context"]

    assert context["active_id"] is None
    assert context["raw_size"] is None
    assert diag.records == ()
    assert not (tmp_path / "asset_switch_report.json").exists()


def test_atomic_asset_switch_publishes_only_complete_context_and_never_null_bucket(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), asset_switch_diagnostic=diag)

    runtime.process_message(metadata(1857, "XAU/USD OTC"), origin="PAGE_NATIVE", now_ms=500)
    runtime.process_message(subscribe_without_timeframe(1857), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(request(1857, 300, "req-xau"), origin="PAGE_NATIVE", now_ms=2_000)

    record = read_report(tmp_path)["records"][0]
    context = runtime.status().sanitized()["session_context"]

    assert context["active_id"] == 1857
    assert context["symbol"] == "XAU/USD OTC"
    assert context["raw_size"] == 300
    assert record["raw_size_after"] == 300
    assert record["bucket_after"] == "POLARIUM:1857:300"
    assert record["category"] != "RACE_CONDITION"


def test_asset_switch_diagnostic_records_successful_switch_bootstrap_and_chart_update(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), asset_switch_diagnostic=diag)

    runtime.process_message(request(2298, 300, "req-xau"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(history(2298, 300, "req-xau", start=1_783_720_200, count=50), origin="SERVER_INBOUND", now_ms=2_000)
    diag.observe_chart_request(active_id=2298, raw_size=300, symbol="XAU/USD OTC", candle_count=50, now_ms=3_000)

    report = read_report(tmp_path)
    record = report["records"][0]

    assert (tmp_path / "asset_switch_report.txt").exists()
    assert record["active_id_after"] == 2298
    assert record["raw_size_after"] == 300
    assert record["request_started"] is True
    assert record["request_finished"] is True
    assert record["response_applied"] is True
    assert record["chart_updated"] is True
    assert record["frontend_updated"] is True
    assert record["category"] == "UNKNOWN"


def test_asset_switch_diagnostic_classifies_repeated_selection_without_switch(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    context = {"active_id": 2298, "raw_size": 300, "symbol": "XAU/USD OTC"}

    diag.observe_selection(
        previous_context=context,
        current_context=context,
        bucket_size_before=50,
        bucket_size_after=50,
        now_ms=1_000,
    )

    record = read_report(tmp_path)["records"][0]

    assert record["category"] == "ASSET_NOT_SWITCHED"
    assert record["failure_step"] == "SESSION_CONTEXT"


def test_asset_switch_diagnostic_discards_old_bootstrap_response_without_race_condition(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    runtime = PolariumMarketFeedRuntime(CandleStore(), asset_switch_diagnostic=diag)

    runtime.process_message(request(76, 300, "req-eur"), origin="PAGE_NATIVE", now_ms=1_000)
    runtime.process_message(request(2298, 300, "req-xau"), origin="PAGE_NATIVE", now_ms=2_000)
    runtime.process_message(history(76, 300, "req-eur", start=1_783_720_200, count=1, symbol="EUR/USD OTC"), origin="SERVER_INBOUND", now_ms=3_000)

    records = read_report(tmp_path)["records"]
    eur_record = next(record for record in records if record["active_id_after"] == 76)

    assert eur_record["category"] == "BOOTSTRAP_DISCARDED"
    assert eur_record["response_ignored"] is True
    assert eur_record["request_discarded"] is True


def test_asset_switch_diagnostic_classifies_bucket_not_updated(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_selection(
        previous_context={"active_id": 76, "raw_size": 300, "symbol": "EUR/USD OTC"},
        current_context={"active_id": 2298, "raw_size": 300, "symbol": "XAU/USD OTC"},
        bucket_size_before=10,
        bucket_size_after=0,
        now_ms=1_000,
    )
    diag.observe_bootstrap_started(active_id=2298, raw_size=300, now_ms=1_100)
    diag.observe_bootstrap_finished(
        active_id=2298,
        raw_size=300,
        symbol="XAU/USD OTC",
        visible_active_id=2298,
        visible_raw_size=300,
        bucket_size_before=0,
        bucket_size_after=0,
        history_count=0,
        readiness_state="BOOTSTRAPPING",
        now_ms=2_000,
    )

    record = read_report(tmp_path)["records"][0]

    assert record["category"] == "BUCKET_NOT_UPDATED"
    assert record["failure_step"] == "CANDLE_BUCKET"


def test_asset_switch_diagnostic_accepts_ready_bucket_without_growth_when_chart_updated(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_selection(
        previous_context={"active_id": 76, "raw_size": 300, "symbol": "EUR/USD OTC"},
        current_context={"active_id": 2298, "raw_size": 300, "symbol": "XAU/USD OTC"},
        bucket_size_before=315,
        bucket_size_after=315,
        now_ms=1_000,
    )
    diag.observe_bootstrap_started(active_id=2298, raw_size=300, now_ms=1_100)
    diag.observe_chart_request(active_id=2298, raw_size=300, symbol="XAU/USD OTC", candle_count=315, now_ms=1_500)
    diag.observe_bootstrap_finished(
        active_id=2298,
        raw_size=300,
        symbol="XAU/USD OTC",
        visible_active_id=2298,
        visible_raw_size=300,
        bucket_size_before=315,
        bucket_size_after=315,
        history_count=315,
        readiness_state="READY",
        now_ms=2_000,
    )

    record = read_report(tmp_path)["records"][0]

    assert record["category"] == "UNKNOWN"
    assert record["failure_step"] == "NO_DIVERGENCE_CLASSIFIED"
    assert record["response_applied"] is True
    assert record["chart_updated"] is True
    assert record["frontend_updated"] is True


def test_asset_switch_diagnostic_ready_bucket_without_chart_waits_for_chart_request(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_selection(
        previous_context={"active_id": 76, "raw_size": 300, "symbol": "EUR/USD OTC"},
        current_context={"active_id": 2298, "raw_size": 300, "symbol": "XAU/USD OTC"},
        bucket_size_before=315,
        bucket_size_after=315,
        now_ms=1_000,
    )
    diag.observe_bootstrap_started(active_id=2298, raw_size=300, now_ms=1_100)
    diag.observe_bootstrap_finished(
        active_id=2298,
        raw_size=300,
        symbol="XAU/USD OTC",
        visible_active_id=2298,
        visible_raw_size=300,
        bucket_size_before=315,
        bucket_size_after=315,
        history_count=315,
        readiness_state="READY",
        now_ms=2_000,
    )

    record = read_report(tmp_path)["records"][0]

    assert record["category"] == "CHART_NOT_UPDATED"
    assert record["failure_reason"] == "Ready bucket exists; waiting for chart request."
    assert record["response_applied"] is True


def test_asset_switch_diagnostic_detects_frontend_stale_chart_source(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_selection(
        previous_context={"active_id": 76, "raw_size": 300, "symbol": "EUR/USD OTC"},
        current_context={"active_id": 2298, "raw_size": 300, "symbol": "XAU/USD OTC"},
        bucket_size_before=50,
        bucket_size_after=50,
        now_ms=1_000,
    )
    diag.observe_chart_request(active_id=76, raw_size=300, symbol="EUR/USD OTC", candle_count=50, now_ms=1_500)

    record = read_report(tmp_path)["records"][0]

    assert record["category"] == "FRONTEND_STALE"
    assert record["chart_source_after"] == "POLARIUM:76:300"
    assert record["frontend_updated"] is False


def test_asset_switch_diagnostic_ready_bucket_with_wrong_chart_source_stays_frontend_stale(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_selection(
        previous_context={"active_id": 76, "raw_size": 300, "symbol": "EUR/USD OTC"},
        current_context={"active_id": 2298, "raw_size": 300, "symbol": "XAU/USD OTC"},
        bucket_size_before=315,
        bucket_size_after=315,
        now_ms=1_000,
    )
    diag.observe_bootstrap_started(active_id=2298, raw_size=300, now_ms=1_100)
    diag.observe_chart_request(active_id=76, raw_size=300, symbol="EUR/USD OTC", candle_count=315, now_ms=1_500)
    diag.observe_bootstrap_finished(
        active_id=2298,
        raw_size=300,
        symbol="XAU/USD OTC",
        visible_active_id=2298,
        visible_raw_size=300,
        bucket_size_before=315,
        bucket_size_after=315,
        history_count=315,
        readiness_state="READY",
        now_ms=2_000,
    )

    record = read_report(tmp_path)["records"][0]

    assert record["category"] == "FRONTEND_STALE"
    assert record["response_applied"] is False
    assert record["chart_source_after"] == "POLARIUM:76:300"


def test_asset_switch_diagnostic_discarded_ready_response_is_not_success(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_selection(
        previous_context={"active_id": 76, "raw_size": 300, "symbol": "EUR/USD OTC"},
        current_context={"active_id": 2298, "raw_size": 300, "symbol": "XAU/USD OTC"},
        bucket_size_before=315,
        bucket_size_after=315,
        now_ms=1_000,
    )
    diag.observe_bootstrap_started(active_id=2298, raw_size=300, now_ms=1_100)
    diag.observe_chart_request(active_id=2298, raw_size=300, symbol="XAU/USD OTC", candle_count=315, now_ms=1_500)
    diag.observe_bootstrap_finished(
        active_id=2298,
        raw_size=300,
        symbol="XAU/USD OTC",
        visible_active_id=76,
        visible_raw_size=300,
        bucket_size_before=315,
        bucket_size_after=315,
        history_count=315,
        readiness_state="READY",
        now_ms=2_000,
    )

    record = read_report(tmp_path)["records"][0]

    assert record["category"] == "BOOTSTRAP_DISCARDED"
    assert record["response_ignored"] is True
    assert record["request_discarded"] is True


def test_asset_switch_diagnostic_sanitizes_sensitive_symbol(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    diag.observe_selection(
        previous_context={"active_id": 76, "raw_size": 60, "symbol": "EUR/USD OTC"},
        current_context={"active_id": 2298, "raw_size": 60, "symbol": "token cookie authorization bearer"},
        bucket_size_before=0,
        bucket_size_after=0,
        now_ms=1_000,
    )

    rendered = (tmp_path / "asset_switch_report.json").read_text(encoding="utf-8").lower()

    assert "token cookie authorization bearer" not in rendered


def test_asset_switch_diagnostic_preserves_m1_m5_m15(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store, asset_switch_diagnostic=diag)

    for raw_size, start in ((60, 1_783_720_020), (300, 1_783_720_200), (900, 1_783_720_800)):
        request_id = f"req-{raw_size}"
        runtime.process_message(request(2298, raw_size, request_id), origin="PAGE_NATIVE", now_ms=raw_size)
        runtime.process_message(history(2298, raw_size, request_id, start=start, count=1), origin="SERVER_INBOUND", now_ms=raw_size + 1)
        diag.observe_chart_request(active_id=2298, raw_size=raw_size, symbol="XAU/USD OTC", candle_count=1, now_ms=raw_size + 2)

    report = read_report(tmp_path)

    assert len(store.series(active_id=2298, raw_size=60)) == 1
    assert len(store.series(active_id=2298, raw_size=300)) == 1
    assert len(store.series(active_id=2298, raw_size=900)) == 1
    assert report["summary"]["total_switches"] == 3
