from __future__ import annotations

from datetime import datetime, timezone

from app.market.events.models import NormalizedMarketCandle
from app.market.persistence.models import MarketPersistenceStatus, PersistenceCleanupResult
from app.market.persistence.repository import CandlePersistenceRepository
from app.market.store import CandleStore
from app.market.store.types import CandleStoreWriteResult


class CandlePersistenceService:
    """Coordinates local normalized candle persistence with the shared CandleStore."""

    def __init__(self, repository: CandlePersistenceRepository, retention_per_series: int = 1000, enabled: bool = True) -> None:
        if retention_per_series <= 0:
            raise ValueError("retention_per_series must be greater than zero")
        self._repository = repository
        self._retention_per_series = retention_per_series
        self._enabled = enabled
        self._database_ready = False
        self._restored_series_count = 0
        self._restored_candles_count = 0
        self._last_write_at: str | None = None
        self._last_restore_at: str | None = None
        self._last_cleanup_at: str | None = None
        self._last_error_code: str | None = None

    def initialize(self) -> None:
        if not self._enabled:
            return
        try:
            self._repository.initialize()
            self._database_ready = True
            self._last_error_code = None
        except Exception:
            self._database_ready = False
            self._last_error_code = "SQLITE_INITIALIZE_FAILED"

    def restore_into_store(self, candle_store: CandleStore) -> tuple[CandleStoreWriteResult, ...]:
        if not self._enabled:
            return ()
        self.initialize()
        if not self._database_ready:
            return ()
        try:
            previous_observer = candle_store.write_observer
            candle_store.set_write_observer(None)
            candles = self._repository.load_all()
            results = candle_store.add_many(candles)
            candle_store.set_write_observer(previous_observer)
            self._restored_candles_count = sum(1 for result in results if result.status in {"added", "updated", "ignored"})
            self._restored_series_count = len(candle_store.series_keys())
            self._last_restore_at = _utcnow_iso()
            self._last_error_code = None
            return results
        except Exception:
            candle_store.set_write_observer(previous_observer)
            self._last_error_code = "SQLITE_RESTORE_FAILED"
            return ()

    def persist_write(self, candle: NormalizedMarketCandle, result: CandleStoreWriteResult) -> None:
        if not self._enabled or result.status == "rejected":
            return
        self.initialize()
        if not self._database_ready:
            return
        try:
            self._repository.upsert(candle)
            self._repository.prune_retention_by_series_key(_series_key_for(candle), self._retention_per_series)
            self._last_write_at = _utcnow_iso()
            self._last_error_code = None
        except Exception:
            self._last_error_code = "SQLITE_WRITE_FAILED"

    def cleanup(self, candle_store: CandleStore) -> PersistenceCleanupResult:
        self.initialize()
        if not self._database_ready:
            self._last_error_code = "SQLITE_NOT_READY"
            return PersistenceCleanupResult(removed_candles_count=0, removed_series_count=0)
        try:
            result = self._repository.clear()
            candle_store.clear()
            self._last_cleanup_at = _utcnow_iso()
            self._last_error_code = None
            return result
        except Exception:
            self._last_error_code = "SQLITE_CLEANUP_FAILED"
            return PersistenceCleanupResult(removed_candles_count=0, removed_series_count=0)

    def status(self) -> MarketPersistenceStatus:
        persisted_candles_count = 0
        persisted_series_count = 0
        if self._enabled and self._database_ready:
            try:
                persisted_candles_count = self._repository.count_candles()
                persisted_series_count = self._repository.count_series()
            except Exception:
                self._last_error_code = "SQLITE_STATUS_FAILED"
        return MarketPersistenceStatus(
            enabled=self._enabled,
            database_ready=self._database_ready,
            restored_series_count=self._restored_series_count,
            restored_candles_count=self._restored_candles_count,
            persisted_series_count=persisted_series_count,
            persisted_candles_count=persisted_candles_count,
            last_write_at=self._last_write_at,
            last_restore_at=self._last_restore_at,
            last_cleanup_at=self._last_cleanup_at,
            retention_per_series=self._retention_per_series,
            database_path_sanitized=self._repository.sanitized_path(),
            last_error_code=self._last_error_code,
        )


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _series_key_for(candle: NormalizedMarketCandle) -> str:
    provider = "IQ_OPTION" if candle.source == "iq_option" else "POLARIUM"
    if candle.active_id is not None:
        return f"{provider}:active:{candle.active_id}:raw:{candle.raw_size}"
    if candle.symbol:
        return f"{provider}:symbol:{candle.symbol}:raw:{candle.raw_size}"
    raise ValueError("Cannot build persistence series key without active_id or symbol.")
