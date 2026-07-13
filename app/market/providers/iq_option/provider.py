from __future__ import annotations

from datetime import datetime, timezone

from app.market.providers.errors import ProviderDisabledError, ProviderValidationError
from app.market.providers.iq_option.client import IQOptionReadOnlyClient, LIBRARY_SOURCE
from app.market.providers.iq_option.config import IQOptionProviderConfig
from app.market.providers.iq_option.mapper import MARKET_TYPE_OTC, PROVIDER_NAME, SUPPORTED_MARKET_TYPES, SUPPORTED_RAW_SIZES, map_assets, map_candles
from app.market.providers.iq_option.status import IQOptionProviderMetrics
from app.market.providers.models import MarketAsset, MarketCandleBatch, MarketCandleRequest, MarketProviderStatus


class IQOptionMarketDataProvider:
    provider_name = PROVIDER_NAME

    def __init__(self, config: IQOptionProviderConfig, client: IQOptionReadOnlyClient, metrics: IQOptionProviderMetrics | None = None) -> None:
        self._config = config
        self._client = client
        self._metrics = metrics or IQOptionProviderMetrics()
        self._connected = False
        self._last_connected_at: str | None = None
        self._last_candle_at: str | None = None
        self._last_symbol: str | None = None
        self._last_raw_size: int | None = None
        self._last_batch_count = 0
        self._last_error_code: str | None = None

    @property
    def metrics(self) -> IQOptionProviderMetrics:
        return self._metrics

    def connect(self) -> MarketProviderStatus:
        if not self._config.enabled:
            self._last_error_code = "PROVIDER_DISABLED"
            raise ProviderDisabledError("IQ Option provider is disabled.")
        try:
            self._client.connect()
            self._connected = True
            self._metrics.connections += 1
            self._last_connected_at = _utcnow_iso()
            self._last_error_code = None
        except Exception as exc:
            self._connected = False
            self._metrics.connection_failures += 1
            self._last_error_code = getattr(exc, "error_code", "PROVIDER_CONNECTION_FAILED")
            raise
        return self.connection_status()

    def disconnect(self) -> MarketProviderStatus:
        self._client.disconnect()
        self._connected = False
        return self.connection_status()

    def connection_status(self) -> MarketProviderStatus:
        connected = self._connected and self._client.is_connected()
        return MarketProviderStatus(
            provider=PROVIDER_NAME,
            enabled=self._config.enabled,
            configured=self._config.configured or self._client.uses_isolated_worker,
            connected=connected,
            account_mode=self._config.account_mode,
            read_only=self._config.read_only,
            last_connected_at=self._last_connected_at,
            last_candle_at=self._last_candle_at,
            last_symbol=self._last_symbol,
            last_raw_size=self._last_raw_size,
            last_batch_count=self._last_batch_count,
            reconnect_count=self._metrics.reconnects,
            last_error_code=self._last_error_code,
            library_source=LIBRARY_SOURCE,
            library_version=self._client.library_version,
        )

    def list_assets(self, market_type: str = MARKET_TYPE_OTC) -> tuple[MarketAsset, ...]:
        if market_type not in SUPPORTED_MARKET_TYPES:
            raise ProviderValidationError("UNSUPPORTED_MARKET_TYPE")
        self._metrics.asset_requests += 1
        payload = self._client.list_assets(market_type=market_type)
        return map_assets(payload, market_type=market_type)

    def get_candles(self, request: MarketCandleRequest) -> MarketCandleBatch:
        if request.raw_size not in SUPPORTED_RAW_SIZES:
            raise ProviderValidationError("UNSUPPORTED_TIMEFRAME")
        if request.market_type not in SUPPORTED_MARKET_TYPES:
            raise ProviderValidationError("UNSUPPORTED_MARKET_TYPE")
        self._metrics.candle_requests += 1
        raw_candles = self._client.get_candles(request.symbol, request.raw_size, request.limit)
        candles = map_candles(request.symbol, request.raw_size, raw_candles, market_type=request.market_type)
        self._metrics.candle_batches += 1
        self._metrics.candles_received += len(raw_candles)
        self._last_symbol = request.symbol
        self._last_raw_size = request.raw_size
        self._last_batch_count = len(candles)
        self._last_candle_at = _utcnow_iso() if candles else self._last_candle_at
        return MarketCandleBatch(
            provider=PROVIDER_NAME,
            market_type=request.market_type,
            symbol=request.symbol,
            raw_size=request.raw_size,
            candles=candles,
        )

    def start_realtime_candles(self, request: MarketCandleRequest) -> dict:
        if request.raw_size not in SUPPORTED_RAW_SIZES:
            raise ProviderValidationError("UNSUPPORTED_TIMEFRAME")
        if request.market_type not in SUPPORTED_MARKET_TYPES:
            raise ProviderValidationError("UNSUPPORTED_MARKET_TYPE")
        return self._client.start_realtime_candles(request.symbol, request.raw_size, maxdict=min(max(request.limit, 20), 100))

    def get_realtime_candles(self, request: MarketCandleRequest) -> MarketCandleBatch:
        if request.raw_size not in SUPPORTED_RAW_SIZES:
            raise ProviderValidationError("UNSUPPORTED_TIMEFRAME")
        if request.market_type not in SUPPORTED_MARKET_TYPES:
            raise ProviderValidationError("UNSUPPORTED_MARKET_TYPE")
        raw_candles = self._client.get_realtime_candles(request.symbol, request.raw_size)
        candles = map_candles(request.symbol, request.raw_size, raw_candles, market_type=request.market_type)
        self._last_symbol = request.symbol
        self._last_raw_size = request.raw_size
        self._last_batch_count = len(candles)
        self._last_candle_at = _utcnow_iso() if candles else self._last_candle_at
        return MarketCandleBatch(
            provider=PROVIDER_NAME,
            market_type=request.market_type,
            symbol=request.symbol,
            raw_size=request.raw_size,
            candles=candles,
        )

    def stop_realtime_candles(self, request: MarketCandleRequest) -> dict:
        if request.raw_size not in SUPPORTED_RAW_SIZES:
            raise ProviderValidationError("UNSUPPORTED_TIMEFRAME")
        if request.market_type not in SUPPORTED_MARKET_TYPES:
            raise ProviderValidationError("UNSUPPORTED_MARKET_TYPE")
        return self._client.stop_realtime_candles(request.symbol, request.raw_size)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
