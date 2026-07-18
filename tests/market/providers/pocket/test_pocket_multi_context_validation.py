from __future__ import annotations

from pathlib import Path

from app.market.providers.pocket.cdp_models import PocketCDPEvent, PocketCDPTarget
from app.market.providers.pocket.cdp_observation_transport import PocketCDPObservationTransport
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.diagnostics import write_multi_context_validation_reports
from app.market.providers.pocket.fake_cdp_client import FakePocketCDPClient
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.multi_context_validation import build_bucket_isolation_report, validate_multi_context_source
from app.market.providers.pocket.runtime import PocketMarketRuntime


def test_multi_context_validation_passes_four_contexts_and_revisit() -> None:
    source = _source(_multi_context_events())
    source.start()
    source.stop()

    report = validate_multi_context_source(source)

    assert report["global_status"] == "PASS"
    assert report["failure_categories"] == []
    assert {item["bucket_key"] for item in report["context_results"]} == {
        "POCKET:EURUSD_otc:60",
        "POCKET:EURUSD_otc:300",
        "POCKET:AUDUSD_otc:900",
        "POCKET:USDBRL_otc:300",
    }
    assert report["revisit"]["status"] == "PASS"
    assert report["outbound_messages_originated_by_friday"] == 0
    assert report["observer_stopped_cleanly"] is True


def test_bucket_isolation_detects_mixed_asset() -> None:
    source = _source(_multi_context_events())
    source.start()
    bad = source.runtime.store.candles("POCKET:EURUSD_otc:60")[-1].__class__(
        provider="POCKET",
        asset="AUDUSD_otc",
        period=60,
        timeframe="M1",
        timestamp=1900000000.0,
        open=1.0,
        high=1.0,
        low=1.0,
        close=1.0,
        volume=None,
        source_event="test",
        is_realtime=True,
    )
    source.runtime.store._series["POCKET:EURUSD_otc:60"][bad.timestamp] = bad
    source.stop()

    report = build_bucket_isolation_report(source.runtime)

    assert "ASSET_BUCKET_MIX" in report["failure_categories"]
    assert any(row["isolation_status"] == "MIXED_ASSET" for row in report["buckets"])


def test_multi_context_validation_marks_missing_history_as_failure() -> None:
    source = _source((_socket_created(), _change("EURUSD_otc", 60, 1.0), _stream("EURUSD_otc", 1.5)))
    source.start()
    source.stop()

    report = validate_multi_context_source(source)
    eurusd_m1 = next(item for item in report["context_results"] if item["bucket_key"] == "POCKET:EURUSD_otc:60")

    assert report["global_status"] == "FAIL"
    assert "HISTORY_NOT_OBSERVED_FOR_CONTEXT" in eurusd_m1["failure_categories"]
    assert eurusd_m1["status"] == "PARTIAL"


def test_multi_context_reports_are_written_sanitized(tmp_path: Path, monkeypatch) -> None:
    from app.market.providers.pocket import diagnostics

    monkeypatch.setattr(diagnostics, "MULTI_CONTEXT_VALIDATION_JSON", tmp_path / "multi.json")
    monkeypatch.setattr(diagnostics, "MULTI_CONTEXT_VALIDATION_TXT", tmp_path / "multi.txt")
    monkeypatch.setattr(diagnostics, "BUCKET_ISOLATION_JSON", tmp_path / "buckets.json")
    monkeypatch.setattr(diagnostics, "BUCKET_ISOLATION_TXT", tmp_path / "buckets.txt")
    source = _source(_multi_context_events())
    source.start()
    source.stop()

    reports = write_multi_context_validation_reports(source)

    assert reports["validation"]["global_status"] == "PASS"
    for path in tmp_path.iterdir():
        text = path.read_text(encoding="utf-8").lower()
        assert "authorization" not in text
        assert "cookie" not in text
        assert "token" not in text


def _source(events):
    config = PocketProviderConfig(preserve_store_on_stop=True)
    return PocketReadOnlyLiveSource(
        PocketCDPObservationTransport(FakePocketCDPClient(targets=_targets(), events=events), config=config),
        PocketMarketRuntime(config=config),
    )


def _targets():
    return (PocketCDPTarget("pocket", "page", "https://pocketoption.com/pt/cabinet/demo-quick-high-low/"),)


def _multi_context_events():
    events = [_socket_created()]
    timestamp = 1.0
    for asset, period in (
        ("EURUSD_otc", 60),
        ("EURUSD_otc", 300),
        ("AUDUSD_otc", 900),
        ("USDBRL_otc", 300),
        ("EURUSD_otc", 60),
    ):
        events.append(_change(asset, period, timestamp))
        events.append(_history(asset, period, timestamp + 0.1))
        events.append(_stream(asset, timestamp + 0.2))
        timestamp += 1.0
    return tuple(events)


def _socket_created():
    return PocketCDPEvent(
        "Network.webSocketCreated",
        {
            "requestId": "market",
            "timestamp": 0.5,
            "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket",
        },
    )


def _change(asset: str, period: int, timestamp: float):
    return PocketCDPEvent(
        "Network.webSocketFrameSent",
        {"requestId": "market", "timestamp": timestamp, "response": {"payloadData": f'42["changeSymbol",{{"asset":"{asset}","period":{period}}}]'}},
    )


def _history(asset: str, period: int, timestamp: float):
    candles = []
    base = 1700000000
    for index in range(50):
        start = base + index * period
        price = 1.0 + index / 1000
        candles.append(f"[{start},{price:.5f},{price + 0.0001:.5f},{price + 0.0002:.5f},{price - 0.0002:.5f},0]")
    return PocketCDPEvent(
        "Network.webSocketFrameReceived",
        {
            "requestId": "market",
            "timestamp": timestamp,
            "response": {"payloadData": f'42["updateHistoryNewFast",{{"asset":"{asset}","period":{period},"candles":[{",".join(candles)}]}}]'},
        },
    )


def _stream(asset: str, timestamp: float):
    return PocketCDPEvent(
        "Network.webSocketFrameReceived",
        {"requestId": "market", "timestamp": timestamp, "response": {"payloadData": f'42["updateStream",[["{asset}",{1700001000 + timestamp:.3f},1.23456]]]'}},
    )
