from __future__ import annotations

from typing import Mapping

from app.market.providers.base import (
    BaseProvider,
    ProviderAsset,
    ProviderAssets,
    ProviderCandle,
    ProviderContext,
    ProviderHealth,
    ProviderHistory,
    ProviderReadiness,
    ProviderStatus,
    ProviderTick,
)
from app.market.providers.pocket.metrics import PocketRuntimeMetrics
from app.market.providers.pocket.models import PocketAssetCatalog
from app.market.providers.pocket.runtime import PocketMarketRuntime
from app.market.providers.pocket.session_context import PocketSessionContext
from tools.pocket_parser.models import PocketAssetInfo, PocketNormalizedCandle, PocketRealtimeTick


def _provider_status(connection_state: str) -> ProviderStatus:
    if connection_state in {"ONLINE", "AUTHORIZED_REPLAY"}:
        return "online"
    if connection_state in {"STARTING", "CONNECTING", "RECONNECTING"}:
        return "starting"
    if connection_state in {"OFFLINE", "ERROR"}:
        return "error" if connection_state == "ERROR" else "degraded"
    return "stopped"


def pocket_context_to_provider_context(context: PocketSessionContext) -> ProviderContext:
    return ProviderContext(
        provider=context.provider,
        asset=context.asset,
        symbol=context.display_name or context.asset,
        timeframe=context.timeframe,
        period=context.period,
        connection_state=_provider_status(context.connection_state),
        history_state=context.history_state,
        readiness="BLOCKED" if context.analysis_blocked else "READY",
        last_price=context.last_price,
        history_count=context.history_count,
        timestamp=int(context.last_update) if context.last_update is not None else None,
        metadata={
            "session_state": context.session_state,
            "market_type": context.market_type,
            "is_otc": context.is_otc,
            "bootstrap_complete": context.bootstrap_complete,
            "analysis_block_reason": context.analysis_block_reason,
        },
    )


def pocket_tick_to_provider_tick(tick: PocketRealtimeTick, period: int | None = None) -> ProviderTick:
    return ProviderTick(
        provider="POCKET",
        symbol=tick.asset,
        period=period,
        timestamp=int(tick.timestamp),
        price=tick.price,
        source=tick.source_event,
        sequence=tick.sequence,
    )


def pocket_candle_to_provider_candle(candle: PocketNormalizedCandle) -> ProviderCandle:
    return ProviderCandle(
        provider=candle.provider,
        symbol=candle.symbol,
        period=candle.period,
        timestamp=int(candle.timestamp),
        open=candle.open,
        high=candle.high,
        low=candle.low,
        close=candle.close,
        volume=candle.volume,
        source=candle.source_event,
        is_closed=candle.is_closed,
    )


def pocket_asset_to_provider_asset(asset: PocketAssetInfo) -> ProviderAsset:
    return ProviderAsset(
        provider="POCKET",
        symbol=asset.symbol,
        display_name=asset.display_name,
        market_type=asset.market_type,
        supported_periods=asset.supported_periods,
        is_open=bool(asset.is_available),
        metadata={
            "is_otc": asset.is_otc,
            "schema": "pocket_asset_info",
        },
    )


def pocket_catalog_to_provider_assets(catalog: PocketAssetCatalog) -> ProviderAssets:
    return ProviderAssets(
        provider="POCKET",
        assets=tuple(pocket_asset_to_provider_asset(asset) for asset in catalog.assets),
        timestamp=None,
        source="pocket_runtime_asset_catalog",
    )


def pocket_metrics_to_provider_health(metrics: PocketRuntimeMetrics, context: PocketSessionContext, last_error: str | None) -> ProviderHealth:
    return ProviderHealth(
        provider=context.provider,
        status=_provider_status(context.connection_state),
        read_only=True,
        last_error_code=last_error,
        metrics={
            "events_received": metrics.events_received,
            "events_processed": metrics.events_processed,
            "events_rejected": metrics.events_rejected,
            "history_batches": metrics.history_batches,
            "historical_candles_written": metrics.historical_candles_written,
            "ticks_processed": metrics.ticks_processed,
            "guard_blocks": metrics.guard_blocks,
        },
    )


class PocketProviderAdapter(BaseProvider):
    def __init__(self, runtime: PocketMarketRuntime | None = None) -> None:
        super().__init__(
            "POCKET",
            capabilities=frozenset({"assets", "history", "ticks", "realtime", "read_only"}),
        )
        self.runtime = runtime or PocketMarketRuntime()

    def start(self) -> None:
        self.runtime.start(live_connection=False)

    def stop(self) -> None:
        self.runtime.stop()

    def status(self) -> ProviderContext:
        return self.get_context()

    def get_context(self) -> ProviderContext:
        return pocket_context_to_provider_context(self.runtime.context)

    def get_assets(self) -> ProviderAssets:
        return pocket_catalog_to_provider_assets(self.runtime.asset_catalog)

    def get_history(self, symbol: str, period: int, limit: int | None = None) -> ProviderHistory:
        key = self.runtime.store.key(symbol, period)
        stored_candles = self.runtime.store.candles(key)
        if limit is not None:
            stored_candles = stored_candles[-limit:]
        candles = tuple(
            ProviderCandle(
                provider=candle.provider,
                symbol=candle.asset,
                period=candle.period,
                timestamp=int(candle.timestamp),
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                source=candle.source_event,
                is_closed=not candle.is_realtime,
            )
            for candle in stored_candles
        )
        return ProviderHistory(
            provider="POCKET",
            symbol=symbol,
            period=period,
            candles=candles,
            history_count=self.runtime.readiness.count_for(key),
            timestamp=candles[-1].timestamp if candles else None,
            source="pocket_runtime_store",
        )

    def get_ticks(self, symbol: str, period: int, limit: int | None = None) -> tuple[ProviderTick, ...]:
        if self.runtime.context.asset != symbol or self.runtime.context.last_price is None or self.runtime.context.last_update is None:
            return ()
        return (
            ProviderTick(
                provider="POCKET",
                symbol=symbol,
                period=period,
                timestamp=int(self.runtime.context.last_update),
                price=self.runtime.context.last_price,
                source="pocket_runtime_context",
            ),
        )

    def get_readiness(self, symbol: str, period: int) -> ProviderReadiness:
        key = self.runtime.store.key(symbol, period)
        history_count = self.runtime.readiness.count_for(key)
        state = self.runtime.readiness.state_for(key)
        return ProviderReadiness(
            provider="POCKET",
            symbol=symbol,
            period=period,
            state=state,
            history_count=history_count,
            required_history_count=self.runtime.config.pocket_history_required,
            analysis_blocked=state != "READY",
            reason=None if state == "READY" else "POCKET_HISTORY_NOT_READY",
        )

    def health(self) -> ProviderHealth:
        return pocket_metrics_to_provider_health(self.runtime.metrics, self.runtime.context, self.runtime.last_error)


class FakePocketProviderAdapter(PocketProviderAdapter):
    def __init__(
        self,
        *,
        context: PocketSessionContext | None = None,
        catalog: PocketAssetCatalog | None = None,
        history: Mapping[tuple[str, int], tuple[ProviderCandle, ...]] | None = None,
        ticks: Mapping[tuple[str, int], tuple[ProviderTick, ...]] | None = None,
    ) -> None:
        super().__init__(PocketMarketRuntime())
        if context is not None:
            self.runtime.context = context
        if catalog is not None:
            self.runtime.asset_catalog = catalog
        self._history = dict(history or {})
        self._ticks = dict(ticks or {})

    def get_history(self, symbol: str, period: int, limit: int | None = None) -> ProviderHistory:
        candles = self._history.get((symbol, period), ())
        if limit is not None:
            candles = candles[-limit:]
        return ProviderHistory(
            provider="POCKET",
            symbol=symbol,
            period=period,
            candles=candles,
            history_count=len(candles),
            timestamp=candles[-1].timestamp if candles else None,
            source="fake_pocket_provider_adapter",
        )

    def get_ticks(self, symbol: str, period: int, limit: int | None = None) -> tuple[ProviderTick, ...]:
        ticks = self._ticks.get((symbol, period), ())
        if limit is not None:
            return ticks[-limit:]
        return ticks


def build_pocket_provider_adapter(config: Mapping[str, object] | None = None) -> PocketProviderAdapter:
    runtime = (config or {}).get("runtime")
    if runtime is not None and not isinstance(runtime, PocketMarketRuntime):
        raise TypeError("runtime must be a PocketMarketRuntime instance")
    return PocketProviderAdapter(runtime=runtime)
