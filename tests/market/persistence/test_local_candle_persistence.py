from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.market.events.models import NormalizedMarketCandle
from app.market.persistence import CandlePersistenceService, SQLiteCandleRepository
from app.market.runtime import market_candle_persistence, market_candle_store, market_pipeline
from app.market.store import CandleStore

client = TestClient(app)


def make_candle(
    start_timestamp: int,
    *,
    active_id: int = 76,
    raw_size: int = 60,
    close: float = 1.2,
    symbol: str | None = None,
    mapping_verified: bool = False,
) -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=active_id,
        symbol=symbol,
        raw_size=raw_size,
        timeframe=None,
        start_timestamp=start_timestamp,
        end_timestamp=start_timestamp + raw_size,
        open=1.1,
        close=close,
        low_candidate=1.0,
        high_candidate=1.3,
        volume=0,
        source="polarium",
        source_event="candle-generated",
        source_verified=True,
        mapping_verified=mapping_verified,
        mapping_notes=("sanitized fixture",),
    )


def make_message(start_timestamp: int, *, active_id: int = 76, raw_size: int = 60, close: float = 1.2) -> dict:
    return {
        "name": "candle-generated",
        "msg": {
            "body": {
                "active_id": active_id,
                "size": raw_size,
                "from": start_timestamp,
                "to": start_timestamp + raw_size,
                "open": 1.1,
                "close": close,
                "min": 1.0,
                "max": 1.3,
                "volume": 0,
            }
        },
    }


def service_for(path: Path, *, retention: int = 1000) -> CandlePersistenceService:
    return CandlePersistenceService(SQLiteCandleRepository(path), retention_per_series=retention)


def test_sqlite_repository_creates_database_and_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "market" / "candles.sqlite3"
    repository = SQLiteCandleRepository(database_path)

    repository.initialize()

    assert database_path.exists()
    with sqlite3.connect(database_path) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        version = connection.execute("SELECT version FROM schema_version").fetchone()[0]
    assert {"market_candles", "schema_version"}.issubset(tables)
    assert version == 2


def test_insert_ignore_and_update_existing_candle(tmp_path: Path) -> None:
    repository = SQLiteCandleRepository(tmp_path / "candles.sqlite3")
    repository.initialize()
    candle = make_candle(100, close=1.2)

    inserted = repository.upsert(candle)
    ignored = repository.upsert(candle)
    updated = repository.upsert(make_candle(100, close=1.25))
    restored = repository.load_all()

    assert inserted.status == "inserted"
    assert ignored.status == "ignored"
    assert updated.status == "updated"
    assert len(restored) == 1
    assert restored[0].close == 1.25


def test_repository_persists_observed_symbol_when_present(tmp_path: Path) -> None:
    repository = SQLiteCandleRepository(tmp_path / "candles.sqlite3")
    repository.initialize()

    repository.upsert(make_candle(100, symbol="EUR/USD OTC"))
    restored = repository.load_all()

    assert restored[0].symbol == "EUR/USD OTC"


def test_repository_restores_null_symbol_when_absent(tmp_path: Path) -> None:
    repository = SQLiteCandleRepository(tmp_path / "candles.sqlite3")
    repository.initialize()

    repository.upsert(make_candle(100))
    restored = repository.load_all()

    assert restored[0].symbol is None


def test_repository_separates_active_id_and_raw_size_and_orders_by_timestamp(tmp_path: Path) -> None:
    repository = SQLiteCandleRepository(tmp_path / "candles.sqlite3")
    repository.initialize()
    repository.upsert(make_candle(300, active_id=76, raw_size=60))
    repository.upsert(make_candle(100, active_id=76, raw_size=60))
    repository.upsert(make_candle(200, active_id=2298, raw_size=60))
    repository.upsert(make_candle(150, active_id=76, raw_size=300))

    restored = repository.load_all()

    assert [(item.active_id, item.raw_size, item.start_timestamp) for item in restored] == [
        (76, 60, 100),
        (76, 60, 300),
        (76, 300, 150),
        (2298, 60, 200),
    ]
    assert repository.count_series() == 3
    assert repository.count_candles() == 4


def test_service_restores_into_same_shared_store_without_duplicates(tmp_path: Path) -> None:
    repository = SQLiteCandleRepository(tmp_path / "candles.sqlite3")
    service = CandlePersistenceService(repository)
    store = CandleStore()
    repository.initialize()
    repository.upsert(make_candle(100))
    repository.upsert(make_candle(200))

    first_restore = service.restore_into_store(store)
    second_restore = service.restore_into_store(store)

    assert [result.status for result in first_restore] == ["added", "added"]
    assert [result.status for result in second_restore] == ["ignored", "ignored"]
    assert len(store.series(76, 60)) == 2
    assert service.status().restored_candles_count == 2


def test_service_persists_store_writes_and_applies_retention(tmp_path: Path) -> None:
    repository = SQLiteCandleRepository(tmp_path / "candles.sqlite3")
    service = CandlePersistenceService(repository, retention_per_series=3)
    store = CandleStore(max_candles_per_series=3)
    service.restore_into_store(store)
    store.set_write_observer(service.persist_write)

    for timestamp in [100, 200, 300, 400, 500]:
        store.add(make_candle(timestamp))

    restored = repository.load_all()

    assert [item.start_timestamp for item in restored] == [300, 400, 500]
    assert service.status().persisted_candles_count == 3
    assert service.status().retention_per_series == 3


def test_empty_and_missing_database_restore_safely(tmp_path: Path) -> None:
    service = service_for(tmp_path / "missing" / "candles.sqlite3")
    store = CandleStore()

    results = service.restore_into_store(store)

    assert results == ()
    assert store.series_keys() == ()
    assert service.status().database_ready is True


def test_corrupt_database_error_is_sanitized(tmp_path: Path) -> None:
    database_path = tmp_path / "candles.sqlite3"
    database_path.write_text("not sqlite", encoding="utf-8")
    service = service_for(database_path)

    service.initialize()

    assert service.status().database_ready is False
    assert service.status().last_error_code == "SQLITE_INITIALIZE_FAILED"
    assert "not sqlite" not in str(service.status().sanitized()).lower()


def test_persistence_stores_no_credentials_payload_or_mapping_claims(tmp_path: Path) -> None:
    database_path = tmp_path / "candles.sqlite3"
    repository = SQLiteCandleRepository(database_path)
    repository.initialize()
    repository.upsert(make_candle(100, mapping_verified=False))

    restored = repository.load_all()
    with sqlite3.connect(database_path) as connection:
        dumped = "\n".join(connection.iterdump()).lower()

    assert restored[0].symbol is None
    assert restored[0].timeframe is None
    assert restored[0].mapping_verified is False
    for forbidden in ["token", "cookie", "authorization", "bearer", "ssid", "password", "headers", "har", "payload", "request_id"]:
        assert forbidden not in dumped


def test_chart_api_returns_restored_candles_and_bridge_pipeline_continues_after_restore() -> None:
    market_candle_persistence.cleanup(market_candle_store)
    market_pipeline.process(make_message(100))
    market_candle_store.clear()

    market_candle_persistence.restore_into_store(market_candle_store)
    restored_response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10})
    market_pipeline.process(make_message(160, close=1.3))
    updated_response = client.get("/api/v1/market/chart", params={"active_id": 76, "raw_size": 60, "limit": 10})

    assert restored_response.status_code == 200
    assert restored_response.json()["count"] == 1
    assert restored_response.json()["candles"][0]["time"] == 100
    assert updated_response.json()["count"] == 2
    assert [item["time"] for item in updated_response.json()["candles"]] == [100, 160]


def test_persistence_status_and_controlled_cleanup_endpoint_are_sanitized() -> None:
    market_candle_persistence.cleanup(market_candle_store)
    market_pipeline.process(make_message(100))

    missing_confirmation = client.delete("/api/v1/market/persistence/candles")
    status_response = client.get("/api/v1/market/persistence/status")
    cleanup_response = client.delete("/api/v1/market/persistence/candles", params={"confirm": "true"})

    assert missing_confirmation.status_code == 400
    assert status_response.status_code == 200
    status = status_response.json()["market_persistence"]
    assert status["enabled"] is True
    assert status["database_path_sanitized"] == ".jarvis_cache/market/candles.sqlite3"
    assert "/Users/" not in str(status)
    assert cleanup_response.status_code == 200
    assert cleanup_response.json()["removed_candles_count"] >= 1
    assert market_candle_store.series_keys() == ()


def test_cleanup_endpoint_is_blocked_in_production(monkeypatch) -> None:
    monkeypatch.setattr(settings, "environment", "production")

    response = client.delete("/api/v1/market/persistence/candles", params={"confirm": "true"})

    assert response.status_code == 403


def test_sqlite_database_path_is_inside_ignored_jarvis_cache() -> None:
    path = ".jarvis_cache/market/candles.sqlite3"
    result = subprocess.run(["git", "check-ignore", path], cwd="/Users/renangodoy/Desktop/jarvis-ai-trader", text=True, capture_output=True)

    assert result.returncode == 0
    assert result.stdout.strip() == path
