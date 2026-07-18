from __future__ import annotations

import json

from tools.pocket_live_observation.orchestrator import config_from_env, resolve_pocket_observation_mode, run_real_passive_observation
from app.market.providers.pocket.cdp_models import PocketCDPEvent, PocketCDPTarget
from app.market.providers.pocket.cdp_observation_transport import PocketCDPObservationTransport
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.diagnostics import write_live_observation_reports
from app.market.providers.pocket.fake_cdp_client import FakePocketCDPClient
from app.market.providers.pocket.live_source import PocketReadOnlyLiveSource
from app.market.providers.pocket.runtime import PocketMarketRuntime


def main() -> None:
    print("Pocket Live Observation")
    config = config_from_env()
    decision = resolve_pocket_observation_mode(config)
    if decision.mode == "BLOCKED_UNSAFE_CONFIGURATION":
        print("Modo: BLOCKED_UNSAFE_CONFIGURATION")
        print(f"error_code: {decision.error_code}")
        return
    if decision.mode == "REAL_PASSIVE_CDP":
        report = run_real_passive_observation(config)
        _print_summary(report)
        return
    print("Modo: FAKE_CDP_ONLY")
    print("Validacao real exige autorizacao expressa do Renan e login DEMO manual.")
    client = FakePocketCDPClient(targets=_targets(), events=_events())
    runtime = PocketMarketRuntime(config=PocketProviderConfig(preserve_store_on_stop=True))
    transport = PocketCDPObservationTransport(client, config=PocketProviderConfig())
    source = PocketReadOnlyLiveSource(transport, runtime)
    source.start()
    source.stop()
    report = write_live_observation_reports(source, {"observation_mode": "FAKE_CDP_ONLY"})
    _print_summary(report)


def _print_summary(report: dict) -> None:
    print(f"target_found: {report['target_found']}")
    print(f"market_socket_found: {report['market_socket_found']}")
    print(f"history_batches: {report['history_batches']}")
    print(f"historical_candles: {report['historical_candles']}")
    print(f"stream_events: {report['stream_events']}")
    print(f"ticks: {report['ticks']}")
    print(f"observer_stopped_cleanly: {report['observer_stopped_cleanly']}")


def _targets() -> tuple[PocketCDPTarget, ...]:
    return (
        PocketCDPTarget("target-friday", "page", "http://127.0.0.1:5173/market-chart"),
        PocketCDPTarget("target-pocket", "page", "https://pocketoption.com/cabinet/demo-quick-high-low/"),
        PocketCDPTarget("target-worker", "service_worker", "https://pocketoption.com/sw.js"),
    )


def _events() -> tuple[PocketCDPEvent, ...]:
    candles = [[1700000000 + index * 60, 1.0 + index / 1000, 1.001 + index / 1000, 1.002 + index / 1000, 0.999 + index / 1000, 10] for index in range(50)]
    return (
        PocketCDPEvent("Network.webSocketCreated", {"requestId": "market-1", "url": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket"}),
        PocketCDPEvent("Network.webSocketCreated", {"requestId": "aux-1", "url": "wss://events-po.com/socket.io/?EIO=4&transport=websocket"}),
        PocketCDPEvent("Network.webSocketFrameSent", {"requestId": "market-1", "timestamp": 1, "response": {"payloadData": '42["changeSymbol",{"asset":"EURUSD_otc","period":60}]'}}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "market-1", "timestamp": 2, "response": {"payloadData": '42["updateHistoryNewFast",' + json.dumps({"asset": "EURUSD_otc", "period": 60, "history": [], "candles": candles}) + "]"}}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "market-1", "timestamp": 3, "response": {"payloadData": '42["updateStream",[["EURUSD_otc",1700003060.1,1.2]]]'}}),
        PocketCDPEvent("Network.webSocketFrameReceived", {"requestId": "aux-1", "timestamp": 4, "response": {"payloadData": '42["profile",{"discarded":true}]'}}),
    )


if __name__ == "__main__":
    main()
