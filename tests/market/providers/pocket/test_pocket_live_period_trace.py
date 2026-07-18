from __future__ import annotations

import json

from app.market.providers.pocket.cdp_models import PocketObservedFrame, PocketObservedSocket
from app.market.providers.pocket.live_period_trace import PocketLivePeriodTrace
from tools.pocket_discovery.socketio_parser import parse_socketio_frame


def test_period_trace_confirms_change_symbol_m1_m5_m15() -> None:
    trace = PocketLivePeriodTrace()

    for period, timeframe in ((60, "M1"), (300, "M5"), (900, "M15")):
        parsed = parse_socketio_frame(f'42["changeSymbol",{{"asset":"EURUSD_otc","period":{period}}}]')
        trace.record_event(event_name="changeSymbol", payload=parsed.payload, parsed=parsed, frame=_frame(), socket=_socket())
        assert trace.atomic_contexts[-1]["timeframe"] == timeframe

    report = trace.report()
    assert report["final_period_source"] == "changeSymbol"
    assert report["period_mapping"] == {60: "M1", 300: "M5", 900: "M15"}


def test_period_trace_ignores_period_absent_as_partial_context() -> None:
    trace = PocketLivePeriodTrace()
    parsed = parse_socketio_frame('42["changeSymbol",{"asset":"EURUSD_otc"}]')

    trace.record_event(event_name="changeSymbol", payload=parsed.payload, parsed=parsed, frame=_frame(), socket=_socket())

    assert trace.report()["context_classification"] == "PARTIAL_CONTEXT_IGNORED"
    assert trace.report()["analysis_blocked"] is True


def test_period_trace_records_chafor_candidate_but_keeps_lower_confidence() -> None:
    trace = PocketLivePeriodTrace()
    parsed = parse_socketio_frame('42["chafor",[["AUDUSD_otc",900]]]')

    trace.record_event(event_name="chafor", payload=parsed.payload, parsed=parsed, frame=_frame(), socket=_socket())
    report = trace.report()

    assert report["final_period_source"] == "chafor"
    assert report["sources"][0]["classification"] == "PERIOD_SOURCE_CANDIDATE_CHAFOR"
    assert report["atomic_contexts"][0]["bucket_key"] == "POCKET:AUDUSD_otc:900"


def test_period_trace_records_update_charts_candidate() -> None:
    trace = PocketLivePeriodTrace()
    settings = json.dumps({"symbol": "USDBRL_otc", "chartPeriod": 300})
    parsed = parse_socketio_frame(f'42["updateCharts",[{{"settings":{json.dumps(settings)}}}]]')

    trace.record_event(event_name="updateCharts", payload=parsed.payload, parsed=parsed, frame=_frame(), socket=_socket())
    report = trace.report()

    assert report["final_period_source"] == "updateCharts"
    assert report["current_asset"] == "USDBRL_otc"
    assert report["current_period"] == 300


def test_period_trace_detects_source_conflict_without_merging_partial_context() -> None:
    trace = PocketLivePeriodTrace()
    first = parse_socketio_frame('42["changeSymbol",{"asset":"EURUSD_otc","period":60}]')
    second = parse_socketio_frame('42["changeSymbol",{"asset":"AUDUSD_otc","period":900}]')

    trace.record_event(event_name="changeSymbol", payload=first.payload, parsed=first, frame=_frame(), socket=_socket())
    trace.record_event(event_name="changeSymbol", payload=second.payload, parsed=second, frame=_frame(), socket=_socket())

    assert trace.report()["context_classification"] == "CONTEXT_SOURCE_CONFLICT"


def _frame() -> PocketObservedFrame:
    return PocketObservedFrame("request", "target", "sent", 1.0, "")


def _socket() -> PocketObservedSocket:
    return PocketObservedSocket("request", "target", "unknown", "api-us-south.po.market", "/socket.io/", (), classification="MARKET_SOCKET", classification_reason="fixture")
