from __future__ import annotations

import contextlib
import importlib
import importlib.metadata
import io
import json
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
CONNECT_TIMEOUT_SECONDS = 8
ASSET_TIMEOUT_SECONDS = 6
CANDLE_TIMEOUT_SECONDS = 8


class PersistentIQOptionWorker:
    def __init__(self) -> None:
        self.client: Any | None = None
        self.guard: IQOptionReadOnlyRuntimeGuard | None = None
        self.connected = False
        self.connect_count = 0
        self.command_count = 0
        self.started_at = time.time()
        self.original_env = _sensitive_env_snapshot()
        self.realtime_streams: set[tuple[str, int]] = set()

    def run(self) -> int:
        for line in sys.stdin:
            raw = line.strip()
            if not raw:
                continue
            started = time.monotonic()
            request_id = _request_id(raw)
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
                response = self._handle_raw(raw)
            duration_ms = int((time.monotonic() - started) * 1000)
            data = response.get("data") or {}
            data["duration_ms"] = duration_ms
            sys.stdout.write(
                json.dumps(
                    {
                        "request_id": request_id,
                        "success": response["success"],
                        "data": data,
                        "error_code": response.get("error_code"),
                        "duration_ms": duration_ms,
                    },
                    separators=(",", ":"),
                )
                + "\n"
            )
            sys.stdout.flush()
            if response.get("stop"):
                break
        self._disconnect()
        cleanup_sensitive_env(self.original_env)
        return 0

    def _handle_raw(self, raw: str) -> dict[str, Any]:
        try:
            payload = json.loads(raw)
            request = parse_request(json.dumps({"command": payload.get("command"), "params": payload.get("params") or {}}))
        except Exception as exc:
            return fail(getattr(exc, "error_code", "WORKER_REQUEST_REJECTED"), self.guard)
        try:
            self.command_count += 1
            if request.command == "status":
                return ok(self._status_data())
            if request.command == "stop":
                return {**ok({"stopped": True, **self._status_data()}), "stop": True}
            if request.command == "disconnect":
                self._disconnect()
                return ok({"disconnect_status": "DISCONNECTED", **self._status_data()})
            if request.command == "connect":
                self._ensure_connected()
                return ok(self._connection_data())
            if request.command in {"list_assets", "list_otc_assets"}:
                self._ensure_connected()
                market_type = _market_type(request.params, default="OTC" if request.command == "list_otc_assets" else "REGULAR")
                assets = self._list_assets(market_type)
                return ok({**self._connection_data(), "provider": PROVIDER, "market_type": market_type, "assets": assets})
            if request.command == "get_candles":
                self._ensure_connected()
                symbol = _symbol(request.params)
                raw_size = _raw_size(request.params)
                limit = _limit(request.params)
                market_type = _market_type(request.params, default="OTC" if symbol.endswith("-OTC") else "REGULAR")
                candles = self._get_candles(symbol=symbol, raw_size=raw_size, limit=limit)
                return ok(
                    {
                        **self._connection_data(),
                        "provider": PROVIDER,
                        "market_type": market_type,
                        "symbol": symbol,
                        "raw_size": raw_size,
                        "count": len(candles),
                        "candles": candles,
                    }
                )
            if request.command == "start_realtime_candles":
                self._ensure_connected()
                symbol = _symbol(request.params)
                raw_size = _raw_size(request.params)
                maxdict = _maxdict(request.params)
                stream_started = self._start_realtime_candles(symbol=symbol, raw_size=raw_size, maxdict=maxdict)
                return ok({**self._connection_data(), "symbol": symbol, "raw_size": raw_size, "stream_started": stream_started, "source_mode": "NEAR_REALTIME"})
            if request.command == "get_realtime_candles":
                self._ensure_connected()
                symbol = _symbol(request.params)
                raw_size = _raw_size(request.params)
                candles = self._get_realtime_candles(symbol=symbol, raw_size=raw_size)
                return ok(
                    {
                        **self._connection_data(),
                        "provider": PROVIDER,
                        "symbol": symbol,
                        "raw_size": raw_size,
                        "count": len(candles),
                        "stream_active": (symbol, raw_size) in self.realtime_streams,
                        "source_mode": "NEAR_REALTIME" if candles else "NO_DATA",
                        "candles": candles,
                    }
                )
            if request.command == "stop_realtime_candles":
                self._ensure_connected()
                symbol = _symbol(request.params)
                raw_size = _raw_size(request.params)
                stream_stopped = self._stop_realtime_candles(symbol=symbol, raw_size=raw_size)
                return ok({**self._connection_data(), "symbol": symbol, "raw_size": raw_size, "stream_stopped": stream_stopped})
            return fail("WORKER_COMMAND_NOT_IMPLEMENTED", self.guard)
        except TimeoutError:
            return fail("IQ_OPTION_WORKER_TIMEOUT", self.guard)
        except RuntimeError as exc:
            if str(exc) == "READ_ONLY_VIOLATION":
                return fail("READ_ONLY_VIOLATION", self.guard)
            return fail("RuntimeError", self.guard)
        except Exception as exc:
            return fail(sanitized_exception_code(exc), self.guard)

    def _ensure_connected(self) -> None:
        if self.client is not None and self.connected:
            check_connect = getattr(self.client, "check_connect", None)
            if not callable(check_connect) or check_connect():
                return
        self._disconnect()
        IQ_Option = importlib.import_module("iqoptionapi.stable_api").IQ_Option
        env = load_secret_env(SECRET_ENV_PATH)
        self.client = IQ_Option(env["IQ_OPTION_EMAIL"], env["IQ_OPTION_PASSWORD"], active_account_type="PRACTICE")
        self.guard = IQOptionReadOnlyRuntimeGuard()
        self.guard.install(self.client)
        connected, reason = call_with_timeout(self.client.connect, timeout_seconds=CONNECT_TIMEOUT_SECONDS)
        if not connected:
            raise RuntimeError(sanitize_reason_code(reason))
        self.connected = True
        self.connect_count += 1

    def _disconnect(self) -> None:
        if self.client is not None:
            for symbol, raw_size in tuple(self.realtime_streams):
                self._stop_realtime_candles(symbol=symbol, raw_size=raw_size)
            close = getattr(self.client, "close", None)
            api_close = getattr(getattr(self.client, "api", None), "close", None)
            if callable(close):
                close()
            elif callable(api_close):
                api_close()
        if self.guard is not None and self.client is not None:
            self.guard.restore(self.client)
        self.client = None
        self.guard = None
        self.connected = False
        self.realtime_streams.clear()

    def _list_assets(self, market_type: str) -> list[dict[str, Any]]:
        return call_with_timeout(list_binary_turbo_assets, self.client, market_type=market_type, timeout_seconds=ASSET_TIMEOUT_SECONDS)

    def _get_candles(self, *, symbol: str, raw_size: int, limit: int) -> list[dict[str, Any]]:
        selected_raw: list[dict[str, Any]] = []
        for candidate_limit in _candidate_limits(limit):
            try:
                raw_candles = call_with_timeout(
                    self.client.get_candles,
                    symbol,
                    raw_size,
                    candidate_limit,
                    time.time(),
                    timeout_seconds=CANDLE_TIMEOUT_SECONDS,
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
            candle = normalized_iq_option_candle(item, symbol=symbol, raw_size=raw_size, category="persistent-worker")
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

    def _start_realtime_candles(self, *, symbol: str, raw_size: int, maxdict: int) -> bool:
        context = (symbol, raw_size)
        if context in self.realtime_streams:
            return True
        result = call_with_timeout(
            self.client.start_candles_stream,
            symbol,
            raw_size,
            maxdict,
            timeout_seconds=CANDLE_TIMEOUT_SECONDS + 20,
        )
        if result is False:
            return False
        self.realtime_streams.add(context)
        return True

    def _get_realtime_candles(self, *, symbol: str, raw_size: int) -> list[dict[str, Any]]:
        snapshot = call_with_timeout(
            self.client.get_realtime_candles,
            symbol,
            raw_size,
            timeout_seconds=3,
        )
        if not isinstance(snapshot, dict):
            return []
        candles: list[dict[str, Any]] = []
        for item in snapshot.values():
            if not isinstance(item, dict):
                continue
            candle = normalized_iq_option_candle(item, symbol=symbol, raw_size=raw_size, category="persistent-worker-realtime")
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
        return candles[-50:]

    def _stop_realtime_candles(self, *, symbol: str, raw_size: int) -> bool:
        context = (symbol, raw_size)
        if context not in self.realtime_streams:
            return True
        try:
            result = call_with_timeout(
                self.client.stop_candles_stream,
                symbol,
                raw_size,
                timeout_seconds=8,
            )
            return result is not False
        finally:
            self.realtime_streams.discard(context)

    def _status_data(self) -> dict[str, Any]:
        return {
            "provider": PROVIDER,
            "read_only": True,
            "isolated_worker": True,
            "persistent_worker": True,
            "connected": self.connected,
            "connect_count": self.connect_count,
            "command_count": self.command_count,
            "uptime_ms": int((time.time() - self.started_at) * 1000),
            "library_version": _library_version(),
            "python": sys.version.split()[0],
        }

    def _connection_data(self) -> dict[str, Any]:
        return {
            **self._status_data(),
            "passive_subscription_count": len(self.guard.passive_subscriptions) if self.guard else 0,
            "passive_subscription_names_sanitized": sorted(set(self.guard.passive_subscriptions))[:10] if self.guard else [],
            "read_only_method_calls": list(self.guard.called) if self.guard else [],
            "disconnect_status": "CONNECTED",
            "asset_discovery_scope": DISCOVERY_SCOPE,
            "realtime_stream_count": len(self.realtime_streams),
            "realtime_streams": [{"symbol": symbol, "raw_size": raw_size} for symbol, raw_size in sorted(self.realtime_streams)],
        }


def _request_id(raw: str) -> str | None:
    try:
        payload = json.loads(raw)
    except Exception:
        return None
    request_id = payload.get("request_id")
    return request_id if isinstance(request_id, str) and len(request_id) <= 80 else None


def _candidate_limits(limit: int) -> tuple[int, ...]:
    candidates = [value for value in BOOTSTRAP_LIMIT_CANDIDATES if value <= max(limit, 1)]
    if limit not in candidates:
        candidates.insert(0, limit)
    return tuple(dict.fromkeys(candidates))


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


def _maxdict(params: dict[str, Any]) -> int:
    maxdict = params.get("maxdict", 20)
    if not isinstance(maxdict, int) or maxdict <= 0:
        raise ValueError("INVALID_MAXDICT")
    return min(maxdict, 100)


def _market_type(params: dict[str, Any], *, default: str) -> str:
    market_type = params.get("market_type", default)
    if market_type not in {"OTC", "REGULAR"}:
        raise ValueError("UNSUPPORTED_MARKET_TYPE")
    return market_type


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


def main() -> int:
    return PersistentIQOptionWorker().run()


if __name__ == "__main__":
    raise SystemExit(main())
