from __future__ import annotations

import inspect
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from app.market.providers.polarium.readiness import HISTORY_EVENTS
from app.market.store.types import CandleSeriesKey, CandleStoreWriteResult

HistoryCountCategory = Literal[
    "STORE_KEY_MISMATCH",
    "STORE_BUCKET_MISMATCH",
    "MERGE_FAILED",
    "MERGE_SKIPPED",
    "MERGE_REPLACED",
    "HISTORY_NOT_INCREMENTED",
    "READINESS_NOT_UPDATED",
    "DUPLICATE_FILTER",
    "UNKNOWN",
]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "history_count_report.json"
REPORT_TXT = REPORT_DIR / "history_count_report.txt"


@dataclass
class HistoryCountRecord:
    event_name: str | None
    active_id: int | None
    symbol: str | None
    raw_size: int | None
    store_key: dict[str, Any] | None
    bucket: str
    history_before: int
    history_after: int
    bucket_before: int
    bucket_after: int
    merge_type: str
    append_count: int
    replace_count: int
    ignored_count: int
    deduplicated_count: int
    readiness_before: str | None
    readiness_after: str | None
    readiness_count_before: int | None
    readiness_count_after: int | None
    history_source: str
    caller: str
    failure_reason: str | None
    category: HistoryCountCategory
    observed_at: int | None = None
    stack: list[str] = field(default_factory=list)

    def sanitized(self) -> dict[str, Any]:
        return asdict(self)


class HistoryCountDiagnostic:
    """Audits the gap between CandleStore writes and Polarium history_count."""

    def __init__(
        self,
        *,
        report_json: Path | str = REPORT_JSON,
        report_txt: Path | str = REPORT_TXT,
        auto_write: bool = True,
    ) -> None:
        self._report_json = Path(report_json)
        self._report_txt = Path(report_txt)
        self._auto_write = auto_write
        self._records: list[HistoryCountRecord] = []

    @property
    def records(self) -> tuple[HistoryCountRecord, ...]:
        return tuple(self._records)

    def observe_history_event(
        self,
        *,
        event: Any,
        store_results: tuple[CandleStoreWriteResult, ...],
        bucket_before: dict[tuple[int, int], int],
        bucket_after: dict[tuple[int, int], int],
        history_before: dict[tuple[int, int], int],
        history_after: dict[tuple[int, int], int],
        readiness_before: dict[tuple[int, int], dict[str, Any]],
        readiness_after: dict[tuple[int, int], dict[str, Any]],
        now_ms: int,
        caller: str = "PolariumMarketFeedRuntime.process_message",
    ) -> None:
        if getattr(event, "event_name", None) not in HISTORY_EVENTS:
            return
        result_by_key = _results_by_context(store_results)
        for candle in getattr(event, "candles", ()):
            context = (candle.active_id, candle.raw_size)
            results = result_by_key.get(context, ())
            if not results:
                results = tuple(item for item in store_results if _result_active_id(item) == candle.active_id or _result_raw_size(item) == candle.raw_size)
            record = HistoryCountRecord(
                event_name=getattr(event, "event_name", None),
                active_id=candle.active_id,
                symbol=candle.symbol,
                raw_size=candle.raw_size,
                store_key=_store_key(results[0].key) if results else None,
                bucket=_bucket_label(candle.active_id, candle.raw_size),
                history_before=history_before.get(context, 0),
                history_after=history_after.get(context, 0),
                bucket_before=bucket_before.get(context, 0),
                bucket_after=bucket_after.get(context, 0),
                merge_type=_merge_type(results),
                append_count=_count(results, "added"),
                replace_count=_count(results, "updated"),
                ignored_count=_count(results, "ignored"),
                deduplicated_count=_count(results, "ignored"),
                readiness_before=_readiness_state(readiness_before.get(context)),
                readiness_after=_readiness_state(readiness_after.get(context)),
                readiness_count_before=_readiness_count(readiness_before.get(context)),
                readiness_count_after=_readiness_count(readiness_after.get(context)),
                history_source="_history_timestamps",
                caller=caller,
                failure_reason=_failure_reason(results),
                category="UNKNOWN",
                observed_at=now_ms,
                stack=_stack_summary(),
            )
            record.category = _classify(record, results)
            self._records.append(record)
        self._write_if_enabled()

    def write_reports(self) -> None:
        self._report_json.parent.mkdir(parents=True, exist_ok=True)
        payload = self.sanitized()
        self._report_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._report_txt.write_text(_render_text(payload), encoding="utf-8")

    def sanitized(self) -> dict[str, Any]:
        records = [record.sanitized() for record in self._records]
        categories = Counter(record["category"] for record in records)
        return {
            "summary": {
                "total_records": len(records),
                "categories": dict(sorted(categories.items())),
            },
            "records": records,
        }

    def _write_if_enabled(self) -> None:
        if self._auto_write:
            self.write_reports()


def _classify(record: HistoryCountRecord, results: tuple[CandleStoreWriteResult, ...]) -> HistoryCountCategory:
    if not results:
        return "MERGE_FAILED"
    if any(item.status == "rejected" for item in results):
        return "MERGE_FAILED"
    if any(_result_active_id(item) not in {None, record.active_id} or _result_raw_size(item) not in {None, record.raw_size} for item in results):
        return "STORE_KEY_MISMATCH"
    expected_bucket_after = record.bucket_before + record.append_count
    if record.bucket_after < expected_bucket_after:
        return "STORE_BUCKET_MISMATCH"
    if record.ignored_count > 0 and record.append_count == 0 and record.replace_count == 0:
        return "DUPLICATE_FILTER"
    if record.replace_count > 0 and record.append_count == 0:
        return "MERGE_REPLACED"
    if record.append_count == 0 and record.replace_count == 0 and record.ignored_count == 0:
        return "MERGE_SKIPPED"
    if record.append_count > 0 and record.history_after == record.history_before:
        return "HISTORY_NOT_INCREMENTED"
    if record.history_after > record.history_before and record.readiness_count_after == record.readiness_count_before:
        return "READINESS_NOT_UPDATED"
    return "UNKNOWN"


def _results_by_context(results: tuple[CandleStoreWriteResult, ...]) -> dict[tuple[int, int], tuple[CandleStoreWriteResult, ...]]:
    grouped: dict[tuple[int, int], list[CandleStoreWriteResult]] = {}
    for item in results:
        active_id = _result_active_id(item)
        raw_size = _result_raw_size(item)
        if active_id is None or raw_size is None:
            continue
        grouped.setdefault((active_id, raw_size), []).append(item)
    return {key: tuple(value) for key, value in grouped.items()}


def _count(results: tuple[CandleStoreWriteResult, ...], status: str) -> int:
    return sum(1 for item in results if item.status == status)


def _merge_type(results: tuple[CandleStoreWriteResult, ...]) -> str:
    if not results:
        return "missing_result"
    statuses = {item.status for item in results}
    if "rejected" in statuses:
        return "rejected"
    if statuses == {"added"}:
        return "append"
    if statuses == {"updated"}:
        return "replace"
    if statuses == {"ignored"}:
        return "ignored"
    return "+".join(sorted(statuses))


def _failure_reason(results: tuple[CandleStoreWriteResult, ...]) -> str | None:
    reasons = [item.reason for item in results if item.reason]
    if not reasons:
        return None
    sanitized = []
    for reason in reasons:
        lowered = reason.lower()
        if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password", "secret")):
            sanitized.append("SANITIZED_REASON")
        else:
            sanitized.append(reason[:160])
    return " | ".join(sanitized)


def _store_key(key: CandleSeriesKey | None) -> dict[str, Any] | None:
    if key is None:
        return None
    return {
        "provider": key.provider,
        "active_id": key.active_id,
        "symbol": key.symbol,
        "raw_size": key.raw_size,
    }


def _result_active_id(result: CandleStoreWriteResult) -> int | None:
    return result.key.active_id if result.key else None


def _result_raw_size(result: CandleStoreWriteResult) -> int | None:
    return result.key.raw_size if result.key else None


def _bucket_label(active_id: int | None, raw_size: int | None) -> str:
    return f"POLARIUM:{active_id}:{raw_size}"


def _readiness_state(snapshot: dict[str, Any] | None) -> str | None:
    value = (snapshot or {}).get("state")
    return value if isinstance(value, str) else None


def _readiness_count(snapshot: dict[str, Any] | None) -> int | None:
    value = (snapshot or {}).get("history_count")
    return value if isinstance(value, int) else None


def _stack_summary() -> list[str]:
    frames = []
    for frame in inspect.stack()[2:7]:
        filename = Path(frame.filename).name
        frames.append(f"{filename}:{frame.function}")
    return frames


def _render_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - History Count Diagnostic", ""]
    summary = payload.get("summary", {})
    lines.append(f"total_records: {summary.get('total_records', 0)}")
    lines.append(f"categories: {summary.get('categories', {})}")
    lines.append("")
    for record in payload.get("records", []):
        label = record.get("symbol") or f"active_id={record.get('active_id')}"
        lines.append(f"- {label} raw_size={record.get('raw_size')} bucket={record.get('bucket')}")
        lines.append(f"  category: {record.get('category')}")
        lines.append(f"  merge_type: {record.get('merge_type')}")
        lines.append(f"  store_key: {record.get('store_key')}")
        lines.append(f"  bucket_size: {record.get('bucket_before')} -> {record.get('bucket_after')}")
        lines.append(f"  history_count: {record.get('history_before')} -> {record.get('history_after')}")
        lines.append(f"  readiness: {record.get('readiness_before')} -> {record.get('readiness_after')}")
        lines.append(f"  readiness_count: {record.get('readiness_count_before')} -> {record.get('readiness_count_after')}")
        lines.append(
            "  writes: "
            f"append={record.get('append_count')} replace={record.get('replace_count')} "
            f"ignored={record.get('ignored_count')} deduplicated={record.get('deduplicated_count')}"
        )
        if record.get("failure_reason"):
            lines.append(f"  failure_reason: {record.get('failure_reason')}")
    lines.append("")
    return "\n".join(lines)
