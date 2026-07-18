from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes import dev_market_selection
from app.main import app
from app.market.providers.polarium.get_candles_envelope import GetCandlesEnvelopeDiagnostic
from app.market.providers.polarium.historical_request_sequence import HistoricalRequestSequenceDiagnostic
from app.market.providers.polarium import live_source
from app.market.providers.polarium.live_source import MarketSocketSendResult, PolariumCDPLiveSource, PolariumCDPLiveSourceConfig, ProgrammaticMarketSelectionResult
from app.market.providers.polarium.live_bootstrap_diagnostic import LiveBootstrapRequestDiagnostic
from app.market.providers.polarium.target_manager import CDPTarget
from app.market.providers.polarium.runtime import PolariumMarketFeedRuntime
from app.market.store import CandleStore
from app.core.config import Settings


def cdp_socket_created() -> dict:
    return {
        "method": "Network.webSocketCreated",
        "params": {
            "requestId": "ws-1",
            "url": "wss://ws.trade.polariumbroker.com/echo/websocket",
        },
    }


def cdp_frame_received(message: dict) -> dict:
    return {
        "method": "Network.webSocketFrameReceived",
        "params": {
            "requestId": "ws-1",
            "response": {"payloadData": __import__("json").dumps(message)},
        },
    }


def cdp_frame_sent(message: dict) -> dict:
    return cdp_frame_sent_on("ws-1", message)


def cdp_frame_sent_on(request_id: str, message: dict) -> dict:
    return {
        "method": "Network.webSocketFrameSent",
        "params": {
            "requestId": request_id,
            "response": {"payloadData": __import__("json").dumps(message)},
        },
    }


def page_native_subscribe_candle(active_id: int, raw_size: int = 60) -> dict:
    return {
        "name": "subscribeMessage",
        "msg": {
            "name": "candle-generated",
            "params": {"routingFilters": {"active_id": active_id, "size": raw_size}},
        },
    }


def candles_generated_message(active_id: int = 76, start: int = 1_783_720_000) -> dict:
    return {
        "name": "candles-generated",
        "msg": {
            "result": {
                "active_id": active_id,
                "at": start,
                "value": 1.1010,
                "candles": {
                    "60": {"from": start, "to": start + 60, "open": 1.1000, "min": 1.0990, "max": 1.1020},
                    "300": {"from": start, "to": start + 300, "open": 1.1000, "min": 1.0985, "max": 1.1030},
                    "900": {"from": start, "to": start + 900, "open": 1.1000, "min": 1.0980, "max": 1.1040},
                },
            }
        },
    }


def first_candles_message(active_id: int, raw_size: int, request_id: str) -> dict:
    return history_message("first-candles", active_id, raw_size, request_id, count=50)


def history_message(event_name: str, active_id: int, raw_size: int, request_id: str, *, count: int, start: int = 1_783_720_000) -> dict:
    if raw_size in {300, 900} and start % raw_size != 0:
        start += raw_size - (start % raw_size)
    return {
        "name": event_name,
        "request_id": request_id,
        "msg": {
            "body": {
                "active_id": active_id,
                "symbol": "EUR/USD OTC" if active_id == 76 else "XAU/USD OTC",
                "size": raw_size,
                "candles": [
                    {
                        "from": start + index * raw_size,
                        "to": start + (index + 1) * raw_size,
                        "open": 1.1,
                        "close": 1.11,
                        "min": 1.09,
                        "max": 1.12,
                        "volume": 0,
                        "size": raw_size,
                    }
                    for index in range(count)
                ],
            }
        },
    }


def disabled_config(*, programmatic_selection_enabled: bool = False) -> PolariumCDPLiveSourceConfig:
    return PolariumCDPLiveSourceConfig(
        enabled=False,
        chrome_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        profile_dir=".jarvis_cache/polarium_cdp_live/test-profile",
        trade_url="https://trade.polariumbroker.com/traderoom",
        friday_frontend_url="http://127.0.0.1:5173",
        cdp_port=9227,
        programmatic_selection_enabled=programmatic_selection_enabled,
    )


def test_polarium_cdp_trade_url_defaults_to_traderoom() -> None:
    assert Settings(_env_file=None).polarium_trade_url == "https://trade.polariumbroker.com/traderoom"


def test_cdp_live_source_routes_candles_generated_to_shared_candle_store() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config())

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(999)))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(999)))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message()))

    assert len(store.series(active_id=76, raw_size=60)) == 1
    assert len(store.series(active_id=76, raw_size=300)) == 1
    assert len(store.series(active_id=76, raw_size=900)) == 1
    assert runtime.status().connected is True
    assert runtime.status().market_socket_ready is True
    assert source.status().connected is True
    assert store.series(active_id=76, raw_size=60)[0].close == 1.1010


def test_cdp_live_source_drops_forbidden_inbound_without_storing_payload() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config())

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "portfolio.position-changed", "msg": {"body": {"secret": "redacted"}}}))

    assert store.series_keys() == ()
    assert runtime.status().forbidden == 1
    assert source.status().last_error_code == "FORBIDDEN_INBOUND_DROPPED"


def test_cdp_live_source_sends_active_bootstrap_for_visible_context_on_market_socket() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(999)))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(999)))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))
    source.observe_cdp_event(cdp_frame_sent(page_native_subscribe_candle(76, 60)))

    asyncio.run(source._maybe_send_bootstrap(cdp))

    assert len(cdp.payloads) == 1
    payload = cdp.payloads[0]
    assert payload["name"] == "sendMessage"
    assert payload["msg"] == {"name": "get-first-candles", "body": {"active_id": 76, "size": 60}}
    assert payload["request_id"].startswith("friday_get_first_candles_76_60_")
    bootstrap = runtime.status().sanitized()["bootstrap"]
    assert bootstrap["request_sent"] is True
    assert bootstrap["request_id_present"] is True


def test_cdp_live_source_does_not_duplicate_when_page_already_sent_bootstrap() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()
    native = {
        "name": "sendMessage",
        "request_id": "native-1",
        "msg": {"name": "get-first-candles", "body": {"active_id": 76, "size": 60}},
    }

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))
    source.observe_cdp_event(cdp_frame_sent(native))

    asyncio.run(source._maybe_send_bootstrap(cdp))

    assert cdp.payloads == []


def test_non_market_page_bootstrap_does_not_block_visible_market_bootstrap() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()
    native = {
        "name": "sendMessage",
        "request_id": "native-other-socket",
        "msg": {"name": "get-first-candles", "body": {"active_id": 2298, "size": 300}},
    }

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))
    asyncio.run(source._handle_cdp_event(cdp, cdp_frame_sent_on("ws-ui", native)))

    assert runtime.status().sanitized()["session_context"]["active_id"] == 2298
    assert runtime.status().sanitized()["session_context"]["raw_size"] == 300
    assert len(cdp.payloads) == 1
    payload = cdp.payloads[0]
    assert payload["name"] == "sendMessage"
    assert payload["msg"] == {"name": "get-first-candles", "body": {"active_id": 2298, "size": 300}}
    assert payload["request_id"].startswith("friday_get_first_candles_2298_300_")


def test_visible_usdbrl_m5_auto_bootstrap_creates_own_polarium_bucket() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config(programmatic_selection_enabled=False), candle_store=store)
    cdp = _FakeCDP()

    def on_payload(payload: dict) -> None:
        if payload.get("name") != "sendMessage":
            return
        source.observe_cdp_event(
            cdp_frame_received(history_message("first-candles", 2298, 300, payload["request_id"], count=50, start=1_783_720_200))
        )

    cdp.on_payload = on_payload
    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))
    source.observe_cdp_event(cdp_frame_sent(page_native_subscribe_candle(76, 60)))
    asyncio.run(source._maybe_send_bootstrap(cdp))
    source.observe_cdp_event(cdp_frame_sent_on("ws-ui", {"name": "sendMessage", "request_id": "ui-usdbrl-m5", "msg": {"name": "get-first-candles", "body": {"active_id": 2298, "size": 300}}}))
    asyncio.run(source._maybe_send_bootstrap(cdp))

    context = runtime.status().sanitized()["session_context"]
    assert source._config.programmatic_selection_enabled is False
    assert all(not payload["request_id"].startswith("friday_native_") for payload in cdp.payloads)
    assert len(store.series(active_id=2298, raw_size=300)) == 50
    assert len(store.series(active_id=76, raw_size=300)) <= 1
    assert context["active_id"] == 2298
    assert context["raw_size"] == 300
    assert context["history_count"] == 50
    assert context["history_state"] == "READY"


def test_live_bootstrap_request_report_records_socket_send_response_store_and_ready(tmp_path: Path) -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    diagnostic = LiveBootstrapRequestDiagnostic(
        report_json=tmp_path / "live_bootstrap_request_report.json",
        report_txt=tmp_path / "live_bootstrap_request_report.txt",
    )
    source = PolariumCDPLiveSource(runtime, disabled_config(programmatic_selection_enabled=False), candle_store=store, live_bootstrap_diagnostic=diagnostic)
    cdp = _FakeCDP()

    def on_payload(payload: dict) -> None:
        if payload.get("name") != "sendMessage":
            return
        source.observe_cdp_event(
            cdp_frame_received(history_message("first-candles", 2298, 300, payload["request_id"], count=50, start=1_783_720_200))
        )

    cdp.on_payload = on_payload
    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))
    source.observe_cdp_event(cdp_frame_sent_on("ws-ui", {"name": "sendMessage", "request_id": "ui-usdbrl-m5", "msg": {"name": "get-first-candles", "body": {"active_id": 2298, "size": 300}}}))
    asyncio.run(source._maybe_send_bootstrap(cdp))

    report = json.loads((tmp_path / "live_bootstrap_request_report.json").read_text(encoding="utf-8"))
    record = next(item for item in report["records"] if item["active_id"] == 2298 and item["raw_size"] == 300)

    assert (tmp_path / "live_bootstrap_request_report.txt").exists()
    assert record["visible_context_observed"] is True
    assert record["owner_selected"] == "AUTO_VISIBLE_CONTEXT"
    assert record["request_created"] is True
    assert record["pending_registered"] is True
    assert record["socket_request_id"] == "ws-1"
    assert record["market_socket_match"] is True
    assert record["send_attempted"] is True
    assert record["send_succeeded"] is True
    assert record["response_received"] is True
    assert record["response_type"] == "first-candles"
    assert record["correlation_result"] == "matched"
    assert record["parser_count"] == 50
    assert record["store_key"] == "POLARIUM:2298:300"
    assert record["store_written"] is True
    assert record["history_count"] == 50
    assert record["readiness"] == "READY"
    assert record["failure_stage"] == "SUCCESS"


def test_cdp_live_source_sends_new_bootstrap_when_visible_timeframe_changes_to_m5_and_m15() -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))
    source.observe_cdp_event(cdp_frame_sent(page_native_subscribe_candle(76, 60)))
    asyncio.run(source._maybe_send_bootstrap(cdp))
    source.observe_cdp_event(cdp_frame_received({"name": "first-candles", "request_id": cdp.payloads[-1]["request_id"], "msg": {"candles_by_size": {"60": {"from": 1_783_720_000, "to": 1_783_720_060, "open": 1.1, "close": 1.1, "min": 1.0, "max": 1.2}}}}))

    source.observe_cdp_event(cdp_frame_sent(page_native_subscribe_candle(76, 300)))
    asyncio.run(source._maybe_send_bootstrap(cdp))
    source.observe_cdp_event(cdp_frame_sent(page_native_subscribe_candle(76, 900)))
    asyncio.run(source._maybe_send_bootstrap(cdp))

    assert [payload["msg"]["body"]["size"] for payload in cdp.payloads] == [60, 300, 900]
    assert len({payload["request_id"] for payload in cdp.payloads}) == 3


def test_cdp_live_source_opens_friday_second_tab_after_market_session_is_ready(monkeypatch) -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()

    monkeypatch.setattr(live_source, "_list_cdp_targets", lambda port: (CDPTarget("polarium-1", "https://trade.polariumbroker.com/traderoom"),))
    monkeypatch.setattr(live_source, "_url_available", lambda url: True)
    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))

    asyncio.run(source._maybe_open_friday_tab(cdp))
    asyncio.run(source._maybe_open_friday_tab(cdp))

    assert cdp.created_targets == ["http://127.0.0.1:5173"]


def test_cdp_live_source_does_not_open_friday_when_frontend_is_unavailable(monkeypatch) -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()

    monkeypatch.setattr(live_source, "_list_cdp_targets", lambda port: (CDPTarget("polarium-1", "https://trade.polariumbroker.com/traderoom"),))
    monkeypatch.setattr(live_source, "_url_available", lambda url: False)
    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))

    asyncio.run(source._maybe_open_friday_tab(cdp))

    assert cdp.created_targets == []


def test_cdp_live_source_opens_friday_even_when_cdp_events_keep_arriving(monkeypatch) -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()

    monkeypatch.setattr(live_source, "_list_cdp_targets", lambda port: (CDPTarget("polarium-1", "https://trade.polariumbroker.com/traderoom"),))
    monkeypatch.setattr(live_source, "_url_available", lambda url: True)

    asyncio.run(source._process_cdp_tick(cdp, cdp_socket_created()))

    assert cdp.created_targets == ["http://127.0.0.1:5173"]


def test_cdp_live_source_does_not_mark_friday_open_when_create_target_returns_none(monkeypatch) -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()
    cdp.target_id = None

    monkeypatch.setattr(live_source, "_list_cdp_targets", lambda port: (CDPTarget("polarium-1", "https://trade.polariumbroker.com/traderoom"),))
    monkeypatch.setattr(live_source, "_url_available", lambda url: True)

    asyncio.run(source._maybe_open_friday_tab(cdp))

    assert cdp.created_targets == ["http://127.0.0.1:5173"]
    assert source._last_error_code == "TARGET_CREATE_FAILED"
    assert source._dual_tab._opened_or_reused is False


def test_cdp_live_source_records_target_create_failure_without_crashing(monkeypatch) -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()
    cdp.raise_on_create = True

    monkeypatch.setattr(live_source, "_list_cdp_targets", lambda port: (CDPTarget("polarium-1", "https://trade.polariumbroker.com/traderoom"),))
    monkeypatch.setattr(live_source, "_url_available", lambda url: True)

    asyncio.run(source._maybe_open_friday_tab(cdp))

    assert source._last_error_code == "RUNTIMEERROR"
    assert source._dual_tab._opened_or_reused is False


def test_cdp_tick_type_error_is_recorded_without_killing_live_source(monkeypatch) -> None:
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config())
    cdp = _FakeCDP()
    calls = {"count": 0}

    async def flaky_handle(_cdp, _event):
        calls["count"] += 1
        if calls["count"] == 1:
            raise TypeError("unexpected cdp frame shape")

    monkeypatch.setattr(source, "_handle_cdp_event", flaky_handle)
    monkeypatch.setattr(source, "_maybe_open_friday_tab", lambda _cdp: _async_none())

    asyncio.run(source._process_cdp_tick(cdp, {"method": "Network.webSocketFrameReceived"}))
    asyncio.run(source._process_cdp_tick(cdp, {"method": "Network.webSocketFrameReceived"}))

    assert source._last_error_code == "TYPEERROR"
    assert calls["count"] == 2


def test_programmatic_market_selection_sends_subscribe_bootstrap_and_updates_context() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config(programmatic_selection_enabled=True), candle_store=store)
    cdp = _FakeCDP()
    cdp.on_payload = lambda payload: source.observe_cdp_event(cdp_frame_received(first_candles_message(76, 300, payload["request_id"]))) if payload.get("name") == "sendMessage" else None
    source._cdp = cdp

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(999)))

    result = asyncio.run(source.select_market(active_id=76, raw_size=300, timeout_seconds=0.2))

    assert result.accepted is True
    assert result.subscribe_sent is True
    assert result.bootstrap_sent is True
    assert result.bootstrap_ready is True
    assert result.chart_count == 50
    assert result.session_context["active_id"] == 76
    assert result.session_context["raw_size"] == 300
    assert [payload["name"] for payload in cdp.payloads] == ["subscribeMessage", "sendMessage", "sendMessage", "sendMessage", "sendMessage", "sendMessage"]
    assert cdp.payloads[0]["msg"]["name"] == "candles-generated"
    assert cdp.payloads[1]["msg"]["name"] == "get-first-candles"
    assert cdp.payloads[2]["msg"]["name"] == "get-first-candles"
    assert [payload["msg"]["name"] for payload in cdp.payloads[3:]] == ["get-candles", "get-candles", "get-candles"]
    assert all(not str(payload.get("request_id", "")).startswith("friday_get_first_candles_") for payload in cdp.payloads)
    assert any(str(payload.get("request_id", "")).startswith("friday_native_get_first_candles_") for payload in cdp.payloads)


def test_programmatic_market_selection_temporarily_suppresses_auto_bootstrap_for_same_context(tmp_path: Path) -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    envelope = GetCandlesEnvelopeDiagnostic(
        report_json=tmp_path / "get_candles_envelope_report.json",
        report_txt=tmp_path / "get_candles_envelope_report.txt",
    )
    source = PolariumCDPLiveSource(runtime, disabled_config(programmatic_selection_enabled=True), candle_store=store, get_candles_envelope=envelope)
    cdp = _FakeCDP()
    source._cdp = cdp

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(76)))
    source.observe_cdp_event(cdp_frame_sent(page_native_subscribe_candle(76, 300)))
    source._programmatic_bootstrap_contexts.add((76, 300))

    asyncio.run(source._maybe_send_bootstrap(cdp))

    assert cdp.payloads == []
    source._programmatic_bootstrap_contexts.discard((76, 300))
    asyncio.run(source._maybe_send_bootstrap(cdp))
    assert len(cdp.payloads) == 1
    assert cdp.payloads[0]["request_id"].startswith("friday_get_first_candles_76_300_")


def test_programmatic_market_selection_first_candles_unitary_is_not_bootstrap_ready() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config(programmatic_selection_enabled=True), candle_store=store)
    cdp = _FakeCDP()
    cdp.on_payload = (
        lambda payload: source.observe_cdp_event(
            cdp_frame_received(history_message("first-candles", 2298, 300, payload["request_id"], count=1))
        )
        if payload.get("name") == "sendMessage"
        else None
    )
    source._cdp = cdp

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(999)))

    result = asyncio.run(source.select_market(active_id=2298, raw_size=300, timeout_seconds=0.2))

    assert result.accepted is True
    assert result.subscribe_sent is True
    assert result.bootstrap_sent is True
    assert result.chart_count == 1
    assert result.bootstrap_ready is False
    assert result.error_code == "BOOTSTRAP_WAIT_TIMEOUT"
    assert result.session_context["history_state"] == "LIMITED"
    assert result.session_context["history_count"] == 1
    assert result.session_context["history_required"] == 50


def test_programmatic_market_selection_becomes_ready_only_after_historical_candles_lot() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config(programmatic_selection_enabled=True), candle_store=store)
    cdp = _FakeCDP()

    def on_payload(payload: dict) -> None:
        if payload.get("name") != "sendMessage":
            return
        source.observe_cdp_event(cdp_frame_received(history_message("first-candles", 2298, 300, payload["request_id"], count=1)))
        source.observe_cdp_event(cdp_frame_received(history_message("candles", 2298, 300, payload["request_id"], count=50, start=1_783_720_300)))

    cdp.on_payload = on_payload
    source._cdp = cdp

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(999)))

    result = asyncio.run(source.select_market(active_id=2298, raw_size=300, timeout_seconds=0.2))

    assert result.accepted is True
    assert result.bootstrap_ready is True
    assert result.chart_count == 51
    assert result.session_context["history_state"] == "READY"
    assert result.session_context["history_count"] == 51


def test_programmatic_market_selection_supports_m1_m5_m15() -> None:
    store = CandleStore()
    runtime = PolariumMarketFeedRuntime(store)
    source = PolariumCDPLiveSource(runtime, disabled_config(programmatic_selection_enabled=True), candle_store=store)
    cdp = _FakeCDP()
    cdp.on_payload = lambda payload: source.observe_cdp_event(
        cdp_frame_received(first_candles_message(payload["msg"]["body"]["active_id"], payload["msg"]["body"]["size"], payload["request_id"]))
    ) if payload.get("name") == "sendMessage" else None
    source._cdp = cdp

    source.observe_cdp_event(cdp_socket_created())
    source.observe_cdp_event(cdp_frame_received({"name": "authenticated"}))
    source.observe_cdp_event(cdp_frame_received({"name": "timeSync"}))
    source.observe_cdp_event(cdp_frame_received(candles_generated_message(999)))

    for raw_size in (60, 300, 900):
        result = asyncio.run(source.select_market(active_id=76, raw_size=raw_size, timeout_seconds=0.2))
        assert result.bootstrap_ready is True
        assert result.session_context["raw_size"] == raw_size
        assert len(store.series(active_id=76, raw_size=raw_size)) == 50


def test_programmatic_market_selection_rejects_without_market_socket() -> None:
    source = PolariumCDPLiveSource(PolariumMarketFeedRuntime(CandleStore()), disabled_config(programmatic_selection_enabled=True), candle_store=CandleStore())

    result = asyncio.run(source.select_market(active_id=76, raw_size=300, timeout_seconds=0.01))

    assert result.accepted is False
    assert result.error_code == "MARKET_SOCKET_NOT_READY"


def test_cdp_market_socket_send_parses_runtime_evaluate_nested_success() -> None:
    cdp = live_source._CDPClient("ws://cdp")
    captured = {}

    async def fake_call(method: str, params: dict | None = None):
        captured["method"] = method
        captured["params"] = params or {}
        return {
            "result": {
                "type": "object",
                "value": {
                    "sent": True,
                    "error_code": None,
                    "socket_count": 1,
                    "open_socket_count": 1,
                    "selected_ready_state": 1,
                },
            }
        }

    cdp.call = fake_call

    result = asyncio.run(cdp.send_market_websocket_payload({"name": "subscribeMessage", "msg": {"name": "candles-generated"}}))

    assert captured["method"] == "Runtime.evaluate"
    assert "Runtime.evaluate" not in captured["params"]["expression"]
    assert result.sent is True
    assert result.error_code is None
    assert result.socket_count == 1
    assert result.open_socket_count == 1
    assert result.selected_ready_state == 1


def test_cdp_market_socket_send_reports_reference_missing_not_generic_failure() -> None:
    cdp = live_source._CDPClient("ws://cdp")

    async def fake_call(method: str, params: dict | None = None):
        return {"result": {"type": "object", "value": {"sent": False, "error_code": "MARKET_SOCKET_REFERENCE_MISSING", "socket_count": 0, "open_socket_count": 0}}}

    cdp.call = fake_call

    result = asyncio.run(cdp.send_market_websocket_payload({"name": "subscribeMessage"}))

    assert result.sent is False
    assert result.error_code == "MARKET_SOCKET_REFERENCE_MISSING"
    assert result.socket_count == 0


def test_cdp_market_socket_send_reports_socket_not_open() -> None:
    cdp = live_source._CDPClient("ws://cdp")

    async def fake_call(method: str, params: dict | None = None):
        return {"result": {"type": "object", "value": {"sent": False, "error_code": "MARKET_SOCKET_NOT_OPEN", "socket_count": 1, "open_socket_count": 0, "selected_ready_state": 3}}}

    cdp.call = fake_call

    result = asyncio.run(cdp.send_market_websocket_payload({"name": "subscribeMessage"}))

    assert result.sent is False
    assert result.error_code == "MARKET_SOCKET_NOT_OPEN"
    assert result.selected_ready_state == 3


def test_cdp_market_socket_send_reports_runtime_evaluate_exception() -> None:
    cdp = live_source._CDPClient("ws://cdp")

    async def fake_call(method: str, params: dict | None = None):
        raise RuntimeError("CDP_CALL_FAILED")

    cdp.call = fake_call

    result = asyncio.run(cdp.send_market_websocket_payload({"name": "subscribeMessage"}))

    assert result.sent is False
    assert result.error_code == "RUNTIME_EVALUATE_FAILED"


def test_wait_for_page_target_uses_polarium_page_not_first_page(monkeypatch) -> None:
    class _FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return json.dumps(
                [
                    {
                        "type": "page",
                        "url": "http://127.0.0.1:5173/market-chart",
                        "webSocketDebuggerUrl": "ws://friday",
                    },
                    {
                        "type": "service_worker",
                        "url": "https://trade.polariumbroker.com/worker.js",
                        "webSocketDebuggerUrl": "ws://worker",
                    },
                    {
                        "type": "page",
                        "url": "https://trade.polariumbroker.com/traderoom",
                        "webSocketDebuggerUrl": "ws://polarium",
                    },
                ]
            ).encode("utf-8")

    monkeypatch.setattr(live_source.urllib.request, "urlopen", lambda *_args, **_kwargs: _FakeResponse())

    target = live_source._wait_for_page_target(9227, "trade.polariumbroker.com")

    assert target == "ws://polarium"


def test_cdp_live_source_stop_clears_programmatic_transient_state() -> None:
    source = PolariumCDPLiveSource(PolariumMarketFeedRuntime(CandleStore()), disabled_config(programmatic_selection_enabled=True), candle_store=CandleStore())
    source._programmatic_bootstrap_contexts.add((76, 300))
    source._programmatic_outbound_signatures.append(("sendMessage", "get-first-candles", 76, 300))

    asyncio.run(source.stop())

    assert source._programmatic_bootstrap_contexts == set()
    assert source._programmatic_outbound_signatures == []


def test_programmatic_outbound_echo_is_not_recorded_as_page_native(tmp_path: Path) -> None:
    diag = HistoricalRequestSequenceDiagnostic(
        report_json=tmp_path / "historical_request_sequence.json",
        report_txt=tmp_path / "historical_request_sequence.txt",
    )
    runtime = PolariumMarketFeedRuntime(CandleStore())
    source = PolariumCDPLiveSource(runtime, disabled_config(), historical_request_sequence=diag)
    cdp = _FakeCDP()
    payload = {"name": "sendMessage", "request_id": "friday-1", "msg": {"name": "get-first-candles", "body": {"active_id": 76, "size": 300}}}

    asyncio.run(source._send_programmatic_payload(cdp, payload, now_ms=1_000))
    source.observe_cdp_event(cdp_frame_sent(payload))

    report = json.loads((tmp_path / "historical_request_sequence.json").read_text(encoding="utf-8"))
    assert report["summary"]["manual_count"] == 0
    assert report["summary"]["programmatic_count"] == 1
    assert report["programmatic_flow"][0]["request_id"] == "friday-1"


def test_programmatic_market_selection_is_disabled_by_default() -> None:
    source = PolariumCDPLiveSource(PolariumMarketFeedRuntime(CandleStore()), disabled_config(), candle_store=CandleStore())

    result = asyncio.run(source.select_market(active_id=76, raw_size=300, timeout_seconds=0.01))

    assert result.accepted is False
    assert result.error_code == "PROGRAMMATIC_SELECTION_DISABLED"


def test_dev_select_market_endpoint_uses_exact_path_when_explicitly_enabled(monkeypatch) -> None:
    class _FakeSource:
        async def select_market(self, *, active_id: int, raw_size: int):
            return ProgrammaticMarketSelectionResult(
                accepted=True,
                active_id=active_id,
                raw_size=raw_size,
                subscribe_sent=True,
                bootstrap_sent=True,
                bootstrap_ready=True,
                chart_count=50,
                session_context={"active_id": active_id, "raw_size": raw_size},
            )

    monkeypatch.setattr(dev_market_selection, "polarium_cdp_live_source", _FakeSource())
    monkeypatch.setattr(dev_market_selection.settings, "polarium_programmatic_selection_enabled", True)

    response = TestClient(app).post("/api/dev/select-market", json={"active_id": 76, "raw_size": 300})

    assert response.status_code == 200
    assert response.json()["active_id"] == 76
    assert response.json()["raw_size"] == 300
    assert response.json()["source"] == "POLARIUM_CDP_PROGRAMMATIC_SELECTION"


def test_dev_select_market_endpoint_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.setattr(dev_market_selection.settings, "polarium_programmatic_selection_enabled", False)

    response = TestClient(app).post("/api/dev/select-market", json={"active_id": 76, "raw_size": 300})

    assert response.status_code == 403
    assert response.json()["detail"]["error_code"] == "PROGRAMMATIC_SELECTION_DISABLED"


def test_dev_select_market_endpoint_rejects_unsupported_raw_size(monkeypatch) -> None:
    monkeypatch.setattr(dev_market_selection.settings, "polarium_programmatic_selection_enabled", True)

    response = TestClient(app).post("/api/dev/select-market", json={"active_id": 76, "raw_size": 120})

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "UNSUPPORTED_RAW_SIZE"


class _FakeCDP:
    def __init__(self) -> None:
        self.payloads: list[dict] = []
        self.created_targets: list[str] = []
        self.on_payload = None
        self.target_id: str | None = "created-friday"
        self.raise_on_create = False

    async def send_market_websocket_payload(self, payload: dict) -> MarketSocketSendResult:
        self.payloads.append(payload)
        if self.on_payload is not None:
            asyncio.get_running_loop().call_soon(self.on_payload, payload)
        return MarketSocketSendResult(sent=True, socket_count=1, open_socket_count=1, selected_ready_state=1)

    async def create_target(self, url: str) -> str | None:
        if self.raise_on_create:
            raise RuntimeError("create target failed")
        self.created_targets.append(url)
        return self.target_id


async def _async_none() -> None:
    return None
