from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

AssetSwitchCategory = Literal[
    "ASSET_NOT_SWITCHED",
    "SESSION_CONTEXT_STALE",
    "BOOTSTRAP_NOT_STARTED",
    "BOOTSTRAP_TIMEOUT",
    "BOOTSTRAP_DISCARDED",
    "BUCKET_NOT_UPDATED",
    "CHART_NOT_UPDATED",
    "FRONTEND_STALE",
    "RACE_CONDITION",
    "UNKNOWN",
]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "asset_switch_report.json"
REPORT_TXT = REPORT_DIR / "asset_switch_report.txt"


@dataclass
class AssetSwitchRecord:
    selection_id: str
    active_id_before: int | None
    active_id_after: int | None
    symbol_before: str | None
    symbol_after: str | None
    raw_size_before: int | None
    raw_size_after: int | None
    bucket_before: str | None
    bucket_after: str | None
    bucket_size_before: int
    bucket_size_after: int
    request_started: bool = False
    request_finished: bool = False
    request_cancelled: bool = False
    request_discarded: bool = False
    response_ignored: bool = False
    response_applied: bool = False
    chart_source_before: str | None = None
    chart_source_after: str | None = None
    chart_updated: bool = False
    frontend_updated: bool = False
    selected_at: int | None = None
    bootstrap_started_at: int | None = None
    bootstrap_finished_at: int | None = None
    chart_updated_at: int | None = None
    failure_step: str = "UNKNOWN"
    failure_reason: str | None = None
    category: AssetSwitchCategory = "UNKNOWN"

    def sanitized(self) -> dict[str, Any]:
        return asdict(self)


class AssetSwitchDiagnostic:
    """Audits visible Polarium asset/timeframe switch lifecycle."""

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
        self._records: list[AssetSwitchRecord] = []
        self._current_selection_id: str | None = None
        self._sequence = 0

    @property
    def records(self) -> tuple[AssetSwitchRecord, ...]:
        return tuple(self._records)

    def observe_selection(
        self,
        *,
        previous_context: dict[str, Any] | None,
        current_context: dict[str, Any] | None,
        bucket_size_before: int,
        bucket_size_after: int,
        now_ms: int,
    ) -> None:
        previous_active = _active_id(previous_context)
        current_active = _active_id(current_context)
        previous_raw_size = _raw_size(previous_context)
        current_raw_size = _raw_size(current_context)
        self._sequence += 1
        selection_id = f"selection-{self._sequence}-{current_active}-{current_raw_size}-{now_ms}"
        self._current_selection_id = selection_id
        record = AssetSwitchRecord(
            selection_id=selection_id,
            active_id_before=previous_active,
            active_id_after=current_active,
            symbol_before=_symbol(previous_context),
            symbol_after=_symbol(current_context),
            raw_size_before=previous_raw_size,
            raw_size_after=current_raw_size,
            bucket_before=_bucket(previous_active, previous_raw_size),
            bucket_after=_bucket(current_active, current_raw_size),
            bucket_size_before=bucket_size_before,
            bucket_size_after=bucket_size_after,
            chart_source_before=_bucket(previous_active, previous_raw_size),
            chart_source_after=None,
            selected_at=now_ms,
        )
        if previous_active == current_active and previous_raw_size == current_raw_size:
            record.category = "ASSET_NOT_SWITCHED"
            record.failure_step = "SESSION_CONTEXT"
            record.failure_reason = "Visible context did not change."
        else:
            record.category = "BOOTSTRAP_NOT_STARTED"
            record.failure_step = "BOOTSTRAP_REQUEST"
            record.failure_reason = "Waiting for get-first-candles request."
        self._records.append(record)
        self._write_if_enabled()

    def observe_bootstrap_started(self, *, active_id: int | None, raw_size: int | None, now_ms: int) -> None:
        record = self._find_current(active_id=active_id, raw_size=raw_size)
        if record is None:
            return
        record.request_started = True
        record.bootstrap_started_at = now_ms
        record.category = "CHART_NOT_UPDATED"
        record.failure_step = "CHART_API"
        record.failure_reason = "Bootstrap started; waiting for chart source update."
        self._write_if_enabled()

    def observe_bootstrap_finished(
        self,
        *,
        active_id: int | None,
        raw_size: int | None,
        symbol: str | None,
        visible_active_id: int | None,
        visible_raw_size: int | None,
        bucket_size_before: int,
        bucket_size_after: int,
        history_count: int,
        readiness_state: str | None,
        now_ms: int,
    ) -> None:
        record = self._find_current(active_id=active_id, raw_size=raw_size)
        if record is None:
            record = self._find_latest()
        if record is None:
            return
        record.request_finished = True
        record.bootstrap_finished_at = now_ms
        record.symbol_after = record.symbol_after or _safe_string(symbol)
        record.bucket_size_before = bucket_size_before
        record.bucket_size_after = bucket_size_after
        if active_id != visible_active_id or raw_size != visible_raw_size:
            record.response_ignored = True
            record.request_discarded = True
            record.category = "BOOTSTRAP_DISCARDED"
            record.failure_step = "BOOTSTRAP_RESPONSE"
            record.failure_reason = "Historical response was discarded because the visible context changed."
        elif bucket_size_after <= 0 or history_count <= 0:
            record.category = "BUCKET_NOT_UPDATED"
            record.failure_step = "CANDLE_BUCKET"
            record.failure_reason = f"Bucket did not grow for readiness={readiness_state or 'UNKNOWN'}."
        elif bucket_size_after <= bucket_size_before and readiness_state == "READY":
            if record.chart_updated and record.frontend_updated:
                record.response_applied = True
                record.category = "UNKNOWN"
                record.failure_step = "NO_DIVERGENCE_CLASSIFIED"
                record.failure_reason = None
            elif record.category != "FRONTEND_STALE":
                record.response_applied = True
                record.category = "CHART_NOT_UPDATED"
                record.failure_step = "CHART_API"
                record.failure_reason = "Ready bucket exists; waiting for chart request."
        else:
            record.response_applied = True
            record.category = "CHART_NOT_UPDATED"
            record.failure_step = "CHART_API"
            record.failure_reason = "Backend bucket is ready; waiting for chart request."
        self._write_if_enabled()

    def observe_chart_request(self, *, active_id: int | None, raw_size: int | None, symbol: str | None, candle_count: int, now_ms: int) -> None:
        record = self._find_latest()
        if record is None:
            return
        requested_bucket = _bucket(active_id, raw_size)
        record.chart_source_after = requested_bucket
        record.chart_updated_at = now_ms
        if active_id == record.active_id_after and raw_size == record.raw_size_after:
            record.chart_updated = candle_count > 0
            record.frontend_updated = candle_count > 0
            record.bucket_size_after = max(record.bucket_size_after, candle_count)
            if candle_count > 0:
                record.category = "UNKNOWN"
                record.failure_step = "NO_DIVERGENCE_CLASSIFIED"
                record.failure_reason = None
            else:
                record.category = "CHART_NOT_UPDATED"
                record.failure_step = "CHART_API"
                record.failure_reason = "Chart API returned zero candles for selected context."
            if symbol:
                record.symbol_after = _safe_string(symbol)
        else:
            record.chart_updated = candle_count > 0
            record.frontend_updated = False
            record.category = "FRONTEND_STALE"
            record.failure_step = "FRONTEND_CONTEXT"
            record.failure_reason = "Chart request did not match latest visible selection."
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
                "total_switches": len(records),
                "categories": dict(sorted(categories.items())),
            },
            "records": records,
        }

    def _find_current(self, *, active_id: int | None, raw_size: int | None) -> AssetSwitchRecord | None:
        for record in reversed(self._records):
            if record.active_id_after == active_id and record.raw_size_after == raw_size:
                return record
        return None

    def _find_latest(self) -> AssetSwitchRecord | None:
        return self._records[-1] if self._records else None

    def _write_if_enabled(self) -> None:
        if self._auto_write:
            self.write_reports()


def _active_id(context: dict[str, Any] | None) -> int | None:
    return _as_int((context or {}).get("active_id")) or _as_int((context or {}).get("visible_active_id"))


def _raw_size(context: dict[str, Any] | None) -> int | None:
    return _as_int((context or {}).get("raw_size")) or _as_int((context or {}).get("visible_raw_size"))


def _symbol(context: dict[str, Any] | None) -> str | None:
    return _safe_string((context or {}).get("symbol")) or _safe_string((context or {}).get("visible_symbol")) or _safe_string((context or {}).get("display_name"))


def _bucket(active_id: int | None, raw_size: int | None) -> str | None:
    if active_id is None or raw_size is None:
        return None
    return f"POLARIUM:{active_id}:{raw_size}"


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _safe_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = " ".join(value.strip().split())
    if not parsed:
        return None
    lowered = parsed.lower()
    if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password", "secret")):
        return None
    return parsed[:120]


def _render_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Asset Switch Diagnostic", ""]
    summary = payload.get("summary", {})
    lines.append(f"total_switches: {summary.get('total_switches', 0)}")
    lines.append(f"categories: {summary.get('categories', {})}")
    lines.append("")
    for record in payload.get("records", []):
        lines.append(f"- {record.get('selection_id')}")
        lines.append(f"  active: {record.get('active_id_before')} -> {record.get('active_id_after')}")
        lines.append(f"  symbol: {record.get('symbol_before')} -> {record.get('symbol_after')}")
        lines.append(f"  bucket: {record.get('bucket_before')} -> {record.get('bucket_after')}")
        lines.append(f"  bucket_size: {record.get('bucket_size_before')} -> {record.get('bucket_size_after')}")
        lines.append(f"  bootstrap: started={record.get('request_started')} finished={record.get('request_finished')} discarded={record.get('request_discarded')}")
        lines.append(f"  chart: {record.get('chart_source_before')} -> {record.get('chart_source_after')} updated={record.get('chart_updated')}")
        lines.append(f"  frontend_updated: {record.get('frontend_updated')}")
        lines.append(f"  category: {record.get('category')}")
        lines.append(f"  failure_step: {record.get('failure_step')}")
        if record.get("failure_reason"):
            lines.append(f"  failure_reason: {record.get('failure_reason')}")
    lines.append("")
    return "\n".join(lines)
