from __future__ import annotations

import json
from pathlib import Path

from app.market.providers.polarium.get_candles_envelope import GetCandlesEnvelopeDiagnostic


def diagnostic(tmp_path: Path) -> GetCandlesEnvelopeDiagnostic:
    return GetCandlesEnvelopeDiagnostic(
        report_json=tmp_path / "get_candles_envelope_report.json",
        report_txt=tmp_path / "get_candles_envelope_report.txt",
    )


def report(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "get_candles_envelope_report.json").read_text(encoding="utf-8"))


def test_get_candles_envelope_captures_nested_shape_types_and_safe_values(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)

    diag.observe_outbound(
        {
            "name": "sendMessage",
            "request_id": "native-1",
            "msg": {
                "name": "get-candles",
                "body": {
                    "active_id": 76,
                    "size": 300,
                    "from": 1_783_700_000,
                    "to": 1_783_730_000,
                    "count": 200,
                    "offset": 100,
                    "extended": {"index": 2, "live": True},
                },
            },
        },
        origin="PAGE_NATIVE",
        now_ms=1_000,
    )

    payload = report(tmp_path)
    native = payload["native_envelopes"][0]

    assert native["payload_path"] == "msg.body"
    assert native["paths"]["msg.body.active_id"] == "integer"
    assert native["paths"]["msg.body.extended.live"] == "boolean"
    assert native["safe_values"]["msg.body.active_id"] == 76
    assert native["safe_values"]["msg.body.from"] == 1_783_700_000
    assert native["safe_values"]["msg.body.extended.index"] == 2
    assert "NATIVE ENVELOPE" in (tmp_path / "get_candles_envelope_report.txt").read_text(encoding="utf-8")


def test_get_candles_envelope_sanitizes_sensitive_nested_fields(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)

    diag.observe_outbound(
        {
            "name": "sendMessage",
            "request_id": "native-secret",
            "authorization": "Bearer should-not-appear",
            "msg": {
                "name": "get-candles",
                "headers": {"cookie": "should-not-appear"},
                "body": {
                    "active_id": 76,
                    "size": 60,
                    "authToken": "should-not-appear",
                    "ssid": "should-not-appear",
                },
            },
        },
        origin="PAGE_NATIVE",
        now_ms=1_000,
    )

    rendered = (tmp_path / "get_candles_envelope_report.json").read_text(encoding="utf-8").lower()

    assert "should-not-appear" not in rendered
    assert "authorization" not in rendered
    assert "cookie" not in rendered
    assert "ssid" not in rendered
    assert "authtoken" not in rendered


def test_get_candles_envelope_compares_native_and_programmatic_missing_fields(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)

    diag.observe_outbound(
        {
            "name": "sendMessage",
            "request_id": "native-1",
            "msg": {"name": "get-candles", "body": {"active_id": 76, "size": 300, "from": 1_783_700_000, "to": 1_783_730_000, "count": 200}},
        },
        origin="PAGE_NATIVE",
        now_ms=1_000,
    )
    diag.observe_outbound(
        {
            "name": "sendMessage",
            "request_id": "friday-1",
            "msg": {"name": "get-candles", "body": {"active_id": 76, "size": 300}},
        },
        origin="FRIDAY_PROGRAMMATIC",
        now_ms=2_000,
    )

    payload = report(tmp_path)

    assert payload["summary"]["native_get_candles_count"] == 1
    assert payload["summary"]["programmatic_get_candles_count"] == 1
    assert "msg.body.from" in payload["missing_fields"]
    assert "msg.body.to" in payload["missing_fields"]
    assert "msg.body.count" in payload["missing_fields"]
    assert payload["structural_differences"]["status"] == "COMPARED"


def test_get_candles_envelope_records_duplicate_bootstrap_owners_by_context(tmp_path: Path) -> None:
    diag = diagnostic(tmp_path)

    diag.observe_bootstrap_owner(owner="NATIVE_ORCHESTRATOR", active_id=76, raw_size=300, request_id="friday-native", now_ms=1_000)
    diag.observe_bootstrap_owner(owner="AUTO_VISIBLE_CONTEXT", active_id=76, raw_size=300, request_id="friday-auto", now_ms=1_100)
    diag.observe_bootstrap_owner(owner="AUTO_VISIBLE_CONTEXT", active_id=76, raw_size=60, request_id="friday-auto-m1", now_ms=1_200)

    payload = report(tmp_path)

    assert payload["summary"]["duplicate_bootstrap_owner_count"] == 1
    assert payload["duplicate_bootstrap_owners"] == [
        {"active_id": 76, "raw_size": 300, "owners": ["AUTO_VISIBLE_CONTEXT", "NATIVE_ORCHESTRATOR"]}
    ]
