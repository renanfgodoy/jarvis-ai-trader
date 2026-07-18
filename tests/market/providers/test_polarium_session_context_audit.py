from __future__ import annotations

from app.market.providers.polarium.live_source import PolariumCDPLiveSource
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.providers.polarium.session_context_audit import SessionContextAudit
from app.market.store import CandleStore

from tests.market.providers.test_polarium_cdp_live_source import cdp_socket_created, disabled_config
from tests.market.providers.test_polarium_market_feed_runtime import candles_generated_payload, page_native_subscribe_candle


def test_session_context_audit_records_visible_context_update_with_bucket_crosscheck(tmp_path) -> None:
    audit = SessionContextAudit(
        report_json=tmp_path / "session_context_audit.json",
        report_txt=tmp_path / "session_context_audit.txt",
    )
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store, session_context_audit=audit)

    runtime.process_message(page_native_subscribe_candle(76, 60), origin="PAGE_NATIVE", now_ms=1000)
    runtime.process_message(candles_generated_payload(76), origin="SERVER_INBOUND", now_ms=2000)

    records = [record.sanitized() for record in audit.records if record.kind == "SESSION_CONTEXT_UPDATE"]
    assert records
    assert records[0]["origin"] == "PAGE_NATIVE"
    assert records[0]["old_active_id"] is None
    assert records[0]["new_active_id"] == 76
    assert records[0]["new_raw_size"] == 60
    assert records[0]["bucket_exists"] is False
    assert records[-1]["origin"] == "MARKET_WS"
    assert records[-1]["new_active_id"] == 76
    assert records[-1]["bucket_exists"] is True
    assert "POLARIUM:76:60" in records[-1]["buckets"]
    assert records[-1]["file"].endswith("runtime.py")
    assert records[-1]["caller"] == "_update_session_context"


def test_session_context_audit_records_cdp_context_markers_without_payload_or_secrets(tmp_path) -> None:
    audit = SessionContextAudit(
        report_json=tmp_path / "session_context_audit.json",
        report_txt=tmp_path / "session_context_audit.txt",
    )
    runtime = PolariumMarketFeedRuntime(CandleStore(), session_context_audit=audit)
    source = PolariumCDPLiveSource(runtime, disabled_config())
    message = {
        "name": "changeSymbol",
        "request_id": "safe-request",
        "msg": {
            "body": {
                "active_id": 2298,
                "symbol": "USDBRL-OTC",
                "token": "must-not-appear",
            }
        },
    }

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(
        {
            "method": "Network.webSocketFrameSent",
            "params": {
                "requestId": "ws-1",
                "targetId": "target-1",
                "response": {"payloadData": __import__("json").dumps(message)},
            },
        }
    )

    cdp_records = [record.sanitized() for record in audit.records if record.kind == "CDP_CONTEXT_EVENT"]
    assert len(cdp_records) == 1
    record = cdp_records[0]
    assert record["origin"] == "PAGE_NATIVE"
    assert record["received_active_id"] == 2298
    assert record["received_symbol"] == "USDBRL-OTC"
    assert record["frame"] == "Network.webSocketFrameSent"
    assert record["request_id"] == "safe-request"
    assert record["websocket"] == "ws-1"
    assert record["target_id"] == "target-1"
    serialized = __import__("json").dumps(record).lower()
    assert "must-not-appear" not in serialized
    assert "token" not in serialized


def test_session_context_audit_writes_json_and_timeline_reports(tmp_path) -> None:
    audit = SessionContextAudit(
        report_json=tmp_path / "session_context_audit.json",
        report_txt=tmp_path / "session_context_audit.txt",
    )
    runtime = PolariumMarketFeedRuntime(CandleStore(), session_context_audit=audit)

    runtime.process_message(page_native_subscribe_candle(2298, 300), origin="PAGE_NATIVE", now_ms=3000)

    report_json = tmp_path / "session_context_audit.json"
    report_txt = tmp_path / "session_context_audit.txt"
    assert report_json.exists()
    assert report_txt.exists()
    assert "Friday Trade - Polarium Session Context Audit" in report_txt.read_text()
    assert "CandleStore bucket exists" in report_txt.read_text()
