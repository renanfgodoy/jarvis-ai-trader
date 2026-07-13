from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketPersistenceStatus:
    enabled: bool
    database_ready: bool
    restored_series_count: int = 0
    restored_candles_count: int = 0
    persisted_series_count: int = 0
    persisted_candles_count: int = 0
    last_write_at: str | None = None
    last_restore_at: str | None = None
    last_cleanup_at: str | None = None
    retention_per_series: int = 1000
    database_path_sanitized: str = ".jarvis_cache/market/candles.sqlite3"
    last_error_code: str | None = None

    def sanitized(self) -> dict:
        return {
            "enabled": self.enabled,
            "database_ready": self.database_ready,
            "restored_series_count": self.restored_series_count,
            "restored_candles_count": self.restored_candles_count,
            "persisted_series_count": self.persisted_series_count,
            "persisted_candles_count": self.persisted_candles_count,
            "last_write_at": self.last_write_at,
            "last_restore_at": self.last_restore_at,
            "last_cleanup_at": self.last_cleanup_at,
            "retention_per_series": self.retention_per_series,
            "database_path_sanitized": self.database_path_sanitized,
            "last_error_code": self.last_error_code,
        }


@dataclass(frozen=True)
class PersistenceWriteResult:
    status: str
    active_id: int
    raw_size: int
    start_timestamp: int


@dataclass(frozen=True)
class PersistenceCleanupResult:
    removed_candles_count: int
    removed_series_count: int
