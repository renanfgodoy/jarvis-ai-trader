from __future__ import annotations

import json
from pathlib import Path

from app.market.providers.pocket.cdp_models import PocketObservedFrame, PocketObservedSocket
from app.market.providers.pocket.diagnostics import write_live_schema_trace_reports
from app.market.providers.pocket.fake_cdp_client import FakePocketCDPClient
from app.market.providers.pocket.live_schema_trace import PocketLiveSchemaTrace, build_schema_sample
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.cdp_observation_transport import PocketCDPObservationTransport
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.runtime import PocketMarketRuntime
from tools.pocket_discovery.socketio_parser import parse_socketio_frame
from tools.pocket_parser.stream_parser import parse_update_stream


def test_live_schema_trace_captures_shape_without_raw_payload_values() -> None:
    parsed = parse_socketio_frame('42["updateStream",{"data":["EURUSD_otc",1700000000.1,1.2],"meta":{"source":"live"}}]')
    sample = build_schema_sample("updateStream", parsed.payload, parsed, _frame(), _socket())

    assert sample["payload_root_type"] == "dict"
    assert "$.data" in sample["nested_key_paths"]
    assert "$.data[]" in sample["candidate_asset_paths"]
    assert "$.data[]" in sample["candidate_timestamp_paths"]
    assert "$.data[]" in sample["candidate_price_paths"]
    assert "1700000000.1" not in json.dumps(sample)


def test_live_schema_trace_deduplicates_and_limits_samples() -> None:
    trace = PocketLiveSchemaTrace(max_samples_per_event=1)
    parsed = parse_socketio_frame('42["updateStream",[["EURUSD_otc",1700000000.1,1.2]]]')

    trace.record_event(event_name="updateStream", payload=parsed.payload, parsed=parsed, frame=_frame(), socket=_socket())
    trace.record_event(event_name="updateStream", payload=parsed.payload, parsed=parsed, frame=_frame(), socket=_socket())

    assert trace.update_stream_report()["samples_count"] == 1


def test_socketio_parser_exposes_namespace_ack_and_multiple_arguments() -> None:
    frame = parse_socketio_frame('42/market,12["updateStream",{"asset":"EURUSD_otc"},[1,2,3]]')

    assert frame.namespace == "/market"
    assert frame.ack_id == "12"
    assert len(frame.args) == 2
    assert frame.payload == {"asset": "EURUSD_otc"}


def test_stream_parser_keeps_har_schema_and_rejects_unknown_live_wrapper() -> None:
    accepted, accepted_rejections = parse_update_stream([["EURUSD_otc", 1700000000.1, 1.2]], source_har="fixture", session_index=0, frame_index=0, sequence_start=0)
    rejected, rejected_rejections = parse_update_stream({"data": ["EURUSD_otc", 1700000000.1, 1.2]}, source_har="fixture", session_index=0, frame_index=1, sequence_start=0)

    assert len(accepted) == 1
    assert accepted_rejections == []
    assert rejected == []
    assert {item.code for item in rejected_rejections} == {"LIVE_STREAM_NESTING_UNSUPPORTED"}


def test_trace_reports_are_written_sanitized(tmp_path: Path, monkeypatch) -> None:
    from app.market.providers.pocket import diagnostics

    monkeypatch.setattr(diagnostics, "LIVE_STREAM_SCHEMA_JSON", tmp_path / "stream.json")
    monkeypatch.setattr(diagnostics, "LIVE_STREAM_SCHEMA_TXT", tmp_path / "stream.txt")
    monkeypatch.setattr(diagnostics, "CHAFOR_SCHEMA_JSON", tmp_path / "chafor.json")
    monkeypatch.setattr(diagnostics, "CHAFOR_SCHEMA_TXT", tmp_path / "chafor.txt")
    monkeypatch.setattr(diagnostics, "LIVE_HISTORY_ABSENCE_JSON", tmp_path / "history.json")
    monkeypatch.setattr(diagnostics, "LIVE_HISTORY_ABSENCE_TXT", tmp_path / "history.txt")
    events = (
        _event('42["updateStream",[["EURUSD_otc",1700000000.1,1.2]]]'),
        _event('42["chafor",{"asset":"EURUSD_otc","period":60}]'),
    )
    source = PocketReadOnlyLiveSource(
        PocketCDPObservationTransport(FakePocketCDPClient(targets=_targets(), events=events)),
        PocketMarketRuntime(config=PocketProviderConfig(preserve_store_on_stop=True)),
    )

    source.start()
    source.stop()
    reports = write_live_schema_trace_reports(source)

    assert reports["stream"]["samples_count"] == 1
    assert reports["chafor"]["samples_count"] == 1
    assert reports["history"]["category"] == "HISTORY_EVENT_NOT_OBSERVED"
    for path in tmp_path.iterdir():
        text = path.read_text(encoding="utf-8").lower()
        assert "authorization" not in text
        assert "cookie" not in text


def test_chafor_is_cataloged_but_not_routed_as_tick() -> None:
    trace = PocketLiveSchemaTrace()
    parsed = parse_socketio_frame('42["chafor",{"asset":"EURUSD_otc","period":60}]')

    trace.record_event(event_name="chafor", payload=parsed.payload, parsed=parsed, frame=_frame(), socket=_socket())
    report = trace.chafor_report()

    assert report["samples_count"] == 1
    assert report["routed_as_tick"] is False
    assert report["classification"] in {"MARKET_CONTROL", "UNKNOWN"}


def _frame() -> PocketObservedFrame:
    return PocketObservedFrame("request", "target", "received", 1.0, "")


def _socket() -> PocketObservedSocket:
    return PocketObservedSocket("request", "target", "unknown", "unknown", "unknown", (), classification="MARKET_SOCKET", classification_reason="fixture")


def _targets():
    from app.market.providers.pocket.cdp_models import PocketCDPTarget

    return (PocketCDPTarget("pocket", "page", "https://pocketoption.com/pt/cabinet/demo-quick-high-low/"),)


def _event(payload: str):
    from app.market.providers.pocket.cdp_models import PocketCDPEvent

    return PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "market", "timestamp": 1, "response": {"payloadData": payload}})
