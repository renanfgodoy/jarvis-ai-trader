from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Event, Lock, Thread
import time

from app.market.events.models import NormalizedMarketCandle
from app.market.providers.iq_option.provider import IQOptionMarketDataProvider
from app.market.providers.models import MarketAsset, MarketCandleBatch, MarketCandleRequest
from app.market.providers.models import ProviderCandle
from app.market.sanity import CandleSanityGuard
from app.market.store import CandleStore


@dataclass(frozen=True)
class IQOptionLoadResult:
    accepted: int
    rejected: int
    stored: int
    updated: int
    ignored: int
    last_error_code: str | None = None

    def sanitized(self) -> dict:
        return {
            "accepted": self.accepted,
            "rejected": self.rejected,
            "stored": self.stored,
            "updated": self.updated,
            "ignored": self.ignored,
            "last_error_code": self.last_error_code,
        }


@dataclass(frozen=True)
class IQOptionRealtimeResult:
    load: IQOptionLoadResult
    stream_started: bool
    source_mode: str
    symbol: str
    raw_size: int

    def sanitized(self) -> dict:
        return {
            "stream_started": self.stream_started,
            "source_mode": self.source_mode,
            "symbol": self.symbol,
            "raw_size": self.raw_size,
            **self.load.sanitized(),
        }


@dataclass(frozen=True)
class IQOptionRealtimeStreamSubscription:
    context: tuple[str, int, str]
    generation: int


@dataclass(frozen=True)
class IQOptionRealtimeStreamEvent:
    event_type: str
    provider: str
    market_type: str
    symbol: str
    raw_size: int
    source_mode: str
    sequence: int
    worker_received_at: int | None
    backend_published_at: int
    candle: ProviderCandle | None = None

    def sanitized(self) -> dict:
        payload = {
            "type": self.event_type,
            "provider": self.provider,
            "market_type": self.market_type,
            "symbol": self.symbol,
            "raw_size": self.raw_size,
            "source_mode": self.source_mode,
            "sequence": self.sequence,
            "provider_event_at": None,
            "worker_received_at": self.worker_received_at,
            "backend_published_at": self.backend_published_at,
        }
        if self.candle is not None:
            payload["candle"] = {
                "timestamp": self.candle.start_timestamp,
                "time": self.candle.start_timestamp,
                "open": self.candle.open,
                "high": self.candle.high,
                "low": self.candle.low,
                "close": self.candle.close,
            }
        return payload


@dataclass(frozen=True)
class IQOptionAssetCacheResult:
    assets: tuple[MarketAsset, ...]
    market_type: str
    from_cache: bool
    refreshed: bool
    duration_ms: int
    last_checked_at: str | None
    last_error_code: str | None = None

    def sanitized(self) -> dict:
        return {
            "market_type": self.market_type,
            "from_cache": self.from_cache,
            "refreshed": self.refreshed,
            "duration_ms": self.duration_ms,
            "last_checked_at": self.last_checked_at,
            "last_error_code": self.last_error_code,
        }


class IQOptionProviderRuntime:
    def __init__(self, provider: IQOptionMarketDataProvider, candle_store: CandleStore, sanity_guard: CandleSanityGuard) -> None:
        self._provider = provider
        self._candle_store = candle_store
        self._sanity_guard = sanity_guard
        self._lock = Lock()
        self._poll_stop = Event()
        self._poll_thread: Thread | None = None
        self._in_flight = False
        self._asset_cache: dict[str, tuple[MarketAsset, ...]] = {}
        self._asset_cache_checked_at: dict[str, str] = {}
        self._asset_cache_refreshing: set[str] = set()
        self._asset_cache_ttl_seconds = 45.0
        self._realtime_context: tuple[str, int, str] | None = None
        self._stream_active_context: tuple[str, int, str] | None = None
        self._stream_generation = 0
        self._stream_sequences: dict[tuple[str, int, str], int] = {}
        self._stream_subscribers: dict[tuple[str, int, str], int] = {}

    @property
    def provider(self) -> IQOptionMarketDataProvider:
        return self._provider

    def load_history(self, request: MarketCandleRequest) -> IQOptionLoadResult:
        with self._lock:
            if self._in_flight:
                return IQOptionLoadResult(accepted=0, rejected=0, stored=0, updated=0, ignored=0, last_error_code="REQUEST_IN_FLIGHT")
            self._in_flight = True
        try:
            batch = self._provider.get_candles(request)
            return self._store_batch(batch)
        finally:
            with self._lock:
                self._in_flight = False

    def load_realtime_update(self, request: MarketCandleRequest) -> IQOptionRealtimeResult:
        result, _batch, _worker_received_at = self._load_realtime_update_with_batch(request)
        return result

    def begin_realtime_stream(self, request: MarketCandleRequest) -> IQOptionRealtimeStreamSubscription:
        context = _context_for(request)
        with self._lock:
            if self._stream_active_context != context:
                self._stream_generation += 1
                self._stream_active_context = context
                self._stream_sequences[context] = 0
            self._stream_subscribers[context] = self._stream_subscribers.get(context, 0) + 1
            return IQOptionRealtimeStreamSubscription(context=context, generation=self._stream_generation)

    def end_realtime_stream(self, subscription: IQOptionRealtimeStreamSubscription) -> None:
        with self._lock:
            current_count = self._stream_subscribers.get(subscription.context, 0)
            if current_count <= 1:
                self._stream_subscribers.pop(subscription.context, None)
            else:
                self._stream_subscribers[subscription.context] = current_count - 1

    def next_realtime_stream_event(
        self,
        subscription: IQOptionRealtimeStreamSubscription,
        request: MarketCandleRequest,
        last_signature: tuple[int, float, float, float, float] | None,
    ) -> tuple[IQOptionRealtimeStreamEvent | None, tuple[int, float, float, float, float] | None]:
        if not self._is_current_stream(subscription):
            return None, last_signature
        result, batch, worker_received_at = self._load_realtime_update_with_batch(request)
        latest = batch.candles[-1] if batch.candles else None
        if latest is None:
            return None, last_signature
        signature = _candle_signature(latest)
        if signature == last_signature:
            return None, last_signature
        if not self._is_current_stream(subscription):
            return None, last_signature
        return (
            IQOptionRealtimeStreamEvent(
                event_type="candle",
                provider=batch.provider,
                market_type=batch.market_type,
                symbol=batch.symbol,
                raw_size=batch.raw_size,
                source_mode=result.source_mode,
                sequence=self._next_stream_sequence(subscription.context),
                worker_received_at=worker_received_at,
                backend_published_at=_epoch_ms(),
                candle=latest,
            ),
            signature,
        )

    def realtime_stream_heartbeat(
        self,
        subscription: IQOptionRealtimeStreamSubscription,
        request: MarketCandleRequest,
    ) -> IQOptionRealtimeStreamEvent | None:
        if not self._is_current_stream(subscription):
            return None
        return IQOptionRealtimeStreamEvent(
            event_type="heartbeat",
            provider="IQ_OPTION",
            market_type=request.market_type,
            symbol=request.symbol,
            raw_size=request.raw_size,
            source_mode="HEARTBEAT",
            sequence=self._next_stream_sequence(subscription.context),
            worker_received_at=None,
            backend_published_at=_epoch_ms(),
            candle=None,
        )

    def realtime_stream_status(self) -> dict:
        with self._lock:
            return {
                "active_context": _context_dict(self._stream_active_context),
                "generation": self._stream_generation,
                "subscribers": {
                    _context_label(context): count
                    for context, count in self._stream_subscribers.items()
                    if count > 0
                },
            }

    def is_realtime_stream_current(self, subscription: IQOptionRealtimeStreamSubscription) -> bool:
        return self._is_current_stream(subscription)

    def refresh_history_background(self, request: MarketCandleRequest) -> None:
        def run() -> None:
            self.load_history(request)

        Thread(target=run, name="iq-option-history-refresh", daemon=True).start()

    def list_assets_cached(self, market_type: str) -> IQOptionAssetCacheResult:
        started = time.monotonic()
        cached = self._asset_cache.get(market_type)
        if cached:
            if self._is_asset_cache_stale(market_type):
                self.refresh_assets_background(market_type)
            return IQOptionAssetCacheResult(
                assets=cached,
                market_type=market_type,
                from_cache=True,
                refreshed=False,
                duration_ms=int((time.monotonic() - started) * 1000),
                last_checked_at=self._asset_cache_checked_at.get(market_type),
            )
        try:
            assets = self.provider.list_assets(market_type=market_type)
            self._asset_cache[market_type] = assets
            self._asset_cache_checked_at[market_type] = _utcnow_iso()
            return IQOptionAssetCacheResult(
                assets=assets,
                market_type=market_type,
                from_cache=False,
                refreshed=True,
                duration_ms=int((time.monotonic() - started) * 1000),
                last_checked_at=self._asset_cache_checked_at.get(market_type),
            )
        except Exception as exc:
            return IQOptionAssetCacheResult(
                assets=(),
                market_type=market_type,
                from_cache=False,
                refreshed=False,
                duration_ms=int((time.monotonic() - started) * 1000),
                last_checked_at=None,
                last_error_code=getattr(exc, "error_code", "IQ_OPTION_ASSETS_FAILED"),
            )

    def refresh_assets_background(self, market_type: str) -> None:
        with self._lock:
            if market_type in self._asset_cache_refreshing:
                return
            self._asset_cache_refreshing.add(market_type)

        def run() -> None:
            try:
                assets = self.provider.list_assets(market_type=market_type)
                if assets:
                    self._asset_cache[market_type] = assets
                    self._asset_cache_checked_at[market_type] = _utcnow_iso()
            finally:
                with self._lock:
                    self._asset_cache_refreshing.discard(market_type)

        Thread(target=run, name=f"iq-option-assets-refresh-{market_type.lower()}", daemon=True).start()

    def runtime_status(self) -> dict:
        worker_status = {}
        try:
            worker_status = self.provider._client._api.status() if getattr(self.provider._client, "_api", None) is not None else {}
        except Exception:
            worker_status = {}
        return {
            "provider": "IQ_OPTION",
            "asset_cache_market_types": sorted(self._asset_cache.keys()),
            "asset_cache_counts": {market_type: len(assets) for market_type, assets in self._asset_cache.items()},
            "asset_cache_checked_at": dict(self._asset_cache_checked_at),
            "history_request_in_flight": self._in_flight,
            "worker": worker_status,
            "realtime_stream": self.realtime_stream_status(),
        }

    def _is_asset_cache_stale(self, market_type: str) -> bool:
        checked_at = self._asset_cache_checked_at.get(market_type)
        if checked_at is None:
            return True
        try:
            checked = datetime.fromisoformat(checked_at)
        except ValueError:
            return True
        return (datetime.now(timezone.utc) - checked).total_seconds() > self._asset_cache_ttl_seconds

    def start_polling(self, request: MarketCandleRequest, *, interval_seconds: float) -> None:
        self.stop_polling()
        self._poll_stop.clear()

        def run() -> None:
            while not self._poll_stop.wait(interval_seconds):
                self._provider.metrics.poll_cycles += 1
                result = self.load_history(request)
                if result.last_error_code:
                    self._provider.metrics.poll_failures += 1

        self._poll_thread = Thread(target=run, name="iq-option-read-only-poller", daemon=True)
        self._poll_thread.start()

    def stop_polling(self) -> None:
        self._poll_stop.set()
        if self._poll_thread and self._poll_thread.is_alive():
            self._poll_thread.join(timeout=2)
        self._poll_thread = None

    def stop_realtime(self) -> None:
        with self._lock:
            context = self._realtime_context
            self._realtime_context = None
        if context is None:
            return
        symbol, raw_size, market_type = context
        try:
            self._provider.stop_realtime_candles(MarketCandleRequest(symbol=symbol, raw_size=raw_size, limit=20, market_type=market_type))
        except Exception:
            pass

    def _ensure_realtime_context(self, request: MarketCandleRequest) -> None:
        next_context = (request.symbol, request.raw_size, request.market_type)
        if self._realtime_context == next_context:
            return
        if self._realtime_context is not None:
            symbol, raw_size, market_type = self._realtime_context
            try:
                self._provider.stop_realtime_candles(MarketCandleRequest(symbol=symbol, raw_size=raw_size, limit=20, market_type=market_type))
            except Exception:
                pass
        self._provider.start_realtime_candles(request)
        self._realtime_context = next_context

    def _load_realtime_update_with_batch(self, request: MarketCandleRequest) -> tuple[IQOptionRealtimeResult, MarketCandleBatch, int]:
        with self._lock:
            self._ensure_realtime_context(request)
            batch = self._provider.get_realtime_candles(request)
            worker_received_at = _epoch_ms()
            load_result = self._store_batch(batch)
        source_mode = _classify_realtime_source(batch, load_result)
        if source_mode != "STALE" and load_result.accepted > 0 and load_result.stored == 0 and load_result.updated == 0:
            source_mode = "SNAPSHOT"
        return (
            IQOptionRealtimeResult(
                load=load_result,
                stream_started=True,
                source_mode=source_mode,
                symbol=request.symbol,
                raw_size=request.raw_size,
            ),
            batch,
            worker_received_at,
        )

    def _is_current_stream(self, subscription: IQOptionRealtimeStreamSubscription) -> bool:
        with self._lock:
            return self._stream_active_context == subscription.context and self._stream_generation == subscription.generation

    def _next_stream_sequence(self, context: tuple[str, int, str]) -> int:
        with self._lock:
            next_sequence = self._stream_sequences.get(context, 0) + 1
            self._stream_sequences[context] = next_sequence
            return next_sequence

    def _store_batch(self, batch: MarketCandleBatch) -> IQOptionLoadResult:
        accepted = 0
        rejected = 0
        stored = 0
        updated = 0
        ignored = 0
        last_error_code = None
        for candle in batch.candles:
            normalized = _to_normalized(candle)
            sanity = self._sanity_guard.validate(normalized)
            if not sanity.accepted:
                rejected += 1
                last_error_code = sanity.error_code
                continue
            result = self._candle_store.add(normalized)
            accepted += 1
            if result.status == "added":
                stored += 1
            elif result.status == "updated":
                updated += 1
            elif result.status == "ignored":
                ignored += 1
        self._provider.metrics.candles_accepted += accepted
        self._provider.metrics.candles_rejected += rejected
        return IQOptionLoadResult(accepted=accepted, rejected=rejected, stored=stored, updated=updated, ignored=ignored, last_error_code=last_error_code)


def _to_normalized(candle) -> NormalizedMarketCandle:
    return NormalizedMarketCandle(
        active_id=None,
        symbol=candle.symbol,
        raw_size=candle.raw_size,
        timeframe=None,
        start_timestamp=candle.start_timestamp,
        end_timestamp=candle.end_timestamp,
        open=candle.open,
        close=candle.close,
        low_candidate=candle.low,
        high_candidate=candle.high,
        volume=float(candle.volume or 0),
        source="iq_option",
        source_event="iq-option-read-only-candles",
        source_verified=candle.source_verified,
        mapping_verified=True,
        mapping_notes=("IQ Option OTC read-only provider candle normalized from community API response.",),
    )


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _epoch_ms() -> int:
    return int(time.time() * 1000)


def _context_for(request: MarketCandleRequest) -> tuple[str, int, str]:
    return (request.symbol, request.raw_size, request.market_type)


def _context_label(context: tuple[str, int, str]) -> str:
    return f"{context[2]}:{context[0]}:{context[1]}"


def _context_dict(context: tuple[str, int, str] | None) -> dict | None:
    if context is None:
        return None
    symbol, raw_size, market_type = context
    return {"symbol": symbol, "raw_size": raw_size, "market_type": market_type}


def _candle_signature(candle: ProviderCandle) -> tuple[int, float, float, float, float]:
    return (candle.start_timestamp, candle.open, candle.high, candle.low, candle.close)


def _classify_realtime_source(batch: MarketCandleBatch, load_result: IQOptionLoadResult) -> str:
    if load_result.accepted <= 0 or not batch.candles:
        return "NO_DATA"
    latest_timestamp = max(candle.start_timestamp for candle in batch.candles)
    raw_size = batch.raw_size if batch.raw_size > 0 else 60
    if time.time() - latest_timestamp > raw_size * 3:
        return "STALE"
    return "NEAR_REALTIME"
