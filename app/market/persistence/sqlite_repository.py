from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.market.events.models import NormalizedMarketCandle
from app.market.persistence.models import PersistenceCleanupResult, PersistenceWriteResult

SCHEMA_VERSION = 2
DEFAULT_DATABASE_PATH = Path(".jarvis_cache/market/candles.sqlite3")


class SQLiteCandleRepository:
    """SQLite repository for normalized candles only."""

    def __init__(self, database_path: Path | str = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER NOT NULL
                )
                """
            )
            current_version = connection.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
            if current_version is None:
                connection.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
            _migrate_schema(connection)
            _ensure_v2_schema(connection)
            connection.execute("UPDATE schema_version SET version = ?", (SCHEMA_VERSION,))
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_market_candles_series_timestamp
                ON market_candles (provider, symbol, active_id, raw_size, start_timestamp)
                """
            )

    def upsert(self, candle: NormalizedMarketCandle) -> PersistenceWriteResult:
        series_key = _series_key_for(candle)
        now = _sqlite_now()
        with self._connect() as connection:
            existing = connection.execute(
                """
                SELECT provider, symbol, active_id, end_timestamp, open, close, low_candidate, high_candidate, volume, mapping_verified
                FROM market_candles
                WHERE series_key = ? AND start_timestamp = ?
                """,
                (series_key, candle.start_timestamp),
            ).fetchone()
            provider = _provider_for(candle)
            values = (
                provider,
                candle.symbol,
                candle.active_id,
                candle.end_timestamp,
                candle.open,
                candle.close,
                candle.low_candidate,
                candle.high_candidate,
                candle.volume,
                1 if candle.mapping_verified else 0,
            )
            if existing is not None and tuple(existing) == values:
                return PersistenceWriteResult(
                    status="ignored",
                    active_id=candle.active_id,
                    raw_size=candle.raw_size,
                    start_timestamp=candle.start_timestamp,
                )
            if existing is None:
                connection.execute(
                    """
                    INSERT INTO market_candles (
                        series_key, provider, symbol, active_id, raw_size, start_timestamp, end_timestamp,
                        open, close, low_candidate, high_candidate, volume,
                        mapping_verified, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        series_key,
                        provider,
                        candle.symbol,
                        candle.active_id,
                        candle.raw_size,
                        candle.start_timestamp,
                        candle.end_timestamp,
                        candle.open,
                        candle.close,
                        candle.low_candidate,
                        candle.high_candidate,
                        candle.volume,
                        1 if candle.mapping_verified else 0,
                        now,
                        now,
                    ),
                )
                status = "inserted"
            else:
                connection.execute(
                    """
                    UPDATE market_candles
                    SET provider = ?,
                        symbol = ?,
                        active_id = ?,
                        end_timestamp = ?,
                        open = ?,
                        close = ?,
                        low_candidate = ?,
                        high_candidate = ?,
                        volume = ?,
                        mapping_verified = ?,
                        updated_at = ?
                    WHERE series_key = ? AND start_timestamp = ?
                    """,
                    (
                        provider,
                        candle.symbol,
                        candle.active_id,
                        candle.end_timestamp,
                        candle.open,
                        candle.close,
                        candle.low_candidate,
                        candle.high_candidate,
                        candle.volume,
                        1 if candle.mapping_verified else 0,
                        now,
                        series_key,
                        candle.start_timestamp,
                    ),
                )
                status = "updated"
            return PersistenceWriteResult(
                status=status,
                active_id=candle.active_id,
                raw_size=candle.raw_size,
                start_timestamp=candle.start_timestamp,
            )

    def load_all(self) -> tuple[NormalizedMarketCandle, ...]:
        if not self.database_path.exists():
            return ()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT provider, symbol, active_id, raw_size, start_timestamp, end_timestamp,
                       open, close, low_candidate, high_candidate, volume, mapping_verified
                FROM market_candles
                ORDER BY provider, symbol, active_id, raw_size, start_timestamp
                """
            ).fetchall()
        return tuple(_row_to_candle(row) for row in rows)

    def prune_retention(self, active_id: int, raw_size: int, limit: int) -> int:
        return self.prune_retention_by_series_key(_series_key("POLARIUM", None, active_id, raw_size), limit)

    def prune_retention_by_series_key(self, series_key: str, limit: int) -> int:
        if limit <= 0:
            raise ValueError("Retention limit must be greater than zero.")
        with self._connect() as connection:
            removed = connection.execute(
                """
                DELETE FROM market_candles
                WHERE series_key = ?
                  AND start_timestamp NOT IN (
                      SELECT start_timestamp
                      FROM market_candles
                      WHERE series_key = ?
                      ORDER BY start_timestamp DESC
                      LIMIT ?
                  )
                """,
                (series_key, series_key, limit),
            ).rowcount
        return int(removed or 0)

    def clear(self) -> PersistenceCleanupResult:
        removed_candles = self.count_candles()
        removed_series = self.count_series()
        self.initialize()
        with self._connect() as connection:
            connection.execute("DELETE FROM market_candles")
        return PersistenceCleanupResult(removed_candles_count=removed_candles, removed_series_count=removed_series)

    def count_candles(self) -> int:
        if not self.database_path.exists():
            return 0
        with self._connect() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM market_candles").fetchone()[0])

    def count_series(self) -> int:
        if not self.database_path.exists():
            return 0
        with self._connect() as connection:
            return int(
                connection.execute("SELECT COUNT(*) FROM (SELECT series_key FROM market_candles GROUP BY series_key)").fetchone()[0]
            )

    def sanitized_path(self) -> str:
        parts = self.database_path.parts
        if ".jarvis_cache" in parts:
            index = parts.index(".jarvis_cache")
            return str(Path(*parts[index:]))
        return ".jarvis_cache/market/candles.sqlite3"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection


def _row_to_candle(row: tuple) -> NormalizedMarketCandle:
    provider = str(row[0])
    return NormalizedMarketCandle(
        active_id=int(row[2]) if row[2] is not None else None,
        symbol=str(row[1]) if row[1] else None,
        raw_size=int(row[3]),
        timeframe=None,
        start_timestamp=int(row[4]),
        end_timestamp=int(row[5]),
        open=float(row[6]),
        close=float(row[7]),
        low_candidate=float(row[8]),
        high_candidate=float(row[9]),
        volume=float(row[10] or 0),
        source="iq_option" if provider == "IQ_OPTION" else "polarium",
        source_event="local-persistence",
        source_verified=True,
        mapping_verified=bool(row[11]),
        mapping_notes=("restored from local normalized candle persistence",),
    )


def _migrate_schema(connection: sqlite3.Connection) -> None:
    table = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'market_candles'").fetchone()
    if table is None:
        return
    columns = {row[1] for row in connection.execute("PRAGMA table_info(market_candles)").fetchall()}
    if "series_key" in columns and "provider" in columns:
        return
    legacy_name = "market_candles_legacy_v1"
    if connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", (legacy_name,)).fetchone() is None:
        connection.execute(f"ALTER TABLE market_candles RENAME TO {legacy_name}")
    else:
        connection.execute("ALTER TABLE market_candles RENAME TO market_candles_legacy_v1_duplicate")
    _ensure_v2_schema(connection)
    legacy_columns = {row[1] for row in connection.execute(f"PRAGMA table_info({legacy_name})").fetchall()}
    symbol_expr = "symbol" if "symbol" in legacy_columns else "NULL"
    connection.execute(
        f"""
        INSERT OR IGNORE INTO market_candles (
            series_key, provider, symbol, active_id, raw_size, start_timestamp, end_timestamp,
            open, close, low_candidate, high_candidate, volume, mapping_verified, created_at, updated_at
        )
        SELECT
            'POLARIUM:active:' || active_id || ':raw:' || raw_size,
            'POLARIUM',
            {symbol_expr},
            active_id,
            raw_size,
            start_timestamp,
            end_timestamp,
            open,
            close,
            low_candidate,
            high_candidate,
            volume,
            mapping_verified,
            created_at,
            updated_at
        FROM {legacy_name}
        """
    )


def _ensure_v2_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS market_candles (
            series_key TEXT NOT NULL,
            provider TEXT NOT NULL,
            symbol TEXT,
            active_id INTEGER,
            raw_size INTEGER NOT NULL,
            start_timestamp INTEGER NOT NULL,
            end_timestamp INTEGER,
            open REAL NOT NULL,
            close REAL NOT NULL,
            low_candidate REAL NOT NULL,
            high_candidate REAL NOT NULL,
            volume REAL,
            mapping_verified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (series_key, start_timestamp)
        )
        """
    )


def _provider_for(candle: NormalizedMarketCandle) -> str:
    return "IQ_OPTION" if candle.source == "iq_option" else "POLARIUM"


def _series_key_for(candle: NormalizedMarketCandle) -> str:
    provider = _provider_for(candle)
    if candle.active_id is not None:
        return _series_key(provider, candle.symbol, candle.active_id, candle.raw_size)
    if candle.symbol:
        return _series_key(provider, candle.symbol, None, candle.raw_size)
    raise ValueError("Cannot persist candle without active_id or symbol.")


def _series_key(provider: str, symbol: str | None, active_id: int | None, raw_size: int) -> str:
    if active_id is not None:
        return f"{provider}:active:{active_id}:raw:{raw_size}"
    if symbol:
        return f"{provider}:symbol:{symbol}:raw:{raw_size}"
    raise ValueError("Cannot build series key without active_id or symbol.")


def _sqlite_now() -> str:
    return datetime.now(timezone.utc).isoformat()
