from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from app.market.store.types import CandleSeriesKey, CandleStoreWriteResult

LiveBootstrapFailureStage = Literal[
    "VISIBLE_CONTEXT_NOT_OBSERVED",
    "OWNER_BLOCKED",
    "OWNER_STALE",
    "REQUEST_NOT_CREATED",
    "PENDING_NOT_REGISTERED",
    "MARKET_SOCKET_NOT_RESOLVED",
    "WRONG_CDP_SOCKET",
    "SEND_NOT_ATTEMPTED",
    "SEND_FAILED",
    "NO_RESPONSE",
    "RESPONSE_NOT_CORRELATED",
    "RESPONSE_REJECTED",
    "PARSER_EMPTY",
    "STORE_NOT_WRITTEN",
    "READINESS_NOT_UPDATED",
    "SUCCESS",
    "UNKNOWN",
]

REPORT_DIR = Path(".jarvis_cache/diagnostics")
REPORT_JSON = REPORT_DIR / "live_bootstrap_request_report.json"
REPORT_TXT = REPORT_DIR / "live_bootstrap_request_report.txt"


@dataclass
class LiveBootstrapRequestRecord:
    active_id: int
    raw_size: int
    visible_context_observed: bool = False
    owner_selected: str | None = None
    owner_reason: str | None = None
    auto_bootstrap_decision: str | None = None
    request_created: bool = False
    request_id: str | None = None
    pending_registered: bool = False
    socket_request_id: str | None = None
    market_socket_match: bool | None = None
    send_attempted: bool = False
    send_succeeded: bool = False
    send_error_code: str | None = None
    response_received: bool = False
    response_type: str | None = None
    response_request_id: str | None = None
    correlation_result: str | None = None
    parser_count: int = 0
    store_key: str | None = None
    store_written: bool = False
    history_count: int = 0
    readiness: str | None = None
    failure_stage: LiveBootstrapFailureStage = "UNKNOWN"
    failure_reason: str | None = None
    observed_at: int | None = None

    def sanitized(self) -> dict[str, Any]:
        return asdict(self)


class LiveBootstrapRequestDiagnostic:
    """Records sanitized live bootstrap ownership and routing evidence."""

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
        self._records: dict[tuple[int, int], LiveBootstrapRequestRecord] = {}

    @property
    def records(self) -> tuple[LiveBootstrapRequestRecord, ...]:
        return tuple(self._records.values())

    def observe_visible_context(self, *, active_id: int | None, raw_size: int | None, now_ms: int) -> None:
        record = self._record(active_id, raw_size)
        if record is None:
            return
        record.visible_context_observed = True
        record.observed_at = now_ms
        _classify(record)
        self._write_if_enabled()

    def observe_owner(
        self,
        *,
        active_id: int | None,
        raw_size: int | None,
        owner: str,
        reason: str,
        request_id: str | None,
        market_socket_match: bool | None,
        socket_request_id: str | None,
        now_ms: int,
    ) -> None:
        record = self._record(active_id, raw_size)
        if record is None:
            return
        record.owner_selected = owner
        record.owner_reason = reason
        record.request_id = record.request_id or request_id
        record.market_socket_match = market_socket_match
        record.socket_request_id = socket_request_id
        record.observed_at = now_ms
        _classify(record)
        self._write_if_enabled()

    def observe_decision(self, *, active_id: int | None, raw_size: int | None, decision: str, reason: str | None, now_ms: int) -> None:
        record = self._record(active_id, raw_size)
        if record is None:
            return
        record.auto_bootstrap_decision = decision if reason is None else f"{decision}:{reason}"
        record.observed_at = now_ms
        _classify(record)
        self._write_if_enabled()

    def observe_request_created(self, *, active_id: int, raw_size: int, request_id: str, now_ms: int) -> None:
        record = self._record(active_id, raw_size)
        if record is None:
            return
        record.request_created = True
        record.request_id = request_id
        record.owner_selected = "AUTO_VISIBLE_CONTEXT"
        record.owner_reason = "VISIBLE_CONTEXT_BOOTSTRAP"
        record.observed_at = now_ms
        _classify(record)
        self._write_if_enabled()

    def observe_pending_registered(self, *, active_id: int | None, raw_size: int | None, request_id: str | None, now_ms: int) -> None:
        record = self._record(active_id, raw_size)
        if record is None:
            return
        record.pending_registered = True
        record.request_id = record.request_id or request_id
        record.observed_at = now_ms
        _classify(record)
        self._write_if_enabled()

    def observe_send(
        self,
        *,
        active_id: int,
        raw_size: int,
        request_id: str,
        socket_request_id: str | None,
        market_socket_match: bool | None,
        attempted: bool,
        succeeded: bool,
        error_code: str | None,
        now_ms: int,
    ) -> None:
        record = self._record(active_id, raw_size)
        if record is None:
            return
        record.request_id = request_id
        record.socket_request_id = socket_request_id
        record.market_socket_match = market_socket_match
        record.send_attempted = attempted
        record.send_succeeded = succeeded
        record.send_error_code = _sanitize(error_code)
        record.observed_at = now_ms
        _classify(record)
        self._write_if_enabled()

    def observe_response(
        self,
        *,
        active_id: int | None,
        raw_size: int | None,
        response_type: str | None,
        response_request_id: str | None,
        correlation_result: str,
        parser_count: int,
        store_results: tuple[CandleStoreWriteResult, ...],
        history_count: int,
        readiness: str | None,
        now_ms: int,
    ) -> None:
        record = self._record(active_id, raw_size)
        if record is None:
            return
        record.response_received = True
        record.response_type = response_type
        record.response_request_id = response_request_id
        record.correlation_result = correlation_result
        record.parser_count = parser_count
        record.store_key = _store_key_for(active_id, raw_size)
        record.store_written = any(_matches_result(item, active_id=active_id, raw_size=raw_size) and item.status in {"added", "updated"} for item in store_results)
        record.history_count = history_count
        record.readiness = readiness
        record.observed_at = now_ms
        _classify(record)
        self._write_if_enabled()

    def observe_programmatic_state(
        self,
        *,
        active_contexts: int,
        outbound_signatures: int,
        now_ms: int,
    ) -> None:
        if active_contexts == 0 and outbound_signatures == 0:
            return
        record = self._records.get((-1, -1)) or LiveBootstrapRequestRecord(active_id=-1, raw_size=-1)
        record.owner_selected = "PROGRAMMATIC_TRANSIENT_STATE"
        record.owner_reason = f"contexts={active_contexts};signatures={outbound_signatures}"
        record.failure_stage = "OWNER_STALE"
        record.failure_reason = "Programmatic transient state exists while selection is disabled."
        record.observed_at = now_ms
        self._records[(-1, -1)] = record
        self._write_if_enabled()

    def write_reports(self) -> None:
        self._report_json.parent.mkdir(parents=True, exist_ok=True)
        payload = self.sanitized()
        self._report_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._report_txt.write_text(_render_text(payload), encoding="utf-8")

    def sanitized(self) -> dict[str, Any]:
        records = [record.sanitized() for record in self.records]
        categories = Counter(record["failure_stage"] for record in records)
        return {
            "summary": {
                "total_records": len(records),
                "by_failure_stage": dict(sorted(categories.items())),
                "success_count": categories.get("SUCCESS", 0),
            },
            "records": records,
        }

    def _record(self, active_id: int | None, raw_size: int | None) -> LiveBootstrapRequestRecord | None:
        if active_id is None or raw_size is None:
            return None
        key = (active_id, raw_size)
        record = self._records.get(key)
        if record is None:
            record = LiveBootstrapRequestRecord(active_id=active_id, raw_size=raw_size)
            self._records[key] = record
        return record

    def _write_if_enabled(self) -> None:
        if self._auto_write:
            self.write_reports()


def _classify(record: LiveBootstrapRequestRecord) -> None:
    if record.store_written and record.history_count >= 50 and record.readiness == "READY":
        record.failure_stage = "SUCCESS"
        record.failure_reason = None
    elif not record.visible_context_observed:
        record.failure_stage = "VISIBLE_CONTEXT_NOT_OBSERVED"
        record.failure_reason = "Visible active_id/raw_size were not observed."
    elif record.owner_selected and record.owner_selected != "AUTO_VISIBLE_CONTEXT" and record.owner_reason == "NON_MARKET_SOCKET":
        record.failure_stage = "OWNER_BLOCKED"
        record.failure_reason = "Non-market socket owner must not block auto bootstrap."
    elif record.auto_bootstrap_decision is None:
        record.failure_stage = "REQUEST_NOT_CREATED"
        record.failure_reason = "No auto bootstrap decision recorded."
    elif record.auto_bootstrap_decision.startswith("none:MARKET_SOCKET_NOT_READY"):
        record.failure_stage = "MARKET_SOCKET_NOT_RESOLVED"
        record.failure_reason = "Market WebSocket was not ready."
    elif record.auto_bootstrap_decision.startswith("none:BOOTSTRAP_ALREADY_PENDING") and not record.send_attempted:
        record.failure_stage = "PENDING_NOT_REGISTERED" if not record.pending_registered else "NO_RESPONSE"
        record.failure_reason = "Bootstrap is pending but no response has been observed."
    elif not record.request_created:
        record.failure_stage = "REQUEST_NOT_CREATED"
        record.failure_reason = "BootstrapRequestFactory did not create a request."
    elif not record.pending_registered:
        record.failure_stage = "PENDING_NOT_REGISTERED"
        record.failure_reason = "Request was not registered as pending."
    elif record.market_socket_match is False:
        record.failure_stage = "WRONG_CDP_SOCKET"
        record.failure_reason = "Request was not associated with the current Market WebSocket."
    elif not record.send_attempted:
        record.failure_stage = "SEND_NOT_ATTEMPTED"
        record.failure_reason = "WebSocket.send was not attempted."
    elif not record.send_succeeded:
        record.failure_stage = "SEND_FAILED"
        record.failure_reason = record.send_error_code or "WebSocket.send failed."
    elif not record.response_received:
        record.failure_stage = "NO_RESPONSE"
        record.failure_reason = "No first-candles/candles response observed."
    elif record.correlation_result not in {None, "matched"}:
        record.failure_stage = "RESPONSE_NOT_CORRELATED"
        record.failure_reason = f"Correlation result: {record.correlation_result}"
    elif record.parser_count <= 0:
        record.failure_stage = "PARSER_EMPTY"
        record.failure_reason = "Parser returned no candles."
    elif not record.store_written:
        record.failure_stage = "STORE_NOT_WRITTEN"
        record.failure_reason = "No matching CandleStore write was observed."
    elif record.readiness != "READY":
        record.failure_stage = "READINESS_NOT_UPDATED"
        record.failure_reason = "Readiness did not reach READY."
    else:
        record.failure_stage = "UNKNOWN"
        record.failure_reason = "No classifier matched the current evidence."


def _matches_result(item: CandleStoreWriteResult, *, active_id: int | None, raw_size: int | None) -> bool:
    key = item.key
    if not isinstance(key, CandleSeriesKey):
        return False
    return key.provider == "POLARIUM" and key.active_id == active_id and key.raw_size == raw_size


def _store_key_for(active_id: int | None, raw_size: int | None) -> str | None:
    if active_id is None or raw_size is None:
        return None
    return f"POLARIUM:{active_id}:{raw_size}"


def _sanitize(value: str | None) -> str | None:
    if value is None:
        return None
    lowered = value.lower()
    if any(term in lowered for term in ("token", "cookie", "authorization", "bearer", "ssid", "password")):
        return "SANITIZED_ERROR"
    return value[:120]


def _render_text(payload: dict[str, Any]) -> str:
    lines = ["Friday Trade - Live Bootstrap Request Report", ""]
    summary = payload.get("summary", {})
    lines.append(f"total_records: {summary.get('total_records', 0)}")
    lines.append(f"by_failure_stage: {summary.get('by_failure_stage', {})}")
    lines.append("")
    for record in payload.get("records", []):
        lines.append(
            f"- active_id={record.get('active_id')} raw_size={record.get('raw_size')} "
            f"owner={record.get('owner_selected')} decision={record.get('auto_bootstrap_decision')} "
            f"request_id={record.get('request_id')} socket_request_id={record.get('socket_request_id')} "
            f"send={record.get('send_succeeded')} response={record.get('response_received')} "
            f"store_key={record.get('store_key')} history_count={record.get('history_count')} "
            f"readiness={record.get('readiness')} failure_stage={record.get('failure_stage')} "
            f"reason={record.get('failure_reason')}"
        )
    lines.append("")
    return "\n".join(lines)
