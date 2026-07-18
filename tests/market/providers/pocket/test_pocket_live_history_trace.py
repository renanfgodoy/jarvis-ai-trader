from __future__ import annotations

import json
from pathlib import Path

from app.market.providers.pocket.cdp_models import PocketCDPEvent, PocketCDPTarget
from app.market.providers.pocket.cdp_observation_transport import PocketCDPObservationTransport
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.diagnostics import write_live_history_period_trace_reports, write_real_validation_report
from app.market.providers.pocket.fake_cdp_client import FakePocketCDPClient
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.runtime import PocketMarketRuntime


def test_history_trace_records_confirmed_update_history_new_fast() -> None:
    source = _source(
        (
            _socket_created(),
            _received('42["changeSymbol",{"asset":"EURUSD_otc","period":300}]', timestamp=1.0),
            _received('42["updateHistoryNewFast",{"asset":"EURUSD_otc","period":300,"candles":[[1700000000,1,1.2,1.3,0.9,0],[1700000300,1.2,1.4,1.5,1.1,0]]}]', timestamp=2.0),
        )
    )
    source.start()
    source.stop()

    report = source.transport.live_history_trace.history_report()

    assert report["final_category"] == "HISTORY_EVENT_CONFIRMED"
    assert report["historical_candles_detected"] == 2
    assert report["analysis_blocked"] is False


def test_history_trace_classifies_unknown_when_no_market_stream() -> None:
    source = _source(())
    source.start()
    source.stop()

    report = source.transport.live_history_trace.history_report()

    assert report["final_category"] == "HISTORY_EVENT_UNKNOWN"
    assert report["analysis_blocked"] is True
    assert report["analysis_block_reason"] == "POCKET_HISTORY_NOT_READY"


def test_history_trace_classifies_not_triggered_when_only_stream_exists() -> None:
    source = _source((_socket_created(), _received('42["updateStream",[["EURUSD_otc",1700000000.1,1.2]]]', timestamp=3.0)))
    source.start()
    source.stop()

    report = source.transport.live_history_trace.history_report()

    assert report["final_category"] == "HISTORY_EVENT_NOT_TRIGGERED"
    assert report["history_count"] == 0


def test_history_trace_records_update_charts_without_promoting_to_history() -> None:
    settings = json.dumps({"symbol": "EURUSD_otc", "chartPeriod": 300})
    source = _source((_socket_created(), _received(f'42["updateCharts",[{{"settings":{json.dumps(settings)}}}]]', timestamp=4.0)))
    source.start()
    source.stop()

    report = source.transport.live_history_trace.history_report()

    assert report["update_charts_samples"][0]["contains_visual_state"] is True
    assert report["update_charts_samples"][0]["contains_history"] is False


def test_http_trace_catalogs_candidate_without_headers_or_body(tmp_path: Path, monkeypatch) -> None:
    from app.market.providers.pocket import diagnostics

    monkeypatch.setattr(diagnostics, "LIVE_HISTORY_TRACE_JSON", tmp_path / "history.json")
    monkeypatch.setattr(diagnostics, "LIVE_HISTORY_TRACE_TXT", tmp_path / "history.txt")
    monkeypatch.setattr(diagnostics, "LIVE_PERIOD_TRACE_JSON", tmp_path / "period.json")
    monkeypatch.setattr(diagnostics, "LIVE_PERIOD_TRACE_TXT", tmp_path / "period.txt")
    monkeypatch.setattr(diagnostics, "LIVE_HTTP_HISTORY_TRACE_JSON", tmp_path / "http.json")
    monkeypatch.setattr(diagnostics, "LIVE_HTTP_HISTORY_TRACE_TXT", tmp_path / "http.txt")
    source = _source(
        (
            _request("req-1", "https://api-us-south.po.market/chart/history?token=secret&asset=EURUSD_otc"),
            _response("req-1", "https://api-us-south.po.market/chart/history?token=secret&asset=EURUSD_otc"),
        )
    )
    source.start()
    source.stop()

    reports = write_live_history_period_trace_reports(source)

    assert reports["http"]["candidate_count"] == 1
    text = (tmp_path / "http.txt").read_text(encoding="utf-8").lower()
    assert "secret" not in text
    assert "authorization" not in text
    assert "body_recorded=false" in text


def test_history_trace_detects_history_on_auxiliary_socket() -> None:
    source = _source(
            (
                _socket_created(request_id="market"),
                PocketCDPEvent("Network.webSocketCreated", {"requestId": "aux", "timestamp": 0.6, "url": "wss://auxiliary.po.market/socket.io/?EIO=4&transport=websocket"}),
                _received('42["updateStream",[["EURUSD_otc",1700000000.1,1.2]]]', request_id="market"),
                _received('42["updateHistoryNewFast",{"asset":"EURUSD_otc","period":60,"candles":[[1700000000,1,1.2,1.3,0.9,0]]}]', request_id="aux"),
            )
        )
    source.start()
    source.stop()

    report = source.transport.live_history_trace.history_report()

    assert report["final_category"] == "HISTORY_EVENT_OTHER_SOCKET"


def test_real_validation_report_includes_history_and_period_classification(tmp_path: Path, monkeypatch) -> None:
    from app.market.providers.pocket import diagnostics

    monkeypatch.setattr(diagnostics, "REAL_VALIDATION_JSON", tmp_path / "real.json")
    monkeypatch.setattr(diagnostics, "REAL_VALIDATION_TXT", tmp_path / "real.txt")
    source = _source((_socket_created(), _received('42["changeSymbol",{"asset":"EURUSD_otc","period":60}]'), _received('42["updateStream",[["EURUSD_otc",1700000000.1,1.2]]]')))
    source.start()
    source.stop()

    report = write_real_validation_report(source, {"observation_mode": "REAL_PASSIVE_CDP"})

    assert report["history_category"] == "HISTORY_EVENT_NOT_TRIGGERED"
    assert report["period_source"] == "changeSymbol"
    assert report["atomic_context_classification"] == "ATOMIC_CONTEXT_CONFIRMED"


def _source(events):
    return PocketReadOnlyLiveSource(
        PocketCDPObservationTransport(FakePocketCDPClient(targets=_targets(), events=events), config=PocketProviderConfig(preserve_store_on_stop=True)),
        PocketMarketRuntime(config=PocketProviderConfig(preserve_store_on_stop=True)),
    )


def _targets():
    return (PocketCDPTarget("pocket", "page", "https://pocketoption.com/pt/cabinet/demo-quick-high-low/"),)


def _socket_created(request_id: str = "market"):
    return PocketCDPEvent(
        "Network.webSocketCreated",
        {
            "requestId": request_id,
            "timestamp": 0.5,
            "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket",
        },
    )


def _received(payload: str, *, request_id: str = "market", timestamp: float = 1.0):
    return PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": request_id, "timestamp": timestamp, "response": {"payloadData": payload}})


def _request(request_id: str, url: str):
    return PocketCDPEvent(
        "Network.requestWillBeSent",
        {
            "requestId": request_id,
            "timestamp": 1.0,
            "request": {"url": url, "method": "GET", "headers": {"Authorization": "secret"}},
            "initiator": {"type": "script"},
        },
    )


def _response(request_id: str, url: str):
    return PocketCDPEvent(
        "Network.responseReceived",
        {
            "requestId": request_id,
            "timestamp": 1.1,
            "response": {"url": url, "status": 200, "mimeType": "application/json", "headers": {"Authorization": "secret"}},
        },
    )
