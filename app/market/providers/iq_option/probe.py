from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
from typing import Any, Callable, Mapping

from app.market.providers.iq_option.mapper import map_assets, map_candles

PINNED_REPOSITORY_URL = "https://github.com/iqoptionapi/iqoptionapi.git"
PINNED_COMMIT_SHA = "8a903cc094a74af1ed935a56a2d6b5a9ed3319d7"
PROBE_VENV_PATH = ".jarvis_cache/iq_option_probe_venv"
NETWORK_FLAG = "IQ_OPTION_PROBE_ALLOW_NETWORK"
CREDENTIAL_ENV_KEYS = ("IQ_OPTION_EMAIL", "IQ_OPTION_PASSWORD")
SUPPORTED_PROBE_RAW_SIZES = (60, 300, 900)
FORBIDDEN_RUNTIME_METHODS = (
    "buy",
    "buy_multi",
    "buy_digital",
    "buy_digital_" + "spot",
    "buy_digital_" + "spot_v2",
    "buy_order",
    "sell_" + "option",
    "sell_digital_" + "option",
    "close_" + "position",
    "change_balance",
    "reset_practice_" + "balance",
    "get_balance",
    "get_balances",
    "get_balance_id",
    "get_balance_mode",
)


@dataclass(frozen=True)
class ProbeDependencyVersions:
    python_version: str
    pip_version: str
    iqoptionapi_version: str | None
    websocket_client_version: str | None
    requests_version: str | None
    urllib3_version: str | None
    certifi_version: str | None


@dataclass(frozen=True)
class CandleProbeSummary:
    raw_size: int
    count: int
    timestamps_ordered: bool
    timestamps_distinct: bool
    ohlc_fields_present: bool
    first_timestamp: int | None
    last_timestamp: int | None


def network_enabled(environ: Mapping[str, str | None]) -> bool:
    return environ.get(NETWORK_FLAG) == "true"


def credentials_configured(environ: Mapping[str, str | None]) -> bool:
    return all(bool(environ.get(key)) for key in CREDENTIAL_ENV_KEYS)


def sanitized_exception_code(exc: BaseException) -> str:
    return type(exc).__name__ or "UNKNOWN_ERROR"


def dependency_versions(*, python_version: str, pip_version: str) -> ProbeDependencyVersions:
    return ProbeDependencyVersions(
        python_version=python_version,
        pip_version=pip_version,
        iqoptionapi_version=_distribution_version("iqoptionapi"),
        websocket_client_version=_distribution_version("websocket-client"),
        requests_version=_distribution_version("requests"),
        urllib3_version=_distribution_version("urllib3"),
        certifi_version=_distribution_version("certifi"),
    )


def build_client_safely(factory: Callable[[str, str], Any], email: str | None, password: str | None) -> str:
    if not email or not password:
        return "CREDENTIALS_MISSING"
    try:
        factory(email, password)
    except Exception as exc:  # pragma: no cover - defensive sanitizer surface
        return sanitized_exception_code(exc)
    return "CLIENT_CREATED"


def summarize_otc_assets(open_time_payload: dict[str, Any], *, limit: int = 10) -> dict[str, Any]:
    assets = map_assets(open_time_payload)
    return {
        "otc_assets_count": len(assets),
        "sample_symbols": [asset.symbol for asset in assets[:limit]],
    }


def summarize_candles(symbol: str, raw_size: int, raw_candles: list[dict[str, Any]]) -> CandleProbeSummary:
    candles = map_candles(symbol, raw_size, raw_candles)
    timestamps = [candle.start_timestamp for candle in candles]
    return CandleProbeSummary(
        raw_size=raw_size,
        count=len(candles),
        timestamps_ordered=timestamps == sorted(timestamps),
        timestamps_distinct=len(timestamps) == len(set(timestamps)),
        ohlc_fields_present=len(candles) == len(raw_candles),
        first_timestamp=timestamps[0] if timestamps else None,
        last_timestamp=timestamps[-1] if timestamps else None,
    )


def forbidden_methods_present(api_object: Any) -> tuple[str, ...]:
    available = set(dir(api_object))
    return tuple(method for method in FORBIDDEN_RUNTIME_METHODS if method in available)


class ReadOnlyMethodGuard:
    def __init__(self) -> None:
        self.called_methods: list[str] = []

    def __getattr__(self, name: str) -> Callable[..., None]:
        if name in FORBIDDEN_RUNTIME_METHODS:
            def blocked(*_args: Any, **_kwargs: Any) -> None:
                self.called_methods.append(name)
                raise RuntimeError("READ_ONLY_VIOLATION")

            return blocked
        raise AttributeError(name)


def contains_sensitive_value(report: str, values: tuple[str | None, ...]) -> bool:
    return any(value in report for value in values if value)


def _distribution_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None
