from __future__ import annotations

import json
from pathlib import Path

from app.market.providers.polarium.historical_request_sequence import HistoricalRequestSequenceDiagnostic


def report(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "historical_request_sequence.json").read_text(encoding="utf-8"))


def diagnostic(tmp_path: Path) -> HistoricalRequestSequenceDiagnostic:
    return HistoricalRequestSequenceDiagnostic(
        report_json=tmp_path / "historical_request_sequence.json",
        report_txt=tmp_path / "historical_request_sequence.txt",
    )


def subscribe(active_id: int) -> dict:
    return {
        "name": "subscribeMessage",
        "msg": {"name": "candles-generated", "params": {"routingFilters": {"active_id": active_id}}},
    }


def get_first(active_id: int, raw_size: int, request_id: str) -> dict:
    return {
        "name": "sendMessage",
        "request_id": request_id,
        "msg": {"name": "get-first-candles", "body": {"active_id": active_id, "size": raw_size}},
    }


def historical_lot(active_id: int, raw_size: int, request_id: str) -> dict:
    return {
        "name": "sendMessage",
        "request_id": request_id,
        "msg": {
            "name": "candles",
            "body": {
                "active_id": active_id,
                "size": raw_size,
                "count": 100,
                "from": 1_783_700_000,
                "to": 1_783_730_000,
                "offset": 100,
            },
        },
    }


def test_historical_request_sequence_captures_sanitized_manual_and_programmatic_flows(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)

    diag.observe_outbound(subscribe(76), origin="PAGE_NATIVE", now_ms=1_000)
    diag.observe_outbound(get_first(76, 300, "native-first"), origin="PAGE_NATIVE", now_ms=1_100)
    diag.observe_outbound(historical_lot(76, 300, "native-lot"), origin="PAGE_NATIVE", now_ms=1_200)
    diag.observe_outbound(subscribe(76), origin="FRIDAY_PROGRAMMATIC", now_ms=2_000)
    diag.observe_outbound(get_first(76, 300, "friday-first"), origin="FRIDAY_PROGRAMMATIC", now_ms=2_100)

    payload = report(tmp_path)

    assert (tmp_path / "historical_request_sequence.txt").exists()
    assert payload["summary"]["manual_count"] == 3
    assert payload["summary"]["programmatic_count"] == 2
    assert payload["manual_flow"][2]["inner_name"] == "candles"
    assert payload["manual_flow"][2]["count"] == 100
    assert payload["manual_flow"][2]["from_timestamp"] == 1_783_700_000
    assert payload["manual_flow"][2]["to_timestamp"] == 1_783_730_000
    assert payload["manual_flow"][2]["offset"] == 100
    assert payload["missing_in_programmatic_flow"] == [
        {
            "manual_order": 3,
            "name": "sendMessage",
            "inner_name": "candles",
            "active_id": 76,
            "raw_size": 300,
            "count": 100,
            "from": 1_783_700_000,
            "to": 1_783_730_000,
            "offset": 100,
        }
    ]


def test_historical_request_sequence_ignores_non_market_and_sensitive_payloads(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)

    diag.observe_outbound(
        {"name": "authenticate", "authorization": "bearer secret", "msg": {"body": {"ssid": "secret"}}},
        origin="PAGE_NATIVE",
        now_ms=1_000,
    )
    diag.observe_outbound({"name": "sendMessage", "msg": {"name": "get-first-candles", "body": {"active_id": 76, "size": 60}}}, origin="PAGE_NATIVE", now_ms=2_000)

    rendered = (tmp_path / "historical_request_sequence.json").read_text(encoding="utf-8").lower()
    payload = report(tmp_path)

    assert payload["summary"]["total_entries"] == 1
    assert "bearer secret" not in rendered
    assert "ssid" not in rendered
    assert "authorization" not in rendered
