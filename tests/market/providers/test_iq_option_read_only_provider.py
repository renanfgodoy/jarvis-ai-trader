from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.market.persistence import CandlePersistenceService, SQLiteCandleRepository
from app.market.providers.errors import ProviderDisabledError, ProviderValidationError
from app.market.providers.iq_option.client import IQOptionReadOnlyClient
from app.market.providers.iq_option.config import IQOptionProviderConfig
from app.market.providers.iq_option.mapper import display_name_for_symbol, map_assets, map_candles
from app.market.providers.iq_option.provider import IQOptionMarketDataProvider
from app.market.providers.iq_option.runtime import IQOptionProviderRuntime
from app.market.providers.models import MarketCandleRequest
from app.market.sanity import CandleSanityGuard
from app.market.store import CandleStore

client = TestClient(app)


class FakeIQApi:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password
        self.connected = False
        self.balance_mode = None
        self.candle_calls = 0
        self.started_streams: list[tuple[str, int, int]] = []
        self.stopped_streams: list[tuple[str, int]] = []
        self.realtime_close = 1.205

    def set_max_reconnect(self, value: int) -> None:
        self.max_reconnect = value

    def connect(self):
        self.connected = True
        return True, None

    def check_connect(self) -> bool:
        return self.connected

    def change_balance(self, mode: str) -> None:
        self.balance_mode = mode

    def close(self) -> None:
        self.connected = False

    def get_all_open_time(self):
        return {
            "digital": {
                "EURUSD-OTC": {"open": True},
                "EURUSD": {"open": True},
            },
            "turbo": {
                "EURUSD-OTC": {"open": True},
                "GBPJPY-OTC": {"open": False},
            },
            "binary": {"BTCUSD-OTC": {"open": True}},
        }

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
                    "1": {"name": "digital.EURUSD-OTC", "enabled": True, "is_suspended": False},
                    "2": {"name": "digital.EURUSD", "enabled": True, "is_suspended": False},
                }
            },
            "turbo": {
                "actives": {
                    "3": {"name": "turbo.EURUSD-OTC", "enabled": True, "is_suspended": False},
                    "4": {"name": "turbo.GBPJPY-OTC", "enabled": False, "is_suspended": False},
                    "7": {"name": "turbo.AMAZON-OTC", "enabled": True, "is_suspended": False},
                }
            },
            "binary": {
                "actives": {
                    "5": {"name": "binary.BTCUSD-OTC", "enabled": True, "is_suspended": False},
                    "6": {"name": "binary.EURUSD", "enabled": True, "is_suspended": False},
                }
            },
        }

    def get_candles(self, symbol: str, raw_size: int, limit: int, now: float):
        self.candle_calls += 1
        base = 1_783_720_000
        return [
            {"from": base + index * raw_size, "open": 1.1, "close": 1.2 + index / 10000, "min": 1.0, "max": 1.3, "volume": index}
            for index in range(limit)
        ]

    def start_candles_stream(self, symbol: str, raw_size: int, maxdict: int):
        self.started_streams.append((symbol, raw_size, maxdict))
        return True

    def get_realtime_candles(self, symbol: str, raw_size: int):
        self.realtime_close += 0.001
        bucket = int(time.time() // raw_size) * raw_size
        return {
            bucket: {"from": bucket, "open": 1.2, "close": self.realtime_close, "min": 1.19, "max": self.realtime_close, "volume": 10}
        }

    def stop_candles_stream(self, symbol: str, raw_size: int):
        self.stopped_streams.append((symbol, raw_size))
        return True


class FailingIQApi(FakeIQApi):
    def connect(self):
        return False, "failed"


class StopFailingIQApi(FakeIQApi):
    def stop_candles_stream(self, symbol: str, raw_size: int):
        self.stopped_streams.append((symbol, raw_size))
        raise RuntimeError("stop failed")


def config(*, enabled: bool = True, email: str | None = "operator@example.com", password: str | None = "secret") -> IQOptionProviderConfig:
    return IQOptionProviderConfig(
        enabled=enabled,
        email=email,
        password=password,
        account_mode="PRACTICE",
        read_only=True,
        default_candle_limit=200,
        poll_interval_seconds=0.01,
    )


def provider_with_fake(api_cls=FakeIQApi, *, enabled: bool = True, email: str | None = "operator@example.com", password: str | None = "secret"):
    cfg = config(enabled=enabled, email=email, password=password)
    client_wrapper = IQOptionReadOnlyClient(cfg, api_factory=api_cls)
    return IQOptionMarketDataProvider(cfg, client_wrapper)


def test_provider_disabled_blocks_connection() -> None:
    provider = provider_with_fake(enabled=False)

    try:
        provider.connect()
    except ProviderDisabledError as exc:
        assert exc.error_code == "PROVIDER_DISABLED"
    else:
        raise AssertionError("Expected disabled provider to block connection.")


def test_credentials_missing_are_not_exposed_in_status() -> None:
    provider = provider_with_fake(email=None, password=None)
    status = provider.connection_status().sanitized()

    assert status["configured"] is False
    assert "operator@example.com" not in str(status)
    assert "secret" not in str(status)


def test_connection_fake_success_uses_practice_and_sanitized_status() -> None:
    provider = provider_with_fake()

    status = provider.connect().sanitized()

    assert status["connected"] is True
    assert status["account_mode"] == "PRACTICE"
    assert status["read_only"] is True
    assert status["library_source"]
    assert "operator@example.com" not in str(status)
    assert "secret" not in str(status)


def test_connection_failure_is_sanitized() -> None:
    provider = provider_with_fake(FailingIQApi)

    try:
        provider.connect()
    except Exception:
        status = provider.connection_status().sanitized()
    else:
        raise AssertionError("Expected fake connection failure.")

    assert status["last_error_code"] == "PROVIDER_CONNECTION_FAILED"


def test_otc_asset_mapping_filters_deduplicates_and_formats_names() -> None:
    assets = map_assets(FakeIQApi("x", "y").get_all_open_time())

    assert [asset.symbol for asset in assets] == ["BTCUSD-OTC", "EURUSD-OTC"]
    assert display_name_for_symbol("EURUSD-OTC") == "EUR/USD OTC"
    assert display_name_for_symbol("AMAZON-OTC") == "AMAZON OTC"
    assert assets[0].provider == "IQ_OPTION"


def test_provider_asset_discovery_translates_otc_stock_to_candle_symbol() -> None:
    provider = provider_with_fake()
    provider.connect()
    assets = provider.list_assets(market_type="OTC")

    amazon = next(asset for asset in assets if asset.display_name == "AMAZON OTC")
    assert amazon.symbol == "AMAZON"
    assert amazon.market_type == "OTC"
    assert amazon.is_otc is True


def test_regular_asset_mapping_filters_only_open_regular_assets() -> None:
    assets = map_assets(FakeIQApi("x", "y").get_all_open_time(), market_type="REGULAR")

    assert [asset.symbol for asset in assets] == ["EURUSD"]
    assert assets[0].market_type == "REGULAR"
    assert assets[0].is_otc is False


def test_m1_m5_m15_and_invalid_timeframe_mapping() -> None:
    raw = FakeIQApi("x", "y").get_candles("EURUSD-OTC", 60, 2, time.time())

    assert len(map_candles("EURUSD-OTC", 60, raw)) == 2
    assert len(map_candles("EURUSD-OTC", 300, raw)) == 2
    assert len(map_candles("EURUSD-OTC", 900, raw)) == 2
    try:
        map_candles("EURUSD-OTC", 120, raw)
    except ValueError as exc:
        assert str(exc) == "UNSUPPORTED_TIMEFRAME"
    else:
        raise AssertionError("Expected unsupported timeframe.")


def test_history_ordering_deduplication_and_ohlc_normalization() -> None:
    raw = [
        {"from": 200, "open": 1.2, "close": 1.25, "low": 1.1, "high": 1.3},
        {"from": 100, "open": 1.1, "close": 1.2, "min": 1.0, "max": 1.3},
        {"from": 100, "open": 1.15, "close": 1.22, "min": 1.0, "max": 1.3},
    ]

    candles = map_candles("EURUSD-OTC", 60, raw)

    assert [candle.start_timestamp for candle in candles] == [100, 200]
    assert candles[0].open == 1.15
    assert candles[0].high == 1.3
    assert candles[0].low == 1.0


def test_runtime_rejects_invalid_candle_and_stores_valid_iq_series_without_polarium_collision() -> None:
    provider = provider_with_fake()
    provider.connect()
    store = CandleStore()
    runtime = IQOptionProviderRuntime(provider, store, CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))

    result = runtime.load_history(MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=2))

    assert result.accepted == 2
    assert store.series_by_key(next(key for key in store.series_keys() if key.provider == "IQ_OPTION"))[0].symbol == "EURUSD-OTC"
    assert store.series(76, 60) == ()


def test_sanity_guard_rejects_invalid_iq_candle() -> None:
    candle = map_candles("EURUSD-OTC", 60, [{"from": 1_783_720_000, "open": 2.0, "close": 1.2, "min": 1.0, "max": 1.3}])[0]
    provider = provider_with_fake()
    store = CandleStore()
    runtime = IQOptionProviderRuntime(provider, store, CandleSanityGuard(min_timestamp=1_500_000_000))

    result = runtime._store_batch(type("Batch", (), {"candles": (candle,)})())

    assert result.rejected == 1
    assert result.last_error_code == "OPEN_OUT_OF_RANGE"


def test_realtime_candles_start_store_update_and_stop_read_only_stream() -> None:
    provider = provider_with_fake()
    provider.connect()
    store = CandleStore()
    runtime = IQOptionProviderRuntime(provider, store, CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))
    request = MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=20, market_type="OTC")

    first = runtime.load_realtime_update(request)
    second = runtime.load_realtime_update(request)
    runtime.stop_realtime()

    assert first.stream_started is True
    assert first.source_mode == "NEAR_REALTIME"
    assert first.load.stored == 1
    assert second.load.updated == 1
    key = next(key for key in store.series_keys() if key.provider == "IQ_OPTION")
    assert key.symbol == "EURUSD-OTC"
    assert store.series_by_key(key)[0].close > 1.2
    fake_api = provider._client._api
    assert fake_api.started_streams == [("EURUSD-OTC", 60, 20)]
    assert fake_api.stopped_streams == [("EURUSD-OTC", 60)]


def test_realtime_context_switch_tolerates_previous_stream_stop_failure() -> None:
    provider = provider_with_fake(StopFailingIQApi)
    provider.connect()
    store = CandleStore()
    runtime = IQOptionProviderRuntime(provider, store, CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))

    first = runtime.load_realtime_update(MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=20, market_type="OTC"))
    second = runtime.load_realtime_update(MarketCandleRequest(symbol="GBPUSD-OTC", raw_size=60, limit=20, market_type="OTC"))

    assert first.stream_started is True
    assert second.stream_started is True
    fake_api = provider._client._api
    assert fake_api.started_streams == [("EURUSD-OTC", 60, 20), ("GBPUSD-OTC", 60, 20)]
    assert fake_api.stopped_streams == [("EURUSD-OTC", 60)]


def test_realtime_stream_event_is_sanitized_and_sequence_increases() -> None:
    provider = provider_with_fake()
    provider.connect()
    runtime = IQOptionProviderRuntime(provider, CandleStore(), CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))
    request = MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=20, market_type="OTC")
    subscription = runtime.begin_realtime_stream(request)

    first, first_signature = runtime.next_realtime_stream_event(subscription, request, None)
    second, _second_signature = runtime.next_realtime_stream_event(subscription, request, first_signature)
    heartbeat = runtime.realtime_stream_heartbeat(subscription, request)

    assert first is not None
    assert second is not None
    assert heartbeat is not None
    first_payload = first.sanitized()
    heartbeat_payload = heartbeat.sanitized()
    assert first_payload["sequence"] == 1
    assert second.sanitized()["sequence"] == 2
    assert heartbeat_payload["sequence"] == 3
    assert first_payload["candle"]["timestamp"]
    assert "password" not in str(first_payload).lower()
    assert "authorization" not in str(first_payload).lower()
    assert "cookie" not in str(first_payload).lower()
    assert "candle" not in heartbeat_payload


def test_realtime_stream_cleanup_removes_subscriber() -> None:
    provider = provider_with_fake()
    runtime = IQOptionProviderRuntime(provider, CandleStore(), CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))
    request = MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=20, market_type="OTC")
    subscription = runtime.begin_realtime_stream(request)

    assert runtime.realtime_stream_status()["subscribers"] == {"OTC:EURUSD-OTC:60": 1}

    runtime.end_realtime_stream(subscription)

    assert runtime.realtime_stream_status()["subscribers"] == {}


def test_realtime_stream_context_switch_invalidates_previous_stream_without_cross_update() -> None:
    provider = provider_with_fake()
    provider.connect()
    runtime = IQOptionProviderRuntime(provider, CandleStore(), CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))
    first_request = MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=20, market_type="OTC")
    second_request = MarketCandleRequest(symbol="GBPUSD-OTC", raw_size=60, limit=20, market_type="OTC")
    first_subscription = runtime.begin_realtime_stream(first_request)
    second_subscription = runtime.begin_realtime_stream(second_request)

    old_event, old_signature = runtime.next_realtime_stream_event(first_subscription, first_request, None)
    new_event, _new_signature = runtime.next_realtime_stream_event(second_subscription, second_request, None)

    assert old_event is None
    assert old_signature is None
    assert new_event is not None
    assert new_event.symbol == "GBPUSD-OTC"
    assert runtime.is_realtime_stream_current(first_subscription) is False
    assert runtime.is_realtime_stream_current(second_subscription) is True


def test_realtime_stream_subscriber_count_returns_to_one_after_switch_cleanup() -> None:
    provider = provider_with_fake()
    runtime = IQOptionProviderRuntime(provider, CandleStore(), CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))
    first_request = MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=20, market_type="OTC")
    second_request = MarketCandleRequest(symbol="GBPUSD-OTC", raw_size=60, limit=20, market_type="OTC")

    assert runtime.realtime_stream_status()["subscribers"] == {}
    first_subscription = runtime.begin_realtime_stream(first_request)
    assert runtime.realtime_stream_status()["subscribers"] == {"OTC:EURUSD-OTC:60": 1}
    runtime.end_realtime_stream(first_subscription)
    second_subscription = runtime.begin_realtime_stream(second_request)
    assert runtime.realtime_stream_status()["subscribers"] == {"OTC:GBPUSD-OTC:60": 1}
    runtime.end_realtime_stream(second_subscription)
    assert runtime.realtime_stream_status()["subscribers"] == {}


def test_realtime_stream_multiple_subscribers_reuse_same_iq_context() -> None:
    provider = provider_with_fake()
    provider.connect()
    runtime = IQOptionProviderRuntime(provider, CandleStore(), CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))
    request = MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=20, market_type="OTC")
    first_subscription = runtime.begin_realtime_stream(request)
    second_subscription = runtime.begin_realtime_stream(request)

    first_event, first_signature = runtime.next_realtime_stream_event(first_subscription, request, None)
    second_event, _second_signature = runtime.next_realtime_stream_event(second_subscription, request, first_signature)

    assert first_event is not None
    assert second_event is not None
    assert runtime.realtime_stream_status()["subscribers"] == {"OTC:EURUSD-OTC:60": 2}
    assert provider._client._api.started_streams == [("EURUSD-OTC", 60, 20)]


def test_persistence_separates_iq_option_and_restores_symbol_series(tmp_path: Path) -> None:
    repository = SQLiteCandleRepository(tmp_path / "candles.sqlite3")
    service = CandlePersistenceService(repository)
    store = CandleStore()
    provider = provider_with_fake()
    provider.connect()
    runtime = IQOptionProviderRuntime(provider, store, CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))
    service.restore_into_store(store)
    store.set_write_observer(service.persist_write)

    runtime.load_history(MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=2))
    restored = CandleStore()
    service.restore_into_store(restored)

    keys = restored.series_keys()
    assert len(keys) == 1
    assert keys[0].provider == "IQ_OPTION"
    assert keys[0].symbol == "EURUSD-OTC"
    assert len(restored.series_by_key(keys[0])) == 2


def test_migrates_existing_polarium_database_without_losing_rows(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE schema_version (version INTEGER NOT NULL)")
        connection.execute("INSERT INTO schema_version VALUES (1)")
        connection.execute(
            "CREATE TABLE market_candles (active_id INTEGER NOT NULL, raw_size INTEGER NOT NULL, start_timestamp INTEGER NOT NULL, end_timestamp INTEGER, open REAL NOT NULL, close REAL NOT NULL, low_candidate REAL NOT NULL, high_candidate REAL NOT NULL, volume REAL, mapping_verified INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY (active_id, raw_size, start_timestamp))"
        )
        connection.execute(
            "INSERT INTO market_candles VALUES (76, 60, 1783720000, 1783720060, 1.1, 1.2, 1.0, 1.3, 0, 0, 'a', 'a')"
        )

    repository = SQLiteCandleRepository(path)
    repository.initialize()
    candles = repository.load_all()

    assert len(candles) == 1
    assert candles[0].source == "polarium"
    assert repository.count_series() == 1


def test_polling_blocks_overlapping_requests_and_can_stop_cleanly() -> None:
    provider = provider_with_fake()
    provider.connect()
    runtime = IQOptionProviderRuntime(provider, CandleStore(), CandleSanityGuard(min_timestamp=1_500_000_000, future_tolerance_seconds=10_000_000_000))

    runtime.start_polling(MarketCandleRequest(symbol="EURUSD-OTC", raw_size=60, limit=2), interval_seconds=0.01)
    time.sleep(0.03)
    runtime.stop_polling()

    assert provider.metrics.poll_cycles >= 1


def test_api_status_and_credentials_rejection_are_sanitized() -> None:
    status = client.get("/api/v1/market/providers/iq-option/status")
    credentials = client.post("/api/v1/market/providers/iq-option/connect", json={"email": "x", "password": "y"})

    assert status.status_code == 200
    assert "password" not in str(status.json()).lower()
    assert credentials.status_code == 400
    assert credentials.json()["detail"]["error_code"] == "CREDENTIALS_NOT_ACCEPTED_BY_ENDPOINT"


def test_no_order_or_balance_endpoints_are_registered() -> None:
    routes = [getattr(route, "path", "") for route in app.routes if "/market/providers/iq-option" in getattr(route, "path", "")]
    serialized = " ".join(routes).lower()

    assert "buy" not in serialized
    assert "sell" not in serialized
    assert "balance" not in serialized
    assert "order" not in serialized


def test_iq_option_candles_route_supports_small_refresh_limit_without_changing_chart_limit() -> None:
    source = Path("/Users/renangodoy/Desktop/jarvis-ai-trader/app/api/routes/market_providers.py").read_text(encoding="utf-8")

    assert "refresh_limit: int | None = Query(default=None, ge=1, le=50)" in source
    assert "load_limit = refresh_limit if refresh_limit is not None else limit" in source
    assert "MarketCandleRequest(symbol=symbol, raw_size=raw_size, limit=load_limit, market_type=market_type)" in source
    assert 'get_provider_series("IQ_OPTION", symbol, raw_size, limit)' in source


def test_iq_option_series_integrity_endpoint_is_registered_and_sanitized() -> None:
    response = client.get("/api/v1/market/providers/iq-option/series-integrity", params={"symbol": "EURUSD-OTC", "raw_size": 60})

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "IQ_OPTION"
    assert payload["symbol"] == "EURUSD-OTC"
    assert payload["raw_size"] == 60
    assert "candles" not in payload
    assert "authorization" not in str(payload).lower()


def test_provider_source_contains_no_order_function_usage() -> None:
    root = Path("/Users/renangodoy/Desktop/jarvis-ai-trader/app/market/providers/iq_option")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))

    for forbidden in ["buy(", "buy_digital_spot", "buy_digital_spot_v2", "sell_option", "close_position", "reset_practice_balance"]:
        assert forbidden not in source
