from __future__ import annotations

import importlib.metadata
import subprocess

from app.market.providers.iq_option import probe


class FakeClient:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password


class FailingClient:
    def __init__(self, email: str, password: str) -> None:
        raise RuntimeError(f"failed for {email}:{password}")


class FakeTradingApi:
    def buy(self) -> None:
        raise AssertionError("should not call")

    def get_balance(self) -> None:
        raise AssertionError("should not call")

    def get_candles(self) -> None:
        return None


def sample_open_time_payload() -> dict:
    return {
        "digital": {
            "EURUSD-OTC": {"open": True},
            "GBPUSD-OTC": {"open": True},
            "EURUSD": {"open": True},
        },
        "turbo": {
            "EURUSD-OTC": {"open": True},
            "BTCUSD-OTC": {"open": False},
        },
        "binary": {},
    }


def sample_candles(raw_size: int) -> list[dict]:
    base = 1_783_720_000
    return [
        {"from": base + index * raw_size, "open": 1.1, "close": 1.2, "min": 1.0, "max": 1.3, "volume": index}
        for index in range(3)
    ]


def test_probe_network_is_disabled_by_default() -> None:
    assert probe.network_enabled({}) is False
    assert probe.network_enabled({probe.NETWORK_FLAG: "false"}) is False
    assert probe.network_enabled({probe.NETWORK_FLAG: "true"}) is True


def test_probe_reports_missing_credentials_without_values() -> None:
    env = {"IQ_OPTION_EMAIL": "", "IQ_OPTION_PASSWORD": None}

    assert probe.credentials_configured(env) is False
    assert probe.build_client_safely(FakeClient, None, None) == "CREDENTIALS_MISSING"


def test_import_fake_and_client_creation() -> None:
    assert probe.build_client_safely(FakeClient, "operator@example.invalid", "secret") == "CLIENT_CREATED"


def test_import_or_client_error_is_sanitized() -> None:
    result = probe.build_client_safely(FailingClient, "operator@example.invalid", "secret")

    assert result == "RuntimeError"
    assert "operator@example.invalid" not in result
    assert "secret" not in result


def test_otc_filter_returns_sanitized_sample_only() -> None:
    summary = probe.summarize_otc_assets(sample_open_time_payload(), limit=2)

    assert summary == {"otc_assets_count": 2, "sample_symbols": ["EURUSD-OTC", "GBPUSD-OTC"]}


def test_candles_m1_m5_m15_are_structurally_summarized() -> None:
    for raw_size in probe.SUPPORTED_PROBE_RAW_SIZES:
        summary = probe.summarize_candles("EURUSD-OTC", raw_size, sample_candles(raw_size))

        assert summary.raw_size == raw_size
        assert summary.count == 3
        assert summary.timestamps_ordered is True
        assert summary.timestamps_distinct is True
        assert summary.ohlc_fields_present is True
        assert summary.first_timestamp == 1_783_720_000
        assert summary.last_timestamp == 1_783_720_000 + raw_size * 2


def test_no_order_function_is_called_by_read_only_guard() -> None:
    guard = probe.ReadOnlyMethodGuard()

    try:
        guard.buy()
    except RuntimeError as exc:
        assert str(exc) == "READ_ONLY_VIOLATION"
    else:
        raise AssertionError("Expected read-only guard violation.")

    assert guard.called_methods == ["buy"]
    assert "buy" in probe.forbidden_methods_present(FakeTradingApi())
    assert "get_balance" in probe.forbidden_methods_present(FakeTradingApi())


def test_report_secret_detection() -> None:
    report = "IMPORT_OK CLIENT_CREATED"

    assert probe.contains_sensitive_value(report, ("secret", "operator@example.invalid")) is False
    assert probe.contains_sensitive_value(f"{report} secret", ("secret", None)) is True


def test_temporary_probe_venv_is_ignored_by_git() -> None:
    result = subprocess.run(
        ["git", "check-ignore", probe.PROBE_VENV_PATH],
        check=True,
        capture_output=True,
        text=True,
    )

    assert probe.PROBE_VENV_PATH in result.stdout


def test_main_venv_does_not_have_iqoptionapi_installed() -> None:
    try:
        importlib.metadata.version("iqoptionapi")
    except importlib.metadata.PackageNotFoundError:
        return
    raise AssertionError("iqoptionapi must not be installed in the main project .venv during the compatibility probe.")
