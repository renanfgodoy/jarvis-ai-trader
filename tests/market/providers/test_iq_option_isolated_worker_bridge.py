from __future__ import annotations

import importlib.metadata
import subprocess
from pathlib import Path

from app.market.chart.runtime_service import MarketChartRuntimeService
from app.market.providers.iq_option.client import IQOptionReadOnlyClient
from app.market.providers.iq_option.config import IQOptionProviderConfig
from app.market.providers.iq_option.provider import IQOptionMarketDataProvider
from app.market.providers.iq_option.runtime import IQOptionProviderRuntime
from app.market.providers.iq_option.worker.asset_discovery import list_binary_turbo_assets
from app.market.providers.iq_option.worker.client import IQOptionIsolatedWorkerClient
from app.market.providers.iq_option.worker.errors import IQOptionWorkerInvalidJSON, IQOptionWorkerRejectedCommand, IQOptionWorkerTimeout
from app.market.providers.iq_option.worker.persistent_runner import PersistentIQOptionWorker
from app.market.providers.iq_option.worker.protocol import decode_response, encode_request, parse_request
from app.market.providers.models import MarketCandleRequest
from app.market.sanity import CandleSanityGuard
from app.market.store import CandleStore


def config() -> IQOptionProviderConfig:
    return IQOptionProviderConfig(
        enabled=True,
        email=None,
        password=None,
        account_mode="PRACTICE",
        read_only=True,
        default_candle_limit=1000,
        poll_interval_seconds=1.0,
    )


def fake_worker_command(command: str, params: dict | None = None) -> dict:
    if command == "connect":
        return {"connected": True, "read_only": True}
    if command == "disconnect":
        return {"disconnect_status": "DISCONNECTED"}
    if command == "status":
        return {"provider": "IQ_OPTION", "isolated_worker": True, "library_version": "7.1.1"}
    if command in {"list_assets", "list_otc_assets"}:
        market_type = (params or {}).get("market_type", "OTC")
        if market_type == "REGULAR":
            return {
                "assets": [
                    {"symbol": "EURUSD", "category": "digital", "is_open": True, "market_type": "REGULAR"},
                ]
            }
        return {
            "assets": [
                {"symbol": "EURUSD-OTC", "category": "digital", "is_open": True, "market_type": "OTC"},
                {"symbol": "GBPUSD-OTC", "category": "digital", "is_open": True, "market_type": "OTC"},
            ]
        }
    if command == "get_candles":
        raw_size = int(params["raw_size"])
        limit = int(params["limit"])
        base = 1_783_720_000
        return {
            "provider": "IQ_OPTION",
            "symbol": params["symbol"],
            "raw_size": raw_size,
            "count": limit,
            "candles": [
                {"from": base + index * raw_size, "to": base + (index + 1) * raw_size, "open": 1.1, "max": 1.3, "min": 1.0, "close": 1.2, "volume": index}
                for index in range(limit)
            ],
        }
    raise AssertionError(command)


class FakeBinaryTurboClient:
    def __init__(self) -> None:
        self.open_time_called = False

    def get_all_open_time(self):
        self.open_time_called = True
        raise AssertionError("get_all_open_time must not be used for IQ Option asset discovery.")

    def get_all_ACTIVES_OPCODE(self):
        return {
            "EURUSD-OTC": 76,
            "BTCUSD-OTC": 99,
            "EURUSD": 1,
            "AMAZON": 31,
        }

    def get_all_init_v2(self):
        return {
            "digital": {
                "actives": {
                    "999": {"name": "digital.EURUSD-OTC", "enabled": True, "is_suspended": False},
                }
            },
            "turbo": {
                "actives": {
                    "1": {"name": "turbo.EURUSD-OTC", "enabled": True, "is_suspended": False},
                    "2": {"name": "turbo.GBPUSD-OTC", "enabled": False, "is_suspended": False},
                    "3": {"name": "turbo.USDJPY-OTC", "enabled": True, "is_suspended": True},
                    "4": {"name": "turbo.EURUSD", "enabled": True, "is_suspended": False},
                    "8": {"name": "turbo.AMAZON-OTC", "enabled": True, "is_suspended": False},
                }
            },
            "binary": {
                "actives": {
                    "5": {"name": "binary.BTCUSD-OTC", "enabled": True, "is_suspended": False},
                    "6": {"name": "binary.EURUSD", "enabled": True, "is_suspended": False},
                    "7": {"name": "binary.XAUUSD", "enabled": False, "is_suspended": False},
                }
            },
        }


class FailingAssetDiscoveryClient:
    def get_all_init_v2(self):
        raise RuntimeError("library exploded with private details")


def test_worker_protocol_accepts_only_sanitized_commands() -> None:
    request = parse_request('{"command":"get_candles","params":{"symbol":"EURUSD-OTC","raw_size":60,"limit":1000,"market_type":"OTC"}}')

    assert request.command == "get_candles"
    assert "password" not in encode_request("status")


def test_worker_protocol_allows_only_read_only_realtime_commands() -> None:
    start = parse_request('{"command":"start_realtime_candles","params":{"symbol":"EURUSD-OTC","raw_size":60,"maxdict":20}}')
    get = parse_request('{"command":"get_realtime_candles","params":{"symbol":"EURUSD-OTC","raw_size":60}}')
    stop = parse_request('{"command":"stop_realtime_candles","params":{"symbol":"EURUSD-OTC","raw_size":60}}')

    assert start.command == "start_realtime_candles"
    assert get.command == "get_realtime_candles"
    assert stop.command == "stop_realtime_candles"
    assert "buy" not in encode_request("start_realtime_candles", {"symbol": "EURUSD-OTC", "raw_size": 60, "maxdict": 20})


def test_worker_protocol_rejects_credentials_and_order_params() -> None:
    for payload in (
        '{"command":"connect","params":{"password":"secret"}}',
        '{"command":"get_candles","params":{"symbol":"EURUSD-OTC","raw_size":60,"amount":1}}',
    ):
        try:
            parse_request(payload)
        except IQOptionWorkerRejectedCommand:
            continue
        raise AssertionError("Expected rejected command.")


def test_worker_response_schema_and_contaminated_stdout() -> None:
    response = decode_response('{"success":true,"data":{"provider":"IQ_OPTION"},"error_code":null}')

    assert response.success is True
    try:
        decode_response('noise\n{"success":true,"data":{},"error_code":null}')
    except IQOptionWorkerInvalidJSON:
        return
    raise AssertionError("Expected invalid JSON for contaminated stdout.")


def test_client_handles_timeout_invalid_json_and_worker_failure(monkeypatch) -> None:
    client = IQOptionIsolatedWorkerClient(timeout_seconds=0.01)

    def timeout_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="worker", timeout=0.01)

    monkeypatch.setattr(subprocess, "run", timeout_run)
    try:
        client._one_shot_command("status")
    except IQOptionWorkerTimeout:
        pass
    else:
        raise AssertionError("Expected timeout.")

    def invalid_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="not-json", stderr="")

    monkeypatch.setattr(subprocess, "run", invalid_run)
    try:
        client._one_shot_command("status")
    except IQOptionWorkerInvalidJSON:
        pass
    else:
        raise AssertionError("Expected invalid JSON.")


def test_main_venv_has_no_iqoptionapi_and_worker_venv_has_it() -> None:
    try:
        importlib.metadata.version("iqoptionapi")
    except importlib.metadata.PackageNotFoundError:
        pass
    else:
        raise AssertionError("Main .venv must not have iqoptionapi installed.")

    result = subprocess.run(
        [".jarvis_cache/iq_option_probe_venv/bin/python", "-m", "pip", "show", "iqoptionapi"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Version: 7.1.1" in result.stdout


def test_worker_status_runs_in_isolated_venv() -> None:
    result = subprocess.run(
        [".jarvis_cache/iq_option_probe_venv/bin/python", "-m", "app.market.providers.iq_option.worker.runner"],
        input=encode_request("status"),
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    response = decode_response(result.stdout)
    assert response.success is True
    assert response.data["isolated_worker"] is True
    assert response.data["library_version"] == "7.1.1"


def test_persistent_worker_status_runs_without_connecting() -> None:
    result = subprocess.run(
        [".jarvis_cache/iq_option_probe_venv/bin/python", "-m", "app.market.providers.iq_option.worker.persistent_runner"],
        input=encode_request("status") + "\n" + encode_request("stop") + "\n",
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    lines = [line for line in result.stdout.splitlines() if line.strip()]
    response = decode_response(lines[0])
    assert response.success is True
    assert response.data["persistent_worker"] is True
    assert response.data["connect_count"] == 0


def test_persistent_worker_uses_short_bounded_timeouts() -> None:
    source = Path("/Users/renangodoy/Desktop/jarvis-ai-trader/app/market/providers/iq_option/worker/persistent_runner.py").read_text(encoding="utf-8")

    assert "CONNECT_TIMEOUT_SECONDS = 8" in source
    assert "ASSET_TIMEOUT_SECONDS = 6" in source
    assert "CANDLE_TIMEOUT_SECONDS = 8" in source
    assert "timeout_seconds=ASSET_TIMEOUT_SECONDS" in source
    assert "timeout_seconds=CANDLE_TIMEOUT_SECONDS" in source


def test_binary_turbo_asset_discovery_does_not_call_blocking_open_time() -> None:
    client = FakeBinaryTurboClient()

    assets = list_binary_turbo_assets(client, market_type="OTC")

    assert client.open_time_called is False
    assert [asset["symbol"] for asset in assets] == ["AMAZON", "BTCUSD-OTC", "EURUSD-OTC"]
    assert [asset["raw_symbol"] for asset in assets] == ["AMAZON-OTC", "BTCUSD-OTC", "EURUSD-OTC"]
    assert {asset["category"] for asset in assets} == {"binary", "turbo"}
    assert all(asset["is_open"] is True for asset in assets)
    assert all(asset["market_type"] == "OTC" for asset in assets)
    assert all(asset["discovery_scope"] == "BINARY_TURBO" for asset in assets)


def test_binary_turbo_asset_discovery_filters_closed_and_separates_regular() -> None:
    client = FakeBinaryTurboClient()

    regular = list_binary_turbo_assets(client, market_type="REGULAR")

    assert [asset["symbol"] for asset in regular] == ["EURUSD"]
    assert regular[0]["market_type"] == "REGULAR"
    assert regular[0]["is_open"] is True


def test_binary_turbo_asset_discovery_rejects_catalog_without_open_status() -> None:
    class CatalogOnlyClient:
        def get_all_init_v2(self):
            return {
                "turbo": {"actives": {"1": {"name": "turbo.EURUSD-OTC"}}},
                "binary": {"actives": {"2": {"name": "binary.EURUSD"}}},
            }

    assert list_binary_turbo_assets(CatalogOnlyClient(), market_type="OTC") == []
    assert list_binary_turbo_assets(CatalogOnlyClient(), market_type="REGULAR") == []


def test_persistent_worker_list_assets_uses_binary_turbo_discovery() -> None:
    worker = PersistentIQOptionWorker()
    worker.client = FakeBinaryTurboClient()
    worker.connected = True

    otc_assets = worker._list_assets("OTC")
    regular_assets = worker._list_assets("REGULAR")

    assert [asset["symbol"] for asset in otc_assets] == ["AMAZON", "BTCUSD-OTC", "EURUSD-OTC"]
    assert [asset["symbol"] for asset in regular_assets] == ["EURUSD"]


def test_persistent_worker_asset_failure_is_sanitized() -> None:
    worker = PersistentIQOptionWorker()
    worker.client = FailingAssetDiscoveryClient()
    worker.connected = True

    response = worker._handle_raw(encode_request("list_assets", {"market_type": "OTC"}))

    assert response["success"] is False
    assert response["error_code"] == "RuntimeError"


def test_backend_provider_uses_worker_without_main_iqoptionapi(monkeypatch) -> None:
    monkeypatch.setattr(IQOptionIsolatedWorkerClient, "_command", lambda _self, command, params=None: fake_worker_command(command, params))
    client = IQOptionReadOnlyClient(config())
    provider = IQOptionMarketDataProvider(config(), client)

    status = provider.connect()
    assets = provider.list_assets()

    assert status.connected is True
    assert status.configured is True
    assert status.library_version == "isolated-worker"
    assert [asset.symbol for asset in assets] == ["EURUSD-OTC", "GBPUSD-OTC"]


def test_store_and_chart_api_receive_worker_candles(monkeypatch) -> None:
    monkeypatch.setattr(IQOptionIsolatedWorkerClient, "_command", lambda _self, command, params=None: fake_worker_command(command, params))
    store = CandleStore(max_candles_per_series=1000)
    provider = IQOptionMarketDataProvider(config(), IQOptionReadOnlyClient(config()))
    provider.connect()
    runtime = IQOptionProviderRuntime(provider, store, CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))

    result = runtime.load_history(MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=1000))
    series = MarketChartRuntimeService(store).get_provider_series("IQ_OPTION", "EURUSD-OTC", 60, 1000)

    assert result.accepted == 1000
    assert result.stored == 1000
    assert len(series.candles) == 1000
    assert series.symbol == "EURUSD-OTC"


def test_small_worker_refresh_does_not_shrink_existing_chart_series(monkeypatch) -> None:
    monkeypatch.setattr(IQOptionIsolatedWorkerClient, "_command", lambda _self, command, params=None: fake_worker_command(command, params))
    store = CandleStore(max_candles_per_series=1000)
    provider = IQOptionMarketDataProvider(config(), IQOptionReadOnlyClient(config()))
    provider.connect()
    runtime = IQOptionProviderRuntime(provider, store, CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))
    chart_service = MarketChartRuntimeService(store)

    bootstrap = runtime.load_history(MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=1000))
    refresh = runtime.load_history(MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=5))
    series = chart_service.get_provider_series("IQ_OPTION", "EURUSD-OTC", 60, 1000)

    assert bootstrap.accepted == 1000
    assert refresh.accepted == 5
    assert len(series.candles) == 1000


def test_backend_source_does_not_import_iqoptionapi_directly() -> None:
    root = Path("/Users/renangodoy/Desktop/jarvis-ai-trader/app/market/providers/iq_option")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.py") if "__pycache__" not in path.parts)

    assert "from iqoptionapi" not in source
    assert "import iqoptionapi" not in source
