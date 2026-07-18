from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.market.providers.polarium.native_bootstrap import (
    NativeBootstrapSendResult,
    NativeBootstrapSequenceReport,
    NativeBootstrapStatus,
    NativeHistoricalBootstrapOrchestrator,
)
from app.market.providers.polarium.runtime_guard import PolariumRuntimeGuard, PolariumRuntimeGuardViolation


def status_for(active_id: int, raw_size: int, *, history_count: int, state: str) -> NativeBootstrapStatus:
    context = {
        "active_id": active_id,
        "raw_size": raw_size,
        "history_state": state,
        "history_count": history_count,
        "history_required": 50,
    }
    return NativeBootstrapStatus(
        bootstrap_ready=state == "READY" and history_count >= 50,
        bootstrap_complete=state == "READY" and history_count >= 50,
        chart_count=history_count,
        session_context=context,
    )


def response(name: str, active_id: int, raw_size: int, request_id: str) -> dict:
    return {
        "name": name,
        "request_id": request_id,
        "msg": {"body": {"active_id": active_id, "size": raw_size}},
    }


def report(tmp_path: Path) -> NativeBootstrapSequenceReport:
    return NativeBootstrapSequenceReport(
        report_json=tmp_path / "native_bootstrap_sequence_report.json",
        report_txt=tmp_path / "native_bootstrap_sequence_report.txt",
    )


@pytest.mark.parametrize("raw_size", (60, 300, 900))
def test_native_bootstrap_replays_sequence_until_ready_for_m1_m5_m15(tmp_path: Path, raw_size: int) -> None:
    active_id = 2298
    history_count = 0
    state = "BOOTSTRAPPING"
    sent: list[dict] = []
    orchestrator = NativeHistoricalBootstrapOrchestrator(report=report(tmp_path), request_spacing_seconds=0)

    async def send(payload: dict) -> NativeBootstrapSendResult:
        nonlocal history_count, state
        sent.append(payload)
        inner = payload["msg"]["name"]
        if inner == "get-first-candles":
            history_count = max(history_count, 1)
            state = "LIMITED"
            orchestrator.observe_response(response("first-candles", active_id, raw_size, payload["request_id"]), status=current_status())
        if inner == "get-candles":
            history_count += 20
            if history_count >= 50:
                state = "READY"
            orchestrator.observe_response(response("candles", active_id, raw_size, payload["request_id"]), status=current_status())
        return NativeBootstrapSendResult(sent=True)

    def current_status() -> NativeBootstrapStatus:
        return status_for(active_id, raw_size, history_count=history_count, state=state)

    result = __import__("asyncio").run(
        orchestrator.run(
            active_id=active_id,
            raw_size=raw_size,
            send=send,
            status=current_status,
            timeout_seconds=0.5,
        )
    )

    assert result.bootstrap_ready is True
    assert result.bootstrap_complete is True
    assert [payload["msg"]["name"] for payload in sent] == [
        "candles-generated",
        "get-first-candles",
        "get-first-candles",
        "get-candles",
        "get-candles",
        "get-candles",
    ]
    rendered = json.loads((tmp_path / "native_bootstrap_sequence_report.json").read_text(encoding="utf-8"))
    assert rendered["summary"]["bootstrap_complete"] is True
    assert rendered["summary"]["last_history_count"] >= 50


def test_native_bootstrap_times_out_when_first_candles_never_arrives(tmp_path: Path) -> None:
    orchestrator = NativeHistoricalBootstrapOrchestrator(report=report(tmp_path), response_timeout_seconds=0.01)
    sent: list[dict] = []

    async def send(payload: dict) -> NativeBootstrapSendResult:
        sent.append(payload)
        return NativeBootstrapSendResult(sent=True)

    result = __import__("asyncio").run(
        orchestrator.run(
            active_id=2298,
            raw_size=300,
            send=send,
            status=lambda: status_for(2298, 300, history_count=0, state="BOOTSTRAPPING"),
            timeout_seconds=0.05,
        )
    )

    assert result.bootstrap_ready is False
    assert result.error_code == "FIRST_CANDLES_RESPONSE_TIMEOUT"
    assert [payload["msg"]["name"] for payload in sent] == ["candles-generated", "get-first-candles"]


def test_native_bootstrap_interrupts_on_send_failure(tmp_path: Path) -> None:
    orchestrator = NativeHistoricalBootstrapOrchestrator(report=report(tmp_path), request_spacing_seconds=0)
    sent: list[dict] = []

    async def send(payload: dict) -> NativeBootstrapSendResult:
        sent.append(payload)
        if payload["msg"]["name"] == "get-candles":
            return NativeBootstrapSendResult(sent=False, error_code="SEND_FAILED")
        if payload["msg"]["name"] == "get-first-candles":
            orchestrator.observe_response(response("first-candles", 2298, 300, payload["request_id"]), status=status_for(2298, 300, history_count=1, state="LIMITED"))
        return NativeBootstrapSendResult(sent=True)

    result = __import__("asyncio").run(
        orchestrator.run(
            active_id=2298,
            raw_size=300,
            send=send,
            status=lambda: status_for(2298, 300, history_count=1, state="LIMITED"),
            timeout_seconds=0.2,
        )
    )

    assert result.error_code == "SEND_FAILED"
    assert [payload["msg"]["name"] for payload in sent] == ["candles-generated", "get-first-candles", "get-first-candles", "get-candles"]


def test_native_bootstrap_reexecution_resets_report_and_preserves_sequence(tmp_path: Path) -> None:
    orchestrator = NativeHistoricalBootstrapOrchestrator(report=report(tmp_path), request_spacing_seconds=0)
    calls = 0

    async def send(payload: dict) -> NativeBootstrapSendResult:
        nonlocal calls
        calls += 1
        if payload["msg"]["name"] == "get-first-candles":
            orchestrator.observe_response(response("first-candles", 76, 60, payload["request_id"]), status=status_for(76, 60, history_count=1, state="LIMITED"))
        if payload["msg"]["name"] == "get-candles":
            orchestrator.observe_response(response("candles", 76, 60, payload["request_id"]), status=status_for(76, 60, history_count=60, state="READY"))
        return NativeBootstrapSendResult(sent=True)

    for _ in range(2):
        result = __import__("asyncio").run(
            orchestrator.run(
                active_id=76,
                raw_size=60,
                send=send,
                status=lambda: status_for(76, 60, history_count=60, state="READY"),
                timeout_seconds=0.2,
            )
        )
        assert result.bootstrap_complete is True

    payload = json.loads((tmp_path / "native_bootstrap_sequence_report.json").read_text(encoding="utf-8"))
    assert calls == 12
    assert payload["summary"]["requests"] == 6


def test_native_bootstrap_ignores_stale_response_after_fast_asset_switch(tmp_path: Path) -> None:
    orchestrator = NativeHistoricalBootstrapOrchestrator(report=report(tmp_path), request_spacing_seconds=0)

    async def send(payload: dict) -> NativeBootstrapSendResult:
        if payload["msg"]["name"] == "get-first-candles":
            orchestrator.observe_response(response("first-candles", 76, 60, payload["request_id"]), status=status_for(76, 60, history_count=1, state="LIMITED"))
        if payload["msg"]["name"] == "get-candles":
            orchestrator.observe_response(response("candles", 76, 60, payload["request_id"]), status=status_for(76, 60, history_count=60, state="READY"))
        return NativeBootstrapSendResult(sent=True)

    __import__("asyncio").run(
        orchestrator.run(
            active_id=76,
            raw_size=60,
            send=send,
            status=lambda: status_for(76, 60, history_count=60, state="READY"),
            timeout_seconds=0.2,
        )
    )
    orchestrator.observe_response(response("candles", 2298, 300, "stale"), status=status_for(2298, 300, history_count=60, state="READY"))

    payload = json.loads((tmp_path / "native_bootstrap_sequence_report.json").read_text(encoding="utf-8"))
    assert all(entry.get("active_id") in {76, None} for entry in payload["entries"])


def test_runtime_guard_allows_only_read_only_get_candles() -> None:
    guard = PolariumRuntimeGuard()

    guard.validate_outbound({"name": "sendMessage", "msg": {"name": "get-candles", "body": {"active_id": 76, "size": 300}}})

    with pytest.raises(PolariumRuntimeGuardViolation):
        guard.validate_outbound({"name": "sendMessage", "msg": {"name": "get-candles", "body": {"active_id": 76, "size": 120}}})
