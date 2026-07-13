from __future__ import annotations

import importlib.metadata
import time
from typing import Any

from app.market.providers.errors import ProviderConnectionError, ProviderCredentialsMissingError, ProviderRequestError
from app.market.providers.iq_option.config import IQOptionProviderConfig
from app.market.providers.iq_option.worker.asset_discovery import list_binary_turbo_assets
from app.market.providers.iq_option.worker import IQOptionIsolatedWorkerClient

LIBRARY_SOURCE = "iqoptionapi/iqoptionapi GitHub community API; PyPI iqoptionapi 0.5 exists but is stale"


class IQOptionReadOnlyClient:
    """Narrow read-only wrapper around the community IQ Option API."""

    def __init__(self, config: IQOptionProviderConfig, *, api_factory: Any | None = None) -> None:
        self._config = config
        self._api_factory = api_factory
        self._api: Any | None = None

    @property
    def uses_isolated_worker(self) -> bool:
        return self._api_factory is None

    @property
    def library_version(self) -> str | None:
        if self._api_factory is None:
            return "isolated-worker"
        try:
            return importlib.metadata.version("iqoptionapi")
        except importlib.metadata.PackageNotFoundError:
            return None

    def connect(self) -> None:
        if self._api_factory is not None and not self._config.configured:
            raise ProviderCredentialsMissingError("IQ Option credentials are not configured.")
        api = self._build_api()
        if hasattr(api, "set_max_reconnect"):
            api.set_max_reconnect(3)
        status, reason = api.connect()
        if not status:
            raise ProviderConnectionError(str(reason or "IQ_OPTION_CONNECT_FAILED"))
        self._api = api

    def disconnect(self) -> None:
        if self._api is not None and hasattr(self._api, "close"):
            self._api.close()
        self._api = None

    def is_connected(self) -> bool:
        return bool(self._api is not None and getattr(self._api, "check_connect", lambda: False)())

    def list_assets(self, market_type: str = "OTC") -> list[dict[str, Any]]:
        api = self._ensure_api()
        list_assets = getattr(api, "list_assets", None)
        if callable(list_assets):
            try:
                return list_assets(market_type)
            except Exception as exc:
                raise ProviderRequestError("IQ_OPTION_ASSETS_FAILED") from exc
        try:
            return list_binary_turbo_assets(api, market_type=market_type)
        except Exception as exc:
            raise ProviderRequestError("IQ_OPTION_ASSETS_FAILED") from exc

    def get_candles(self, symbol: str, raw_size: int, limit: int) -> list[dict[str, Any]]:
        api = self._ensure_api()
        try:
            return api.get_candles(symbol, raw_size, limit, time.time())
        except Exception as exc:
            raise ProviderRequestError("IQ_OPTION_CANDLES_FAILED") from exc

    def start_realtime_candles(self, symbol: str, raw_size: int, maxdict: int = 20) -> dict[str, Any]:
        api = self._ensure_api()
        start = getattr(api, "start_realtime_candles", None)
        if callable(start):
            try:
                return start(symbol, raw_size, maxdict)
            except Exception as exc:
                raise ProviderRequestError("IQ_OPTION_REALTIME_START_FAILED") from exc
        try:
            result = api.start_candles_stream(symbol, raw_size, maxdict)
        except Exception as exc:
            raise ProviderRequestError("IQ_OPTION_REALTIME_START_FAILED") from exc
        return {"stream_started": result is not False, "symbol": symbol, "raw_size": raw_size}

    def get_realtime_candles(self, symbol: str, raw_size: int) -> list[dict[str, Any]]:
        api = self._ensure_api()
        get_realtime = getattr(api, "get_realtime_candles", None)
        if not callable(get_realtime):
            raise ProviderRequestError("IQ_OPTION_REALTIME_UNAVAILABLE")
        try:
            payload = get_realtime(symbol, raw_size)
        except Exception as exc:
            raise ProviderRequestError("IQ_OPTION_REALTIME_FAILED") from exc
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return [item for item in payload.values() if isinstance(item, dict)]
        return []

    def stop_realtime_candles(self, symbol: str, raw_size: int) -> dict[str, Any]:
        api = self._ensure_api()
        stop = getattr(api, "stop_realtime_candles", None)
        if callable(stop):
            try:
                return stop(symbol, raw_size)
            except Exception as exc:
                raise ProviderRequestError("IQ_OPTION_REALTIME_STOP_FAILED") from exc
        try:
            result = api.stop_candles_stream(symbol, raw_size)
        except Exception as exc:
            raise ProviderRequestError("IQ_OPTION_REALTIME_STOP_FAILED") from exc
        return {"stream_stopped": result is not False, "symbol": symbol, "raw_size": raw_size}

    def _ensure_api(self) -> Any:
        if self._api is None:
            raise ProviderConnectionError("IQ_OPTION_NOT_CONNECTED")
        return self._api

    def _build_api(self) -> Any:
        if self._api_factory is None:
            return IQOptionIsolatedWorkerClient()
        return self._api_factory(self._config.email, self._config.password)
