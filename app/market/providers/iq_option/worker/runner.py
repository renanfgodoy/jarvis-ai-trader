from __future__ import annotations

import contextlib
import io
import importlib
import importlib.metadata
import sys
import time
from typing import Any

from app.market.providers.iq_option.real_probe import (
    BOOTSTRAP_LIMIT_CANDIDATES,
    IQOptionReadOnlyRuntimeGuard,
    SECRET_ENV_PATH,
    call_with_timeout,
    cleanup_sensitive_env,
    load_secret_env,
    normalized_iq_option_candle,
    sanitize_reason_code,
    sanitized_exception_code,
)
from app.market.providers.iq_option.worker.asset_discovery import DISCOVERY_SCOPE, list_binary_turbo_assets
from app.market.providers.iq_option.worker.protocol import encode_response, parse_request

PROVIDER = "IQ_OPTION"
SUPPORTED_RAW_SIZES = {60, 300, 900}
DEFAULT_TIMEOUT_SECONDS = 30


def main() -> int:
    raw_request = sys.stdin.read()
    try:
        request = parse_request(raw_request)
    except Exception as exc:
        sys.stdout.write(encode_response(False, error_code=getattr(exc, "error_code", "WORKER_REQUEST_REJECTED")))
        return 2

    output_buffer = io.StringIO()
    error_buffer = io.StringIO()
    with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
        response = dispatch(request.command, request.params)
    sys.stdout.write(encode_response(response["success"], response.get("data"), response.get("error_code")))
    return 0 if response["success"] else 2


def dispatch(command: str, params: dict[str, Any]) -> dict[str, Any]:
    if command == "status":
        return ok(
            {
                "provider": PROVIDER,
                "read_only": True,
                "isolated_worker": True,
                "library_version": _library_version(),
                "python": sys.version.split()[0],
            }
        )
    if command == "disconnect":
        return ok({"disconnect_status": "DISCONNECTED", "isolated_worker": True})

    client = None
    guard = None
    original_env = _sensitive_env_snapshot()
    try:
        IQ_Option = importlib.import_module("iqoptionapi.stable_api").IQ_Option

        env = load_secret_env(SECRET_ENV_PATH)
        client = IQ_Option(env["IQ_OPTION_EMAIL"], env["IQ_OPTION_PASSWORD"], active_account_type="PRACTICE")
        guard = IQOptionReadOnlyRuntimeGuard()
        guard.install(client)
        connected, reason = call_with_timeout(client.connect, timeout_seconds=DEFAULT_TIMEOUT_SECONDS)
        if not connected:
            return fail(sanitize_reason_code(reason), guard)

        if command == "connect":
            return ok(_connection_data(guard))
        if command in {"list_assets", "list_otc_assets"}:
            market_type = _market_type(params, default="OTC" if command == "list_otc_assets" else "REGULAR")
            assets = _list_assets(client, market_type=market_type)
            return ok({**_connection_data(guard), "provider": PROVIDER, "market_type": market_type, "assets": assets})
        if command == "get_candles":
            symbol = _symbol(params)
            raw_size = _raw_size(params)
            limit = _limit(params)
            candles = _get_candles(client, symbol=symbol, raw_size=raw_size, limit=limit)
            return ok(
                {
                    **_connection_data(guard),
                    "provider": PROVIDER,
                    "symbol": symbol,
                    "raw_size": raw_size,
                    "count": len(candles),
                    "candles": candles,
                }
            )
        return fail("WORKER_COMMAND_NOT_IMPLEMENTED", guard)
    except TimeoutError:
        return fail("IQ_OPTION_WORKER_TIMEOUT", guard)
    except RuntimeError as exc:
        if str(exc) == "READ_ONLY_VIOLATION":
            return fail("READ_ONLY_VIOLATION", guard)
        return fail("RuntimeError", guard)
    except Exception as exc:
        return fail(sanitized_exception_code(exc), guard)
    finally:
        if client is not None:
            _disconnect(client)
        if guard is not None and client is not None:
            guard.restore(client)
        cleanup_sensitive_env(original_env)


def _list_assets(client: Any, *, market_type: str) -> list[dict[str, Any]]:
    return call_with_timeout(list_binary_turbo_assets, client, market_type=market_type, timeout_seconds=DEFAULT_TIMEOUT_SECONDS)


def _get_candles(client: Any, *, symbol: str, raw_size: int, limit: int) -> list[dict[str, Any]]:
    selected_raw: list[dict[str, Any]] = []
    for candidate_limit in _candidate_limits(limit):
        try:
            raw_candles = call_with_timeout(
                client.get_candles,
                symbol,
                raw_size,
                candidate_limit,
                time.time(),
                timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
            )
        except Exception:
            continue
        if isinstance(raw_candles, list) and raw_candles:
            selected_raw = raw_candles
            break
    candles: list[dict[str, Any]] = []
    for item in selected_raw:
        if not isinstance(item, dict):
            continue
        candle = normalized_iq_option_candle(item, symbol=symbol, raw_size=raw_size, category="worker")
        if candle is None:
            continue
        candles.append(
            {
                "from": candle.start_timestamp,
                "to": candle.end_timestamp,
                "open": candle.open,
                "max": candle.high_candidate,
                "min": candle.low_candidate,
                "close": candle.close,
                "volume": candle.volume,
            }
        )
    return candles[-limit:]


def _candidate_limits(limit: int) -> tuple[int, ...]:
    candidates = [value for value in BOOTSTRAP_LIMIT_CANDIDATES if value <= max(limit, 1)]
    if limit not in candidates:
        candidates.insert(0, limit)
    return tuple(dict.fromkeys(candidates))


def _connection_data(guard: IQOptionReadOnlyRuntimeGuard) -> dict[str, Any]:
    return {
        "connected": True,
        "read_only": True,
        "passive_subscription_count": len(guard.passive_subscriptions),
        "passive_subscription_names_sanitized": sorted(set(guard.passive_subscriptions))[:10],
        "read_only_method_calls": list(guard.called),
        "disconnect_status": "DISCONNECTED",
        "asset_discovery_scope": DISCOVERY_SCOPE,
    }


def _symbol(params: dict[str, Any]) -> str:
    symbol = params.get("symbol")
    if not isinstance(symbol, str) or not symbol:
        raise ValueError("INVALID_SYMBOL")
    return symbol


def _raw_size(params: dict[str, Any]) -> int:
    raw_size = params.get("raw_size")
    if not isinstance(raw_size, int) or raw_size not in SUPPORTED_RAW_SIZES:
        raise ValueError("UNSUPPORTED_TIMEFRAME")
    return raw_size


def _limit(params: dict[str, Any]) -> int:
    limit = params.get("limit", 1000)
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("INVALID_LIMIT")
    return min(limit, 5000)


def _market_type(params: dict[str, Any], *, default: str) -> str:
    market_type = params.get("market_type", default)
    if market_type not in {"OTC", "REGULAR"}:
        raise ValueError("UNSUPPORTED_MARKET_TYPE")
    return market_type


def _disconnect(client: Any) -> None:
    close = getattr(client, "close", None)
    api_close = getattr(getattr(client, "api", None), "close", None)
    if callable(close):
        close()
    elif callable(api_close):
        api_close()


def _library_version() -> str | None:
    try:
        return importlib.metadata.version("iqoptionapi")
    except importlib.metadata.PackageNotFoundError:
        return None


def _sensitive_env_snapshot() -> dict[str, str | None]:
    import os

    return {
        "IQ_OPTION_EMAIL": os.environ.get("IQ_OPTION_EMAIL"),
        "IQ_OPTION_PASSWORD": os.environ.get("IQ_OPTION_PASSWORD"),
        "IQ_OPTION_ACCOUNT_MODE": os.environ.get("IQ_OPTION_ACCOUNT_MODE"),
        "IQ_OPTION_PROBE_ALLOW_NETWORK": os.environ.get("IQ_OPTION_PROBE_ALLOW_NETWORK"),
    }


def ok(data: dict[str, Any]) -> dict[str, Any]:
    return {"success": True, "data": data, "error_code": None}


def fail(error_code: str, guard: IQOptionReadOnlyRuntimeGuard | None) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if guard is not None:
        data = {
            "read_only_method_calls": list(guard.called),
            "passive_subscription_count": len(guard.passive_subscriptions),
            "passive_subscription_names_sanitized": sorted(set(guard.passive_subscriptions))[:10],
        }
    return {"success": False, "data": data, "error_code": error_code}


if __name__ == "__main__":
    raise SystemExit(main())
