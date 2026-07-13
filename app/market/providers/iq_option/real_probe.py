from __future__ import annotations

import hashlib
import importlib
import math
import os
import queue
import stat
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from app.market.providers.iq_option.probe import (
    FORBIDDEN_RUNTIME_METHODS,
    PINNED_COMMIT_SHA,
    PINNED_REPOSITORY_URL,
    PROBE_VENV_PATH,
    credentials_configured,
    network_enabled,
    sanitized_exception_code,
)

SECRET_ENV_PATH = Path(".jarvis_cache/iq_option/probe.env")
REPORT_PATH = Path("docs/iq_option/IQ_OPTION_REAL_PRACTICE_PROBE_REPORT.md")
REQUIRED_SECRET_MODE = 0o600
PRACTICE_MODE = "PRACTICE"
REAL_PROBE_LIMIT = 20
REAL_PROBE_SIZES = (60, 300, 900)
BOOTSTRAP_LIMIT_CANDIDATES = (5000, 2000, 1000, 500, 200, 100)
LIBRARY_CALL_TIMEOUT_SECONDS = 25
DISCOVERY_CANDLE_TIMEOUT_SECONDS = 8
OTC_PRIORITY_SYMBOLS = ("EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDCAD-OTC")
EXTRA_FORBIDDEN_METHODS = (
    "get_order",
    "get_orders",
    "get_position",
    "get_positions",
    "get_portfolio",
)
PASSIVE_SUBSCRIPTION_METHODS = ("position_change_all", "order_changed_all")


@dataclass(frozen=True)
class PreValidationResult:
    project_root: str
    main_python_version: str
    isolated_python_version: str
    env_file_exists: bool
    env_file_git_ignored: bool
    env_file_mode: str | None
    main_venv_has_iqoptionapi: bool
    isolated_venv_has_iqoptionapi: bool
    safe: bool
    error_code: str | None = None


@dataclass(frozen=True)
class CandleValidationSummary:
    raw_size: int
    count: int
    distinct_timestamps: int
    first_timestamp: int | None
    last_timestamp: int | None
    valid_count: int
    invalid_count: int
    last_error_code: str | None = None


@dataclass(frozen=True)
class UpdateSummary:
    status: str
    first_hash: str | None = None
    second_hash: str | None = None


@dataclass(frozen=True)
class BootstrapSummary:
    selected_limit: int = 0
    accepted: int = 0
    rejected: int = 0
    stored: int = 0
    chart_count: int = 0
    last_error_code: str | None = None


@dataclass
class RealPracticeProbeReport:
    library_source: str = PINNED_REPOSITORY_URL
    library_commit: str = PINNED_COMMIT_SHA
    python_version: str = sys.version.split()[0]
    import_result: str = "NOT_EXECUTED"
    client_result: str = "NOT_EXECUTED"
    connected: bool = False
    account_mode: str | None = None
    read_only: bool = True
    connection_attempts: int = 0
    connection_duration_ms: int | None = None
    otc_assets_count: int = 0
    open_otc_assets_count: int = 0
    sample_symbols: list[str] = field(default_factory=list)
    selected_symbol: str | None = None
    selected_category: str | None = None
    m1: CandleValidationSummary | None = None
    m5: CandleValidationSummary | None = None
    m15: CandleValidationSummary | None = None
    update_summary: UpdateSummary = field(default_factory=lambda: UpdateSummary(status="NOT_EXECUTED"))
    bootstrap_summary: BootstrapSummary = field(default_factory=BootstrapSummary)
    disconnect_status: str = "NOT_EXECUTED"
    last_error_code: str | None = None
    forbidden_method_calls: list[str] = field(default_factory=list)
    passive_subscription_count: int = 0
    passive_subscription_names_sanitized: list[str] = field(default_factory=list)
    credentials_exposed: bool = False
    main_venv_modified: bool = False

    def sanitized_dict(self) -> dict[str, Any]:
        return asdict(self)


class IQOptionReadOnlyRuntimeGuard:
    def __init__(self) -> None:
        self.called: list[str] = []
        self.passive_subscriptions: list[str] = []
        self._originals: dict[str, Any] = {}

    def install(self, client: Any) -> None:
        for name in tuple(FORBIDDEN_RUNTIME_METHODS) + EXTRA_FORBIDDEN_METHODS:
            if hasattr(client, name):
                self._originals[name] = getattr(client, name)
                setattr(client, name, self._blocked(name))
        for name in PASSIVE_SUBSCRIPTION_METHODS:
            if hasattr(client, name):
                original = getattr(client, name)
                self._originals[name] = original
                setattr(client, name, self._passive_subscription(name, original))

    def restore(self, client: Any) -> None:
        for name, original in self._originals.items():
            setattr(client, name, original)

    def _blocked(self, name: str) -> Callable[..., None]:
        def blocked(*_args: Any, **_kwargs: Any) -> None:
            self.called.append(name)
            raise RuntimeError("READ_ONLY_VIOLATION")

        return blocked

    def _passive_subscription(self, name: str, original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            self.passive_subscriptions.append(name)
            return original(*args, **kwargs)

        return wrapped


ReadOnlyRuntimeGuard = IQOptionReadOnlyRuntimeGuard


def run_real_practice_probe(env_path: Path = SECRET_ENV_PATH) -> RealPracticeProbeReport:
    report = RealPracticeProbeReport()
    loaded_env = load_secret_env(env_path)
    original_env = {key: os.environ.get(key) for key in ("IQ_OPTION_EMAIL", "IQ_OPTION_PASSWORD", "IQ_OPTION_ACCOUNT_MODE", "IQ_OPTION_PROBE_ALLOW_NETWORK")}
    try:
        os.environ.update(loaded_env)
        if not credentials_configured(os.environ):
            report.last_error_code = "CREDENTIALS_MISSING"
            return report
        if not network_enabled(os.environ):
            report.last_error_code = "NETWORK_NOT_AUTHORIZED"
            return report
        if os.environ.get("IQ_OPTION_ACCOUNT_MODE") != PRACTICE_MODE:
            report.last_error_code = "ACCOUNT_MODE_NOT_PRACTICE"
            return report

        try:
            IQ_Option = importlib.import_module("iqoptionapi.stable_api").IQ_Option
        except Exception as exc:
            report.import_result = sanitized_exception_code(exc)
            report.last_error_code = "IMPORT_FAILED"
            return report
        report.import_result = "IMPORT_OK"

        try:
            client = IQ_Option(os.environ["IQ_OPTION_EMAIL"], os.environ["IQ_OPTION_PASSWORD"], active_account_type=PRACTICE_MODE)
        except Exception as exc:
            report.client_result = sanitized_exception_code(exc)
            report.last_error_code = "CLIENT_CREATE_FAILED"
            return report
        report.client_result = "CLIENT_CREATED"

        guard = IQOptionReadOnlyRuntimeGuard()
        guard.install(client)
        try:
            started_at = time.monotonic()
            for attempt in range(1, 3):
                report.connection_attempts = attempt
                try:
                    status, reason = client.connect()
                except RuntimeError as exc:
                    report.forbidden_method_calls = guard.called
                    report.last_error_code = str(exc)
                    return report
                except Exception as exc:
                    report.last_error_code = sanitized_exception_code(exc)
                    continue
                if status:
                    report.connected = True
                    report.last_error_code = None
                    break
                report.last_error_code = sanitize_reason_code(reason)
                time.sleep(0.5)
            report.connection_duration_ms = int((time.monotonic() - started_at) * 1000)
            report.forbidden_method_calls = guard.called
            report.passive_subscription_count = len(guard.passive_subscriptions)
            report.passive_subscription_names_sanitized = sorted(set(guard.passive_subscriptions))[:10]
            if not report.connected:
                return report

            mode = passive_account_mode(client)
            report.account_mode = mode or "PRACTICE_CONFIGURED_UNCONFIRMED"

            assets_error: str | None = None
            try:
                open_time_payload = call_with_timeout(client.get_all_open_time, timeout_seconds=LIBRARY_CALL_TIMEOUT_SECONDS)
                assets = extract_otc_assets(open_time_payload)
            except TimeoutError:
                assets_error = "ASSETS_TIMEOUT"
                assets = fallback_open_otc_assets_by_candles(client)
            except Exception as exc:
                assets_error = sanitized_exception_code(exc)
                assets = fallback_open_otc_assets_by_candles(client)
            report.otc_assets_count = len(assets)
            open_assets = [asset for asset in assets if asset["is_open"]]
            report.open_otc_assets_count = len(open_assets)
            report.sample_symbols = [asset["symbol"] for asset in open_assets[:10]]
            selected = select_open_otc_asset(open_assets)
            if selected is None:
                report.last_error_code = assets_error or "NO_OPEN_OTC_ASSET"
                return report
            report.selected_symbol = selected["symbol"]
            report.selected_category = selected["category"]

            summaries = fetch_timeframes(client, report.selected_symbol)
            report.m1 = summaries.get(60)
            report.m5 = summaries.get(300)
            report.m15 = summaries.get(900)
            if not report.m1 or report.m1.valid_count <= 0:
                report.last_error_code = "M1_CANDLES_UNAVAILABLE"
                return report
            report.bootstrap_summary = bootstrap_candles_into_store(client, report.selected_symbol, report.selected_category, report.m1.raw_size)
            if report.bootstrap_summary.accepted <= 0 or report.bootstrap_summary.chart_count <= 0:
                report.last_error_code = report.bootstrap_summary.last_error_code or "BOOTSTRAP_FAILED"
                return report
            try:
                report.update_summary = short_update_probe(client, report.selected_symbol)
            except TimeoutError:
                report.update_summary = UpdateSummary(status="UPDATE_TIMEOUT")
            except Exception as exc:
                report.update_summary = UpdateSummary(status=sanitized_exception_code(exc))
            return report
        finally:
            report.forbidden_method_calls = guard.called
            report.passive_subscription_count = len(guard.passive_subscriptions)
            report.passive_subscription_names_sanitized = sorted(set(guard.passive_subscriptions))[:10]
            report.disconnect_status = disconnect_client(client)
            guard.restore(client)
    finally:
        cleanup_sensitive_env(original_env)


def prevalidate_environment(project_root: Path = Path("."), env_path: Path = SECRET_ENV_PATH) -> PreValidationResult:
    root = project_root.resolve()
    env_exists = env_path.exists()
    ignored = _git_check_ignore(env_path)
    mode = _file_mode(env_path) if env_exists else None
    main_has = _package_available(Path(".venv/bin/python"), "iqoptionapi")
    isolated_has = _package_available(Path(f"{PROBE_VENV_PATH}/bin/python"), "iqoptionapi")
    safe = env_exists and ignored and mode == "600" and not main_has and isolated_has
    error = None
    if not env_exists:
        error = "SECRET_FILE_MISSING"
    elif not ignored:
        error = "SECRET_FILE_NOT_GIT_IGNORED"
    elif mode != "600":
        error = "SECRET_FILE_INSECURE_PERMISSION"
    elif main_has:
        error = "MAIN_VENV_MODIFIED"
    elif not isolated_has:
        error = "ISOLATED_LIBRARY_MISSING"
    return PreValidationResult(
        project_root=str(root),
        main_python_version=_python_version(Path(".venv/bin/python")),
        isolated_python_version=_python_version(Path(f"{PROBE_VENV_PATH}/bin/python")),
        env_file_exists=env_exists,
        env_file_git_ignored=ignored,
        env_file_mode=mode,
        main_venv_has_iqoptionapi=main_has,
        isolated_venv_has_iqoptionapi=isolated_has,
        safe=safe,
        error_code=error,
    )


def load_secret_env(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError("SECRET_FILE_MISSING")
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in {"IQ_OPTION_EMAIL", "IQ_OPTION_PASSWORD", "IQ_OPTION_ACCOUNT_MODE", "IQ_OPTION_PROBE_ALLOW_NETWORK"}:
            values[key] = value.strip().strip("\"'")
    return values


def passive_account_mode(client: Any) -> str | None:
    profile = getattr(getattr(client, "api", None), "profile", None)
    balance_type = getattr(profile, "balance_type", None)
    if balance_type in (4, "4", "practice", "PRACTICE"):
        return PRACTICE_MODE
    if balance_type in (1, "1", "real", "REAL"):
        return "REAL"
    return None


def extract_otc_assets(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    assets: dict[str, dict[str, Any]] = {}
    for category in ("digital", "turbo", "binary"):
        category_payload = payload.get(category)
        if not isinstance(category_payload, dict):
            continue
        for symbol, metadata in category_payload.items():
            if not isinstance(symbol, str) or not symbol.endswith("-OTC") or not isinstance(metadata, dict):
                continue
            assets[symbol] = {"symbol": symbol, "category": category, "is_open": bool(metadata.get("open"))}
    return [assets[symbol] for symbol in sorted(assets)]


def fallback_open_otc_assets_by_candles(client: Any) -> list[dict[str, Any]]:
    candidates = otc_candidate_symbols(client)
    open_assets: list[dict[str, Any]] = []
    for symbol in candidates:
        try:
            candles = call_with_timeout(
                client.get_candles,
                symbol,
                60,
                1,
                time.time(),
                timeout_seconds=DISCOVERY_CANDLE_TIMEOUT_SECONDS,
            )
        except Exception:
            continue
        summary = validate_candles(60, candles)
        if summary.valid_count > 0:
            open_assets.append({"symbol": symbol, "category": "candle_probe", "is_open": True})
    return open_assets


def otc_candidate_symbols(client: Any) -> list[str]:
    try:
        active_codes = client.get_all_ACTIVES_OPCODE()
    except Exception:
        active_codes = {}
    discovered = [symbol for symbol in active_codes if isinstance(symbol, str) and symbol.endswith("-OTC")]
    ordered: list[str] = []
    for symbol in OTC_PRIORITY_SYMBOLS:
        if symbol not in ordered:
            ordered.append(symbol)
    for symbol in sorted(discovered):
        if symbol not in ordered:
            ordered.append(symbol)
    return ordered[:30]


def select_open_otc_asset(assets: list[dict[str, Any]]) -> dict[str, Any] | None:
    for symbol in OTC_PRIORITY_SYMBOLS:
        for asset in assets:
            if asset["symbol"] == symbol:
                return asset
    return assets[0] if assets else None


def fetch_timeframes(client: Any, symbol: str) -> dict[int, CandleValidationSummary]:
    summaries: dict[int, CandleValidationSummary] = {}
    for raw_size in REAL_PROBE_SIZES:
        try:
            candles = call_with_timeout(
                client.get_candles,
                symbol,
                raw_size,
                REAL_PROBE_LIMIT,
                time.time(),
                timeout_seconds=LIBRARY_CALL_TIMEOUT_SECONDS,
            )
        except TimeoutError:
            summaries[raw_size] = CandleValidationSummary(raw_size, 0, 0, None, None, 0, 0, "CANDLES_TIMEOUT")
            continue
        except Exception as exc:
            summaries[raw_size] = CandleValidationSummary(raw_size, 0, 0, None, None, 0, 0, sanitized_exception_code(exc))
            continue
        summaries[raw_size] = validate_candles(raw_size, candles)
    return summaries


def bootstrap_candles_into_store(client: Any, symbol: str, category: str | None, raw_size: int) -> BootstrapSummary:
    from app.market.chart.service import CandleChartService
    from app.market.events.models import NormalizedMarketCandle
    from app.market.store import CandleStore

    selected_limit = 0
    selected_candles: list[dict[str, Any]] = []
    last_error_code: str | None = None
    for limit in BOOTSTRAP_LIMIT_CANDIDATES:
        try:
            raw_candles = call_with_timeout(
                client.get_candles,
                symbol,
                raw_size,
                limit,
                time.time(),
                timeout_seconds=LIBRARY_CALL_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            last_error_code = sanitized_exception_code(exc)
            continue
        summary = validate_candles(raw_size, raw_candles)
        if summary.valid_count > 0:
            selected_limit = limit
            selected_candles = raw_candles
            break
        last_error_code = summary.last_error_code

    if not selected_candles:
        return BootstrapSummary(selected_limit=selected_limit, last_error_code=last_error_code or "NO_BOOTSTRAP_CANDLES")

    store = CandleStore(max_candles_per_series=max(len(selected_candles), 1))
    accepted = 0
    rejected = 0
    stored = 0
    for raw in selected_candles:
        candle = normalized_iq_option_candle(raw, symbol=symbol, raw_size=raw_size, category=category)
        if candle is None:
            rejected += 1
            continue
        result = store.add(candle)
        if result.status in {"added", "updated", "ignored"}:
            accepted += 1
        if result.status == "added":
            stored += 1

    chart = CandleChartService(store).get_chart_series_by_key(
        key=store.series_keys()[0],
        limit=max(selected_limit, len(selected_candles)),
    ) if store.series_keys() else None
    chart_count = len(chart.candles) if chart else 0
    return BootstrapSummary(
        selected_limit=selected_limit,
        accepted=accepted,
        rejected=rejected,
        stored=stored,
        chart_count=chart_count,
        last_error_code=None if chart_count > 0 else "CHART_EMPTY",
    )


def normalized_iq_option_candle(raw: dict[str, Any], *, symbol: str, raw_size: int, category: str | None):
    from app.market.events.models import NormalizedMarketCandle

    timestamp = _as_int(raw.get("from") or raw.get("at") or raw.get("timestamp"))
    open_price = _as_float(raw.get("open"))
    close = _as_float(raw.get("close"))
    low = _as_float(raw.get("min") if raw.get("min") is not None else raw.get("low"))
    high = _as_float(raw.get("max") if raw.get("max") is not None else raw.get("high"))
    if timestamp is None or None in {open_price, close, low, high}:
        return None
    if not all(math.isfinite(value) and value > 0 for value in (open_price, close, low, high)):
        return None
    if not (high >= low and low <= open_price <= high and low <= close <= high):
        return None
    volume = _as_float(raw.get("volume")) or 0.0
    return NormalizedMarketCandle(
        active_id=None,
        symbol=symbol,
        raw_size=raw_size,
        timeframe=None,
        start_timestamp=timestamp,
        end_timestamp=timestamp + raw_size,
        open=open_price,
        close=close,
        low_candidate=low,
        high_candidate=high,
        volume=volume,
        source="iq_option",
        source_event=f"iq-option-otc-{category or 'unknown'}",
        source_verified=True,
        mapping_verified=True,
        mapping_notes=("IQ Option OTC read-only bootstrap candle.",),
    )


def validate_candles(raw_size: int, candles: Any) -> CandleValidationSummary:
    if not isinstance(candles, list):
        return CandleValidationSummary(raw_size, 0, 0, None, None, 0, 0, "INVALID_CANDLE_RESPONSE")
    timestamps: list[int] = []
    valid = 0
    invalid = 0
    for candle in candles:
        timestamp = _as_int(candle.get("from") if isinstance(candle, dict) else None)
        open_price = _as_float(candle.get("open") if isinstance(candle, dict) else None)
        close = _as_float(candle.get("close") if isinstance(candle, dict) else None)
        low = _as_float((candle.get("min") if candle.get("min") is not None else candle.get("low")) if isinstance(candle, dict) else None)
        high = _as_float((candle.get("max") if candle.get("max") is not None else candle.get("high")) if isinstance(candle, dict) else None)
        if timestamp is not None:
            timestamps.append(timestamp)
        if timestamp is None or None in {open_price, close, low, high}:
            invalid += 1
            continue
        if not all(math.isfinite(value) and value > 0 for value in (open_price, close, low, high)):
            invalid += 1
            continue
        if not (high >= low and low <= open_price <= high and low <= close <= high):
            invalid += 1
            continue
        valid += 1
    ordered = timestamps == sorted(timestamps)
    distinct = len(set(timestamps))
    return CandleValidationSummary(
        raw_size=raw_size,
        count=len(candles),
        distinct_timestamps=distinct,
        first_timestamp=min(timestamps) if timestamps else None,
        last_timestamp=max(timestamps) if timestamps else None,
        valid_count=valid if ordered else 0,
        invalid_count=invalid + (0 if ordered else len(candles)),
        last_error_code=None if valid and ordered else "INVALID_CANDLES",
    )


def short_update_probe(client: Any, symbol: str) -> UpdateSummary:
    first = call_with_timeout(client.get_candles, symbol, 60, REAL_PROBE_LIMIT, time.time(), timeout_seconds=LIBRARY_CALL_TIMEOUT_SECONDS)
    first_hash = structural_last_candle_hash(first)
    time.sleep(5)
    second = call_with_timeout(client.get_candles, symbol, 60, REAL_PROBE_LIMIT, time.time(), timeout_seconds=LIBRARY_CALL_TIMEOUT_SECONDS)
    second_hash = structural_last_candle_hash(second)
    first_last = _last_timestamp(first)
    second_last = _last_timestamp(second)
    if first_hash == second_hash:
        return UpdateSummary(status="UNCHANGED", first_hash=first_hash, second_hash=second_hash)
    if first_last is not None and second_last is not None and second_last > first_last:
        return UpdateSummary(status="NEW_CANDLE_APPENDED", first_hash=first_hash, second_hash=second_hash)
    return UpdateSummary(status="CURRENT_CANDLE_UPDATED", first_hash=first_hash, second_hash=second_hash)


def call_with_timeout(function: Callable[..., Any], *args: Any, timeout_seconds: float, **kwargs: Any) -> Any:
    results: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=1)

    def run() -> None:
        try:
            results.put(("ok", function(*args, **kwargs)))
        except BaseException as exc:  # pragma: no cover - defensive around external library
            results.put(("error", exc))

    worker = threading.Thread(target=run, name="iq-option-probe-library-call", daemon=True)
    worker.start()
    try:
        status, value = results.get(timeout=timeout_seconds)
    except queue.Empty as exc:
        raise TimeoutError("IQ_OPTION_LIBRARY_CALL_TIMEOUT") from exc
    if status == "error":
        raise value
    return value


def disconnect_client(client: Any) -> str:
    close = getattr(client, "close", None)
    api_close = getattr(getattr(client, "api", None), "close", None)
    try:
        if callable(close):
            close()
            return "DISCONNECTED"
        if callable(api_close):
            api_close()
            return "DISCONNECTED"
    except Exception:
        return "DISCONNECT_FAILED"
    return "DISCONNECT_NOT_SUPPORTED"


def structural_last_candle_hash(candles: Any) -> str | None:
    if not isinstance(candles, list) or not candles:
        return None
    candle = candles[-1]
    if not isinstance(candle, dict):
        return None
    parts = [str(candle.get(key)) for key in ("from", "open", "close", "min", "max", "low", "high")]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def write_report(report: RealPracticeProbeReport, path: Path = REPORT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = report.sanitized_dict()
    lines = ["# IQ Option Real PRACTICE Probe Report", ""]
    for key, value in data.items():
        lines.append(f"## {key}")
        lines.append("")
        lines.append("```text")
        lines.append(str(value))
        lines.append("```")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def cleanup_sensitive_env(original_env: Mapping[str, str | None]) -> None:
    for key in ("IQ_OPTION_EMAIL", "IQ_OPTION_PASSWORD", "IQ_OPTION_ACCOUNT_MODE", "IQ_OPTION_PROBE_ALLOW_NETWORK"):
        if original_env.get(key) is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = str(original_env[key])


def sanitize_reason_code(reason: Any) -> str:
    if reason is None:
        return "UNKNOWN_REASON"
    if isinstance(reason, str) and len(reason) <= 64 and "@" not in reason:
        return reason
    return type(reason).__name__


def _last_timestamp(candles: Any) -> int | None:
    if not isinstance(candles, list) or not candles or not isinstance(candles[-1], dict):
        return None
    return _as_int(candles[-1].get("from"))


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _git_check_ignore(path: Path) -> bool:
    return subprocess.run(["git", "check-ignore", str(path)], capture_output=True, text=True).returncode == 0


def _file_mode(path: Path) -> str | None:
    if not path.exists():
        return None
    return oct(stat.S_IMODE(path.stat().st_mode)).removeprefix("0o")


def _package_available(python: Path, package: str) -> bool:
    return subprocess.run([str(python), "-m", "pip", "show", package], capture_output=True, text=True).returncode == 0


def _python_version(python: Path) -> str:
    result = subprocess.run([str(python), "--version"], capture_output=True, text=True, check=False)
    return (result.stdout or result.stderr).strip()


def main() -> int:
    prevalidation = prevalidate_environment()
    if not prevalidation.safe:
        report = RealPracticeProbeReport(last_error_code=prevalidation.error_code)
        write_report(report)
        print(prevalidation.error_code)
        return 2
    report = run_real_practice_probe()
    write_report(report)
    print(report.last_error_code or "PROBE_COMPLETED")
    return 0 if report.last_error_code is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
