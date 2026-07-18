from __future__ import annotations

from app.market.providers.polarium.target_manager import CDPTarget, DualTabCDPSessionManager


def polarium_target() -> CDPTarget:
    return CDPTarget(target_id="polarium-1", url="https://trade.polariumbroker.com/traderoom", kind="page")


def friday_target() -> CDPTarget:
    return CDPTarget(target_id="friday-1", url="http://127.0.0.1:5173/market-chart", kind="page")


def test_dual_tab_opens_friday_when_market_session_is_ready() -> None:
    manager = DualTabCDPSessionManager(friday_frontend_url="http://127.0.0.1:5173")

    plan = manager.plan(targets=(polarium_target(),), market_ready=True, frontend_available=True, now_ms=1_000)

    assert plan.action == "open_friday"
    assert plan.friday_url == "http://127.0.0.1:5173"
    assert plan.polarium_target_id == "polarium-1"


def test_dual_tab_preserves_polarium_and_reuses_existing_friday_target() -> None:
    manager = DualTabCDPSessionManager(friday_frontend_url="http://127.0.0.1:5173")

    plan = manager.plan(targets=(polarium_target(), friday_target()), market_ready=True, frontend_available=True, now_ms=1_000)

    assert plan.action == "reuse_friday"
    assert plan.polarium_target_id == "polarium-1"
    assert plan.friday_target_id == "friday-1"


def test_dual_tab_is_idempotent_after_opening_friday() -> None:
    manager = DualTabCDPSessionManager(friday_frontend_url="http://127.0.0.1:5173")

    first = manager.plan(targets=(polarium_target(),), market_ready=True, frontend_available=True, now_ms=1_000)
    manager.mark_opened("friday-created")
    second = manager.plan(targets=(polarium_target(),), market_ready=True, frontend_available=True, now_ms=2_000)

    assert first.action == "open_friday"
    assert second.action == "skip"
    assert second.reason == "FRIDAY_TAB_ALREADY_HANDLED"


def test_dual_tab_opens_friday_without_waiting_for_market_session_ready() -> None:
    manager = DualTabCDPSessionManager(friday_frontend_url="http://127.0.0.1:5173")

    plan = manager.plan(targets=(polarium_target(),), market_ready=False, frontend_available=True, now_ms=1_000)

    assert plan.action == "open_friday"
    assert plan.reason == "SAFE_TO_OPEN_FRIDAY_TAB"
    assert plan.polarium_target_id == "polarium-1"


def test_dual_tab_frontend_unavailable_does_not_replace_or_close_polarium() -> None:
    manager = DualTabCDPSessionManager(friday_frontend_url="http://127.0.0.1:5173")

    plan = manager.plan(targets=(polarium_target(),), market_ready=True, frontend_available=False, now_ms=1_000)
    retry = manager.plan(targets=(polarium_target(),), market_ready=True, frontend_available=True, now_ms=7_000)

    assert plan.action == "wait"
    assert plan.reason == "FRIDAY_FRONTEND_UNAVAILABLE"
    assert plan.polarium_target_id == "polarium-1"
    assert retry.action == "open_friday"


def test_dual_tab_waits_until_polarium_target_exists() -> None:
    manager = DualTabCDPSessionManager(friday_frontend_url="http://127.0.0.1:5173")

    plan = manager.plan(targets=(), market_ready=True, frontend_available=True, now_ms=1_000)

    assert plan.action == "wait"
    assert plan.reason == "POLARIUM_TARGET_NOT_DETECTED"
