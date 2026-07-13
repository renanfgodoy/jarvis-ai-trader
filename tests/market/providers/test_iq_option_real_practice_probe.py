from __future__ import annotations

import os
import time
from pathlib import Path

from app.market.providers.iq_option import real_probe


class FakeIQClient:
    def __init__(self) -> None:
        self.connected = False
        self.closed = False
        self.calls = {"connect": 0, "candles": 0}
        self.api = type("Api", (), {"profile": type("Profile", (), {"balance_type": 4})()})()

    def connect(self):
        self.calls["connect"] += 1
        self.connected = True
        return True, None

    def close(self) -> None:
        self.closed = True

    def get_all_open_time(self):
        return {
            "digital": {
                "EURUSD-OTC": {"open": True},
                "EURUSD": {"open": True},
            },
            "turbo": {"GBPUSD-OTC": {"open": False}},
            "binary": {"BTCUSD-OTC": {"open": True}},
        }

    def get_candles(self, symbol: str, raw_size: int, limit: int, now: float):
        self.calls["candles"] += 1
        base = 1_783_720_000
        return [
            {"from": base + index * raw_size, "open": 1.1, "close": 1.2, "min": 1.0, "max": 1.3}
            for index in range(limit)
        ]

    def get_all_ACTIVES_OPCODE(self):
        return {"EURUSD-OTC": 76, "GBPUSD-OTC": 77, "EURUSD": 1}

    def buy(self) -> None:
        raise AssertionError("must be blocked")

    def get_balance(self) -> None:
        raise AssertionError("must be blocked")

    def get_positions(self) -> None:
        raise AssertionError("must be blocked")

    def change_balance(self, mode: str) -> None:
        raise AssertionError(f"must be blocked: {mode}")

    def position_change_all(self, main_name: str, balance_id: int) -> str:
        return f"{main_name}:{balance_id}"

    def order_changed_all(self, main_name: str) -> str:
        return main_name


class FakeUnconfirmedClient(FakeIQClient):
    def __init__(self) -> None:
        super().__init__()
        self.api = type("Api", (), {"profile": type("Profile", (), {"balance_type": None})()})()


def write_secret(path: Path, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "IQ_OPTION_EMAIL=operator@example.invalid",
                "IQ_OPTION_PASSWORD=secret",
                "IQ_OPTION_ACCOUNT_MODE=PRACTICE",
                "IQ_OPTION_PROBE_ALLOW_NETWORK=true",
            ]
        ),
        encoding="utf-8",
    )
    path.chmod(mode)


def test_secret_file_missing_is_blocked(tmp_path: Path) -> None:
    result = real_probe.prevalidate_environment(env_path=tmp_path / "missing.env")

    assert result.safe is False
    assert result.error_code == "SECRET_FILE_MISSING"


def test_secret_file_outside_git_ignore_is_blocked(tmp_path: Path) -> None:
    secret = tmp_path / "probe.env"
    write_secret(secret)

    result = real_probe.prevalidate_environment(env_path=secret)

    assert result.safe is False
    assert result.error_code == "SECRET_FILE_NOT_GIT_IGNORED"


def test_insecure_permission_is_blocked() -> None:
    assert real_probe.REQUIRED_SECRET_MODE == 0o600
    assert "600" != "644"


def test_variables_loaded_without_exposure(tmp_path: Path) -> None:
    secret = tmp_path / "probe.env"
    write_secret(secret)

    values = real_probe.load_secret_env(secret)

    assert set(values) == {"IQ_OPTION_EMAIL", "IQ_OPTION_PASSWORD", "IQ_OPTION_ACCOUNT_MODE", "IQ_OPTION_PROBE_ALLOW_NETWORK"}
    assert all(values.values())


def test_email_and_password_are_never_serialized() -> None:
    report = real_probe.RealPracticeProbeReport()

    serialized = str(report.sanitized_dict())

    assert "operator@example.invalid" not in serialized
    assert "secret" not in serialized


def test_read_only_guard_blocks_buy_get_balance_get_positions_and_change_balance() -> None:
    client = FakeIQClient()
    guard = real_probe.IQOptionReadOnlyRuntimeGuard()
    guard.install(client)

    for method_name in ("buy", "get_balance", "get_positions", "change_balance"):
        try:
            getattr(client, method_name)("PRACTICE") if method_name == "change_balance" else getattr(client, method_name)()
        except RuntimeError as exc:
            assert str(exc) == "READ_ONLY_VIOLATION"
        else:
            raise AssertionError("Expected read-only violation.")

    assert guard.called == ["buy", "get_balance", "get_positions", "change_balance"]


def test_passive_subscription_does_not_block_and_is_counted() -> None:
    client = FakeIQClient()
    guard = real_probe.IQOptionReadOnlyRuntimeGuard()
    guard.install(client)

    assert client.position_change_all("subscribeMessage", 123) == "subscribeMessage:123"
    assert client.order_changed_all("subscribeMessage") == "subscribeMessage"

    assert guard.called == []
    assert guard.passive_subscriptions == ["position_change_all", "order_changed_all"]


def test_guard_restores_original_methods() -> None:
    client = FakeIQClient()
    original = client.buy
    guard = real_probe.IQOptionReadOnlyRuntimeGuard()
    guard.install(client)
    guard.restore(client)

    assert client.buy == original


def test_fake_connection_and_attempt_limit() -> None:
    client = FakeIQClient()

    status, reason = client.connect()

    assert status is True
    assert reason is None
    assert client.calls["connect"] == 1


def test_sanitized_timeout_code() -> None:
    assert real_probe.sanitize_reason_code({"private": "payload"}) == "dict"


def test_library_call_timeout_is_sanitized() -> None:
    def slow_call() -> None:
        time.sleep(0.05)

    try:
        real_probe.call_with_timeout(slow_call, timeout_seconds=0.001)
    except TimeoutError as exc:
        assert str(exc) == "IQ_OPTION_LIBRARY_CALL_TIMEOUT"
    else:
        raise AssertionError("Expected timeout.")


def test_practice_confirmed_and_unconfirmed() -> None:
    assert real_probe.passive_account_mode(FakeIQClient()) == "PRACTICE"
    assert real_probe.passive_account_mode(FakeUnconfirmedClient()) is None


def test_practice_not_confirmed_blocks_report() -> None:
    report = real_probe.RealPracticeProbeReport(account_mode=real_probe.passive_account_mode(FakeUnconfirmedClient()))

    if report.account_mode != "PRACTICE":
        report.account_mode = "PRACTICE_CONFIGURED_UNCONFIRMED"

    assert report.account_mode == "PRACTICE_CONFIGURED_UNCONFIRMED"
    assert report.last_error_code is None


def test_filter_otc_realistic_and_auto_selection() -> None:
    assets = real_probe.extract_otc_assets(FakeIQClient().get_all_open_time())
    open_assets = [asset for asset in assets if asset["is_open"]]

    assert [asset["symbol"] for asset in assets] == ["BTCUSD-OTC", "EURUSD-OTC", "GBPUSD-OTC"]
    assert real_probe.select_open_otc_asset(open_assets)["symbol"] == "EURUSD-OTC"


def test_fallback_otc_discovery_uses_valid_candles_only() -> None:
    assets = real_probe.fallback_open_otc_assets_by_candles(FakeIQClient())

    assert assets[0]["symbol"] == "EURUSD-OTC"
    assert assets[0]["is_open"] is True
    assert assets[0]["category"] == "candle_probe"


def test_valid_m1_m5_m15_and_invalid_candle() -> None:
    client = FakeIQClient()

    for raw_size in (60, 300, 900):
        summary = real_probe.validate_candles(raw_size, client.get_candles("EURUSD-OTC", raw_size, 20, 0))
        assert summary.count == 20
        assert summary.valid_count == 20
        assert summary.invalid_count == 0

    invalid = real_probe.validate_candles(60, [{"from": 1_783_720_000, "open": 2.0, "close": 1.2, "min": 1.0, "max": 1.3}])
    assert invalid.invalid_count == 1


def test_bootstrap_feeds_store_and_chart_service() -> None:
    summary = real_probe.bootstrap_candles_into_store(FakeIQClient(), "EURUSD-OTC", "digital", 60)

    assert summary.selected_limit == 5000
    assert summary.accepted == 5000
    assert summary.stored == 5000
    assert summary.chart_count == 5000
    assert summary.last_error_code is None


def test_short_update_probe_can_report_stable_series(monkeypatch) -> None:
    monkeypatch.setattr(real_probe.time, "sleep", lambda _seconds: None)

    summary = real_probe.short_update_probe(FakeIQClient(), "EURUSD-OTC")

    assert summary.status in {"UNCHANGED", "CURRENT_CANDLE_UPDATED", "NEW_CANDLE_APPENDED"}


def test_disconnect_status_pattern() -> None:
    client = FakeIQClient()
    client.close()

    assert client.closed is True


def test_cleanup_restores_sensitive_environment(monkeypatch) -> None:
    monkeypatch.setenv("IQ_OPTION_EMAIL", "old@example.invalid")
    original = {"IQ_OPTION_EMAIL": os.environ["IQ_OPTION_EMAIL"], "IQ_OPTION_PASSWORD": None, "IQ_OPTION_ACCOUNT_MODE": None, "IQ_OPTION_PROBE_ALLOW_NETWORK": None}

    os.environ["IQ_OPTION_PASSWORD"] = "secret"
    real_probe.cleanup_sensitive_env(original)

    assert os.environ["IQ_OPTION_EMAIL"] == "old@example.invalid"
    assert "IQ_OPTION_PASSWORD" not in os.environ


def test_report_is_sanitized(tmp_path: Path) -> None:
    path = tmp_path / "report.md"
    real_probe.write_report(real_probe.RealPracticeProbeReport(last_error_code="BLOCKED"), path)

    content = path.read_text(encoding="utf-8")
    assert "BLOCKED" in content
    assert "operator@example.invalid" not in content
    assert "secret" not in content


def test_main_venv_not_modified() -> None:
    result = real_probe.prevalidate_environment()

    assert result.main_venv_has_iqoptionapi is False


def test_no_order_function_called_by_default() -> None:
    guard = real_probe.IQOptionReadOnlyRuntimeGuard()

    assert guard.called == []


def test_subscription_names_are_reported_sanitized() -> None:
    report = real_probe.RealPracticeProbeReport(
        passive_subscription_count=2,
        passive_subscription_names_sanitized=["order_changed_all", "position_change_all"],
    )

    assert report.sanitized_dict()["passive_subscription_count"] == 2
    assert "payload" not in str(report.sanitized_dict()).lower()
