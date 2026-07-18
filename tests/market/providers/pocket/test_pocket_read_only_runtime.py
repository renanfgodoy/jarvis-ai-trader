from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.market.providers.pocket.cdp_client import PocketLocalCDPClient
from app.market.providers.pocket.candle_store_adapter import PocketCandleStoreAdapter
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.cdp_models import PocketCDPEvent, PocketCDPTarget
from app.market.providers.pocket.cdp_observation_transport import PocketCDPObservationTransport
from app.market.providers.pocket.diagnostics import write_live_observation_reports, write_real_validation_report
from app.market.providers.pocket.errors import POCKET_LIVE_CONNECTION_DISABLED, POCKET_READ_ONLY_GUARD_BLOCKED, PocketRuntimeError
from app.market.providers.pocket.fake_transport import FakePocketTransport
from app.market.providers.pocket.fake_cdp_client import FakePocketCDPClient
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.models import PocketDomainEvent
from app.market.providers.pocket.readiness import PocketReadinessTracker
from app.market.providers.pocket.realtime_candle_builder import PocketRealtimeCandleBuilder
from app.market.providers.pocket.replay_transport import PocketReplayTransport
from app.market.providers.pocket.runtime import PocketMarketRuntime
from app.market.providers.pocket.runtime_guard import ALLOWED_ACTIONS, BLOCKED_ACTIONS, PocketRuntimeGuard
from app.market.providers.pocket.target_manager import PocketTargetManager
from tools.pocket_live_observation import __main__ as pocket_live_cli
from tools.pocket_live_observation.orchestrator import (
    POCKET_CHROME_EXECUTABLE_NOT_FOUND,
    POCKET_UNSAFE_OBSERVATION_CONFIGURATION,
    build_chrome_command,
    config_from_env,
    resolve_pocket_observation_mode,
    start_chrome,
)
from tools.pocket_parser.asset_parser import parse_change_symbol, parse_update_assets
from tools.pocket_parser.history_parser import parse_history_batch
from tools.pocket_parser.models import PocketRealtimeTick

PRIVATE_HARS = (
    Path(".jarvis_private/pocket_hars/pocketoption.com.har"),
    Path(".jarvis_private/pocket_hars/pocketoption.com(1).har"),
)


def test_default_config_is_safe_and_disabled() -> None:
    config = PocketProviderConfig()

    assert config.pocket_provider_enabled is False
    assert config.pocket_live_connection_enabled is False
    assert config.pocket_read_only is True
    assert config.pocket_real_observation_authorized is False
    assert config.pocket_history_required == 50


def test_pocket_observation_mode_matrix_defaults_to_fake() -> None:
    assert resolve_pocket_observation_mode(PocketProviderConfig()).mode == "FAKE_CDP_ONLY"
    assert resolve_pocket_observation_mode(PocketProviderConfig(pocket_cdp_enabled=True)).mode == "FAKE_CDP_ONLY"
    assert resolve_pocket_observation_mode(PocketProviderConfig(pocket_cdp_enabled=True, pocket_real_observation_authorized=True)).mode == "REAL_PASSIVE_CDP"


@pytest.mark.parametrize(
    "config",
    [
        PocketProviderConfig(pocket_cdp_enabled=True, pocket_real_observation_authorized=True, pocket_live_connection_enabled=True),
        PocketProviderConfig(pocket_cdp_enabled=True, pocket_real_observation_authorized=True, pocket_read_only=False),
        PocketProviderConfig(pocket_cdp_enabled=True, pocket_real_observation_authorized=True, pocket_cdp_observation_only=False),
    ],
)
def test_pocket_observation_mode_blocks_unsafe_configuration(config: PocketProviderConfig) -> None:
    decision = resolve_pocket_observation_mode(config)

    assert decision.mode == "BLOCKED_UNSAFE_CONFIGURATION"
    assert decision.error_code == POCKET_UNSAFE_OBSERVATION_CONFIGURATION


def test_pocket_observation_config_from_env_requires_explicit_authorization() -> None:
    config = config_from_env(
        {
            "POCKET_CDP_ENABLED": "true",
            "POCKET_CDP_OBSERVATION_ONLY": "true",
            "POCKET_READ_ONLY": "true",
            "POCKET_LIVE_CONNECTION_ENABLED": "false",
        }
    )

    assert config.pocket_real_observation_authorized is False
    assert resolve_pocket_observation_mode(config).mode == "FAKE_CDP_ONLY"


def test_pocket_observation_config_from_env_enables_real_mode_only_when_safe() -> None:
    config = config_from_env(
        {
            "POCKET_CDP_ENABLED": "true",
            "POCKET_CDP_OBSERVATION_ONLY": "true",
            "POCKET_READ_ONLY": "true",
            "POCKET_LIVE_CONNECTION_ENABLED": "false",
            "POCKET_REAL_OBSERVATION_AUTHORIZED": "true",
        }
    )

    assert resolve_pocket_observation_mode(config).mode == "REAL_PASSIVE_CDP"


def test_chrome_command_contains_dedicated_port_private_profile_and_url() -> None:
    config = PocketProviderConfig(pocket_cdp_debug_port=9230, pocket_cdp_profile_dir=".jarvis_private/chrome-pocket-profile", pocket_trade_url="https://pocketoption.com/")

    command = build_chrome_command(config, executable="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

    assert command[0].endswith("Google Chrome")
    assert "--remote-debugging-port=9230" in command
    assert "--user-data-dir=.jarvis_private/chrome-pocket-profile" in command
    assert "https://pocketoption.com/" in command
    assert all("@" not in part for part in command)


def test_chrome_launcher_reports_missing_executable() -> None:
    with pytest.raises(PocketRuntimeError) as error:
        start_chrome(PocketProviderConfig(), executable="/missing/google-chrome")

    assert error.value.code == POCKET_CHROME_EXECUTABLE_NOT_FOUND


def test_cli_fake_mode_remains_default(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("POCKET_REAL_OBSERVATION_AUTHORIZED", raising=False)

    pocket_live_cli.main()

    output = capsys.readouterr().out
    assert "Modo: FAKE_CDP_ONLY" in output
    assert "market_socket_found: True" in output


def test_cli_real_mode_delegates_to_real_orchestrator(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    called: dict[str, bool] = {}

    def fake_real_runner(config: PocketProviderConfig) -> dict:
        called["real"] = config.pocket_real_observation_authorized
        return {
            "target_found": False,
            "market_socket_found": False,
            "history_batches": 0,
            "historical_candles": 0,
            "stream_events": 0,
            "ticks": 0,
            "observer_stopped_cleanly": True,
        }

    monkeypatch.setenv("POCKET_CDP_ENABLED", "true")
    monkeypatch.setenv("POCKET_CDP_OBSERVATION_ONLY", "true")
    monkeypatch.setenv("POCKET_READ_ONLY", "true")
    monkeypatch.setenv("POCKET_LIVE_CONNECTION_ENABLED", "false")
    monkeypatch.setenv("POCKET_REAL_OBSERVATION_AUTHORIZED", "true")
    monkeypatch.setattr(pocket_live_cli, "run_real_passive_observation", fake_real_runner)

    pocket_live_cli.main()

    output = capsys.readouterr().out
    assert called["real"] is True
    assert "Modo: FAKE_CDP_ONLY" not in output


def test_fake_transport_start_stop_next_event_and_empty() -> None:
    transport = FakePocketTransport([PocketDomainEvent("auth/success")])

    assert transport.next_event() is None
    transport.start()
    assert transport.is_running() is True
    assert transport.next_event().event_type == "auth/success"  # type: ignore[union-attr]
    assert transport.next_event() is None
    transport.stop()
    assert transport.is_running() is False


def test_guard_allows_read_only_and_blocks_forbidden_actions() -> None:
    guard = PocketRuntimeGuard()

    for action in ALLOWED_ACTIONS:
        guard.ensure_allowed(action)
    for action in BLOCKED_ACTIONS:
        with pytest.raises(PocketRuntimeError) as error:
            guard.ensure_allowed(action)
        assert error.value.code == POCKET_READ_ONLY_GUARD_BLOCKED


def test_runtime_blocks_live_connection() -> None:
    runtime = PocketMarketRuntime()

    with pytest.raises(PocketRuntimeError) as error:
        runtime.start(live_connection=True)

    assert error.value.code == POCKET_LIVE_CONNECTION_DISABLED
    assert runtime.last_error == POCKET_LIVE_CONNECTION_DISABLED


def test_runtime_processes_asset_history_tick_chart_and_unknown_event() -> None:
    runtime = PocketMarketRuntime(config=PocketProviderConfig(pocket_history_required=2, preserve_store_on_stop=True))
    runtime.start()
    changed = parse_change_symbol({"asset": "EURUSD_otc", "period": 300})
    batch, rejections = parse_history_batch(
        {
            "asset": "EURUSD_otc",
            "period": 300,
            "history": [[1700000000.1, 1.0]],
            "candles": [[1700000000, 1.0, 1.1, 1.2, 0.9, 10], [1700000300, 1.1, 1.2, 1.3, 1.0, 11]],
        },
        source_har="fixture.har",
        session_index=1,
        frame_index=1,
    )
    assert batch is not None
    assert rejections == []

    runtime.process(PocketDomainEvent("updateAssets", tuple(parse_update_assets([[1, "#EURUSD_otc", "EUR/USD OTC", "currency", 3, 92, 60, 30, 3, 1, 0, 0, [], 1700000000, True, [{"time": 60}], 0]]))))
    runtime.process(PocketDomainEvent("changeSymbol", changed))
    runtime.process(PocketDomainEvent("updateHistoryNewFast", batch))
    runtime.process(PocketDomainEvent("updateStream", PocketRealtimeTick("EURUSD_otc", 1.21, 1700000360.0, "updateStream", 1, "fixture.har", 1)))
    runtime.process(PocketDomainEvent("updateCharts", {"symbol": "EURUSD_otc"}))
    runtime.process(PocketDomainEvent("mystery", {"safe": True}))

    status = runtime.status()
    assert status["metrics"]["history_batches"] == 1
    assert status["metrics"]["historical_candles_written"] == 2
    assert status["metrics"]["ticks_processed"] == 1
    assert status["metrics"]["realtime_candles_created"] == 1
    assert status["unknown_events"] == {"mystery": 1}
    assert status["current_context"]["history_state"] == "READY"
    assert status["current_context"]["analysis_blocked"] is False


def test_store_adapter_replaces_deduplicates_sorts_and_returns_last() -> None:
    store = PocketCandleStoreAdapter()
    batch, _ = parse_history_batch(
        {"asset": "AUDUSD_otc", "period": 60, "candles": [[100, 1.0, 1.1, 1.2, 0.9], [60, 0.9, 1.0, 1.1, 0.8], [60, 0.9, 1.0, 1.1, 0.8]]},
        source_har="fixture.har",
        session_index=1,
        frame_index=1,
    )

    assert batch is not None
    assert store.add_historical(batch.candles) == 2
    assert store.count("POCKET:AUDUSD_otc:60") == 2
    assert store.candles("POCKET:AUDUSD_otc:60")[0].timestamp == 60
    assert store.last("POCKET:AUDUSD_otc:60").timestamp == 100  # type: ignore[union-attr]


@pytest.mark.parametrize("period", [60, 300, 900])
def test_realtime_candle_builder_aggregates_ohlc_and_rolls_bucket(period: int) -> None:
    builder = PocketRealtimeCandleBuilder()

    first, first_status = builder.update(PocketRealtimeTick("EURUSD_otc", 1.0, 1200.0, "updateStream", 1, "fixture", 1), period)
    second, second_status = builder.update(PocketRealtimeTick("EURUSD_otc", 1.2, 1201.0, "updateStream", 2, "fixture", 1), period)

    assert first_status == "created"
    assert second_status == "updated"
    assert second.open == first.open
    assert second.high == 1.2
    assert second.low == 1.0
    assert second.close == 1.2
    assert second.volume == 2


def test_readiness_transitions() -> None:
    tracker = PocketReadinessTracker(history_required=3)
    key = "POCKET:EURUSD_otc:60"

    assert tracker.state_for(key) == "EMPTY"
    assert tracker.start_bootstrap(key) == "BOOTSTRAPPING"
    assert tracker.update_history(key, 1) == "LIMITED"
    assert tracker.update_history(key, 3) == "READY"
    assert tracker.mark_error(key) == "ERROR"


def test_live_source_routes_events_and_stop_cleans_transient_state() -> None:
    runtime = PocketMarketRuntime(config=PocketProviderConfig(pocket_history_required=1))
    source = PocketReadOnlyLiveSource(FakePocketTransport([PocketDomainEvent("auth/success"), PocketDomainEvent("unknown")]), runtime)

    source.start()
    assert source.events_routed == 2
    assert runtime.status()["metrics"]["events_received"] == 2
    source.stop()
    assert runtime.status()["connection_state"] == "STOPPED"
    assert runtime.store.list_buckets() == ()


@pytest.mark.skipif(not all(path.exists() for path in PRIVATE_HARS), reason="Private Pocket HARs are not available locally.")
def test_replay_transport_processes_two_hars_and_runtime_is_deterministic() -> None:
    def run_once() -> dict:
        runtime = PocketMarketRuntime(config=PocketProviderConfig(pocket_history_required=50, preserve_store_on_stop=True))
        source = PocketReadOnlyLiveSource(PocketReplayTransport(tuple(str(path) for path in PRIVATE_HARS)), runtime)
        source.start()
        return source.status()

    first = run_once()
    second = run_once()

    assert first["runtime"]["buckets"] == second["runtime"]["buckets"]
    assert len(first["runtime"]["buckets"]) == 7
    assert first["runtime"]["metrics"]["history_batches"] == 9
    assert first["runtime"]["metrics"]["historical_candles_written"] == 890
    assert first["runtime"]["metrics"]["ticks_processed"] == 419
    assert all(state in {"READY", "LIMITED"} for state in first["runtime"]["readiness"].values())


def test_pocket_provider_does_not_import_network_clients() -> None:
    banned_imports = {"socket", "websockets", "aiohttp", "requests", "httpx"}
    for path in Path("app/market/providers/pocket").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
                assert not imported & banned_imports, f"{path} imports {imported & banned_imports}"
            if isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in banned_imports, f"{path} imports {node.module}"


def test_target_manager_selects_pocket_page_and_ignores_other_targets() -> None:
    manager = PocketTargetManager()
    target = manager.select_target(
        (
            PocketCDPTarget("friday", "page", "http://127.0.0.1:5173/market-chart"),
            PocketCDPTarget("polarium", "page", "https://trade.polariumbroker.com/traderoom"),
            PocketCDPTarget("iframe", "iframe", "https://pocketoption.com/iframe"),
            PocketCDPTarget("worker", "service_worker", "https://pocketoption.com/sw.js"),
            PocketCDPTarget("pocket", "page", "https://pocketoption.com/cabinet/demo-quick-high-low/"),
        )
    )

    assert target is not None
    assert target.target_id == "pocket"


def test_target_manager_prefers_configured_trade_path_when_multiple_pocket_tabs_exist() -> None:
    manager = PocketTargetManager("https://pocketoption.com/pt/cabinet/demo-quick-high-low/")

    target = manager.select_target(
        (
            PocketCDPTarget("cabinet", "page", "https://pocketoption.com/pt/cabinet/"),
            PocketCDPTarget("trade", "page", "https://pocketoption.com/pt/cabinet/demo-quick-high-low/"),
        )
    )

    assert target is not None
    assert target.target_id == "trade"


def test_cdp_observer_confirms_market_socket_by_events_and_routes_history_and_ticks() -> None:
    client = FakePocketCDPClient(targets=_cdp_targets(), events=_cdp_events())
    runtime = PocketMarketRuntime(config=PocketProviderConfig(pocket_history_required=2, preserve_store_on_stop=True))
    transport = PocketCDPObservationTransport(client)
    source = PocketReadOnlyLiveSource(transport, runtime)

    source.start()

    status = source.status()
    assert status["transport"]["market_socket_found"] is True
    assert runtime.store.count("POCKET:EURUSD_otc:60") >= 2
    assert runtime.status()["metrics"]["ticks_processed"] == 1
    assert runtime.status()["current_context"]["asset"] == "EURUSD_otc"
    assert runtime.status()["current_context"]["period"] == 60
    assert transport.sockets["market"].classification == "MARKET_SOCKET"
    assert transport.sockets["aux"].classification != "MARKET_SOCKET"


def test_cdp_observer_discards_sensitive_market_payload_and_ignores_non_market_socket() -> None:
    events = (
        PocketCDPEvent("Network.webSocketCreated", {"requestId": "market", "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket"}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "market", "timestamp": 1, "response": {"payloadData": '42["auth",{"profile":"discard"}]'}}),
        PocketCDPEvent("Network.webSocketCreated", {"requestId": "aux", "url": "wss://events-po.com/socket.io/?EIO=4&transport=websocket"}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "aux", "timestamp": 2, "response": {"payloadData": '42["updateStream",[["EURUSD_otc",1700000000,1.1]]]'}}),
    )
    transport = PocketCDPObservationTransport(FakePocketCDPClient(targets=_cdp_targets(), events=events))

    transport.start()

    assert transport.sensitive_events_discarded == 1
    assert transport.non_market_frames_ignored == 1
    assert transport.next_event() is None


def test_cdp_observer_infers_market_socket_when_created_event_was_missed() -> None:
    events = (
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "late-market", "timestamp": 2, "response": {"payloadData": '42["updateHistoryNewFast",{"asset":"EURUSD_otc","period":60,"history":[],"candles":[[1700000000,1.0,1.1,1.2,0.9,10]]}]'}}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "late-market", "timestamp": 3, "response": {"payloadData": '42["updateStream",[["EURUSD_otc",1700000060.1,1.2]]]'}}),
    )
    runtime = PocketMarketRuntime(config=PocketProviderConfig(pocket_history_required=1, preserve_store_on_stop=True))
    source = PocketReadOnlyLiveSource(PocketCDPObservationTransport(FakePocketCDPClient(targets=_cdp_targets(), events=events)), runtime)

    source.start()

    status = source.status()
    assert status["transport"]["market_socket_found"] is True
    assert source.transport.sockets["late-market"].classification_reason == "MARKET_EVENT_WITHOUT_SOCKET_CREATED"
    assert runtime.store.count("POCKET:EURUSD_otc:60") >= 1
    assert runtime.status()["metrics"]["ticks_processed"] == 1


def test_cdp_observer_ignores_partial_context_and_publishes_atomic_context_only() -> None:
    events = (
        PocketCDPEvent("Network.webSocketCreated", {"requestId": "market", "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket"}),
        PocketCDPEvent("Network.webSocketFrameSent", {"requestId": "market", "timestamp": 1, "response": {"payloadData": '42["changeSymbol",{"asset":"EURUSD_otc"}]'}}),
        PocketCDPEvent("Network.webSocketFrameSent", {"requestId": "market", "timestamp": 2, "response": {"payloadData": '42["changeSymbol",{"asset":"EURUSD_otc","period":300}]'}}),
    )
    runtime = PocketMarketRuntime(config=PocketProviderConfig(preserve_store_on_stop=True))
    source = PocketReadOnlyLiveSource(PocketCDPObservationTransport(FakePocketCDPClient(targets=_cdp_targets(), events=events)), runtime)

    source.start()

    assert runtime.status()["current_context"]["asset"] == "EURUSD_otc"
    assert runtime.status()["current_context"]["period"] == 300
    assert source.transport.status()["market_socket_found"] is True


def test_cdp_observer_handles_binary_event_attachment_from_socketio_parser() -> None:
    transport = PocketCDPObservationTransport(
        FakePocketCDPClient(
            targets=_cdp_targets(),
            events=(
                PocketCDPEvent("Network.webSocketCreated", {"requestId": "market", "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket"}),
                PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "market", "timestamp": 1, "response": {"payloadData": '451-["updateStream",{"_placeholder":true,"num":0}]'}}),
                PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "market", "timestamp": 2, "response": {"payloadData": "W1siRVVSVVNEX290YyIsMTcwMDAwMDAwMCwxLjFdXQ=="}}),
            ),
        )
    )
    runtime = PocketMarketRuntime(config=PocketProviderConfig(preserve_store_on_stop=True))
    source = PocketReadOnlyLiveSource(transport, runtime)

    source.start()

    assert runtime.status()["metrics"]["ticks_processed"] == 1


def test_cdp_lifecycle_stop_closes_fake_client_and_reports_cleanly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.market.providers.pocket import diagnostics

    monkeypatch.setattr(diagnostics, "LIVE_OBSERVATION_JSON", tmp_path / "live.json")
    monkeypatch.setattr(diagnostics, "LIVE_OBSERVATION_TXT", tmp_path / "live.txt")
    monkeypatch.setattr(diagnostics, "SOCKET_OBSERVATION_JSON", tmp_path / "socket.json")
    monkeypatch.setattr(diagnostics, "SOCKET_OBSERVATION_TXT", tmp_path / "socket.txt")
    monkeypatch.setattr(diagnostics, "LIVE_CONTEXT_JSON", tmp_path / "context.json")
    monkeypatch.setattr(diagnostics, "LIVE_CONTEXT_TXT", tmp_path / "context.txt")
    client = FakePocketCDPClient(targets=_cdp_targets(), events=_cdp_events())
    runtime = PocketMarketRuntime(config=PocketProviderConfig(pocket_history_required=2, preserve_store_on_stop=True))
    source = PocketReadOnlyLiveSource(PocketCDPObservationTransport(client), runtime)

    source.start()
    source.stop()
    report = write_live_observation_reports(source)

    assert client.closed is True
    assert report["observer_stopped_cleanly"] is True
    assert (tmp_path / "live.json").exists()
    assert (tmp_path / "socket.json").exists()
    assert (tmp_path / "context.json").exists()


def test_real_validation_report_is_sanitized_and_records_zero_outbound(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.market.providers.pocket import diagnostics

    monkeypatch.setattr(diagnostics, "REAL_VALIDATION_JSON", tmp_path / "real.json")
    monkeypatch.setattr(diagnostics, "REAL_VALIDATION_TXT", tmp_path / "real.txt")
    runtime = PocketMarketRuntime(config=PocketProviderConfig(pocket_history_required=2, preserve_store_on_stop=True))
    source = PocketReadOnlyLiveSource(PocketCDPObservationTransport(FakePocketCDPClient(targets=_cdp_targets(), events=_cdp_events())), runtime)

    source.start()
    source.stop()
    report = write_real_validation_report(source, {"observation_mode": "REAL_PASSIVE_CDP"})

    assert report["observation_mode"] == "REAL_PASSIVE_CDP"
    assert report["market_socket_found"] is True
    assert report["history_batches"] == 1
    assert report["historical_candles"] == 2
    assert report["ticks"] == 1
    assert report["outbound_messages_originated_by_friday"] == 0
    assert (tmp_path / "real.json").exists()
    assert "authorization" not in (tmp_path / "real.txt").read_text(encoding="utf-8").lower()


def test_local_cdp_client_with_fake_local_cdp_wire_observes_network_events(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.market.providers.pocket.cdp_client as cdp_client
    import tools.pocket_live_observation.cdp_wire as cdp_wire

    class FakeHTTPResponse:
        status = 200

        def __enter__(self) -> "FakeHTTPResponse":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return (
                b'[{"id":"target-pocket","type":"page","url":"https://pocketoption.com/cabinet/demo-quick-high-low/",'
                b'"title":"Pocket","webSocketDebuggerUrl":"ws://127.0.0.1:9230/devtools/page/target-pocket"}]'
            )

    class FakeWire:
        def __init__(self) -> None:
            self.network_enable_received = False
            self.closed = False

        def write_json(self, payload: dict) -> None:
            self.network_enable_received = payload.get("method") == "Network.enable"

        def read_json(self) -> dict:
            return {
                "method": "Network.webSocketCreated",
                "params": {"requestId": "market", "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket"},
            }

        def close(self) -> None:
            self.closed = True

    wire = FakeWire()
    monkeypatch.setattr(cdp_client, "urlopen", lambda *_args, **_kwargs: FakeHTTPResponse())
    monkeypatch.setattr(cdp_wire, "connect_cdp_wire", lambda *_args, **_kwargs: wire)
    client = PocketLocalCDPClient(port=9230, http_timeout=2.0)

    targets = client.list_targets()
    client.attach_target(targets[0].target_id)
    client.enable_network()
    event = client.next_event()
    client.close()

    assert targets[0].url == "https://pocketoption.com/cabinet/demo-quick-high-low/"
    assert event is not None
    assert event.method == "Network.webSocketCreated"
    assert wire.network_enable_received is True
    assert wire.closed is True


def test_guard_blocks_cdp_specific_forbidden_actions() -> None:
    guard = PocketRuntimeGuard()
    for action in ("OPEN_SOCKET_DIRECTLY", "SEND_MESSAGE", "MODIFY_CDP_FRAME", "INTERCEPT_REQUEST", "REPLAY_LIVE_CREDENTIAL"):
        with pytest.raises(PocketRuntimeError) as error:
            guard.ensure_allowed(action)
        assert error.value.code == POCKET_READ_ONLY_GUARD_BLOCKED


def test_pocket_observation_code_has_no_outbound_message_primitives() -> None:
    banned_fragments = ("websocket.send", "socket.emit", "sio.emit", "Runtime.evaluate", "sendMessage", "Storage.getCookies", "Fetch.enable")
    for base in (Path("app/market/providers/pocket"), Path("tools/pocket_live_observation")):
        for path in base.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            for fragment in banned_fragments:
                assert fragment not in text, f"{fragment} found in {path}"


def _cdp_targets() -> tuple[PocketCDPTarget, ...]:
    return (
        PocketCDPTarget("friday", "page", "http://127.0.0.1:5173/market-chart"),
        PocketCDPTarget("pocket", "page", "https://pocketoption.com/cabinet/demo-quick-high-low/"),
        PocketCDPTarget("worker", "service_worker", "https://pocketoption.com/sw.js"),
    )


def _cdp_events() -> tuple[PocketCDPEvent, ...]:
    return (
        PocketCDPEvent("Network.webSocketCreated", {"requestId": "market", "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket"}),
        PocketCDPEvent("Network.webSocketCreated", {"requestId": "aux", "url": "wss://events-po.com/socket.io/?EIO=4&transport=websocket"}),
        PocketCDPEvent("Network.webSocketFrameSent", {"requestId": "market", "timestamp": 1, "response": {"payloadData": '42["changeSymbol",{"asset":"EURUSD_otc","period":60}]'}}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "market", "timestamp": 2, "response": {"payloadData": '42["updateHistoryNewFast",{"asset":"EURUSD_otc","period":60,"history":[],"candles":[[1700000000,1.0,1.1,1.2,0.9,10],[1700000060,1.1,1.2,1.3,1.0,11]]}]'}}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "market", "timestamp": 3, "response": {"payloadData": '42["updateStream",[["EURUSD_otc",1700000120.1,1.2]]]'}}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "aux", "timestamp": 4, "response": {"payloadData": '42["unknownAux",{"safe":true}]'}}),
    )
