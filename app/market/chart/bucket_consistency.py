from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Literal

from app.market.store.types import CandleSeriesKey

ChartBucketConsistencyEvent = Literal[
    "CHART_REQUEST_RECEIVED",
    "CHART_STORE_KEY_RESOLVED",
    "CHART_BUCKET_FOUND",
    "CHART_BUCKET_MISSING",
    "CHART_RESPONSE_CREATED",
]

REPORT_JSON_PATH = Path(".jarvis_cache/diagnostics/chart_bucket_consistency.json")
REPORT_TEXT_PATH = Path(".jarvis_cache/diagnostics/chart_bucket_consistency.txt")
MAX_RECORDS = 500


@dataclass(frozen=True)
class ChartBucketConsistencyRecord:
    timestamp: str
    event: ChartBucketConsistencyEvent
    active_id_requested: int | None
    raw_size_requested: int | None
    store_key: str | None
    bucket_exists: bool | None
    bucket_count: int | None
    response_active_id: int | None
    response_raw_size: int | None
    response_count: int | None
    first_timestamp: int | None
    last_timestamp: int | None


class ChartBucketConsistencyDiagnostic:
    """Sanitized read-only audit trail for Chart API to CandleStore lookups."""

    def __init__(
        self,
        json_path: Path = REPORT_JSON_PATH,
        text_path: Path = REPORT_TEXT_PATH,
        max_records: int = MAX_RECORDS,
    ) -> None:
        self._json_path = json_path
        self._text_path = text_path
        self._max_records = max_records
        self._records: list[ChartBucketConsistencyRecord] = []
        self._lock = Lock()

    def observe(
        self,
        event: ChartBucketConsistencyEvent,
        *,
        active_id_requested: int | None = None,
        raw_size_requested: int | None = None,
        store_key: CandleSeriesKey | str | None = None,
        bucket_exists: bool | None = None,
        bucket_count: int | None = None,
        response_active_id: int | None = None,
        response_raw_size: int | None = None,
        response_count: int | None = None,
        first_timestamp: int | None = None,
        last_timestamp: int | None = None,
    ) -> None:
        record = ChartBucketConsistencyRecord(
            timestamp=datetime.now(UTC).isoformat(),
            event=event,
            active_id_requested=active_id_requested,
            raw_size_requested=raw_size_requested,
            store_key=format_store_key(store_key),
            bucket_exists=bucket_exists,
            bucket_count=bucket_count,
            response_active_id=response_active_id,
            response_raw_size=response_raw_size,
            response_count=response_count,
            first_timestamp=first_timestamp,
            last_timestamp=last_timestamp,
        )
        with self._lock:
            self._records.append(record)
            self._records = self._records[-self._max_records :]
            self._write_reports()

    def records(self) -> tuple[ChartBucketConsistencyRecord, ...]:
        with self._lock:
            return tuple(self._records)

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._write_reports()

    def _write_reports(self) -> None:
        payload = [asdict(record) for record in self._records]
        self._json_path.parent.mkdir(parents=True, exist_ok=True)
        self._json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._text_path.write_text("\n".join(_format_text_record(record) for record in self._records), encoding="utf-8")


def format_store_key(store_key: CandleSeriesKey | str | None) -> str | None:
    if store_key is None:
        return None
    if isinstance(store_key, str):
        return store_key
    provider = store_key.provider
    identifier = store_key.active_id if store_key.active_id is not None else store_key.symbol
    return f"{provider}:{identifier}:{store_key.raw_size}"


def candle_bounds(candles: tuple[object, ...]) -> tuple[int | None, int | None]:
    if not candles:
        return None, None
    first_timestamp = getattr(candles[0], "start_timestamp", getattr(candles[0], "time", None))
    last_timestamp = getattr(candles[-1], "start_timestamp", getattr(candles[-1], "time", None))
    return _safe_int(first_timestamp), _safe_int(last_timestamp)


def _safe_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


def _format_text_record(record: ChartBucketConsistencyRecord) -> str:
    return (
        f"{record.timestamp} {record.event} "
        f"requested={record.active_id_requested}/{record.raw_size_requested} "
        f"store_key={record.store_key} bucket_exists={record.bucket_exists} "
        f"bucket_count={record.bucket_count} "
        f"response={record.response_active_id}/{record.response_raw_size} "
        f"response_count={record.response_count} "
        f"first={record.first_timestamp} last={record.last_timestamp}"
    )
