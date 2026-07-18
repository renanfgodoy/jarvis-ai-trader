from __future__ import annotations

from dataclasses import asdict, replace

from app.market.providers.pocket.candle_store_adapter import PocketCandleStoreAdapter
from app.market.providers.pocket.config import PocketProviderConfig
from app.market.providers.pocket.errors import POCKET_LIVE_CONNECTION_DISABLED, POCKET_UNKNOWN_EVENT, PocketRuntimeError
from app.market.providers.pocket.event_router import PocketEventRouter
from app.market.providers.pocket.metrics import PocketRuntimeMetrics
from app.market.providers.pocket.models import PocketAssetCatalog, PocketDomainEvent
from app.market.providers.pocket.readiness import PocketReadinessTracker
from app.market.providers.pocket.realtime_candle_builder import PocketRealtimeCandleBuilder
from app.market.providers.pocket.runtime_guard import PocketRuntimeGuard
from app.market.providers.pocket.session_context import PocketSessionContext
from tools.pocket_parser.models import PocketAssetChanged, PocketHistoryBatch, PocketRealtimeTick, SUPPORTED_PERIODS


class PocketMarketRuntime:
    def __init__(
        self,
        *,
        config: PocketProviderConfig | None = None,
        store: PocketCandleStoreAdapter | None = None,
        guard: PocketRuntimeGuard | None = None,
    ) -> None:
        self.config = config or PocketProviderConfig()
        self.store = store or PocketCandleStoreAdapter()
        self.guard = guard or PocketRuntimeGuard()
        self.metrics = PocketRuntimeMetrics()
        self.router = PocketEventRouter()
        self.readiness = PocketReadinessTracker(self.config.pocket_history_required)
        self.builder = PocketRealtimeCandleBuilder()
        self.context = PocketSessionContext(history_required=self.config.pocket_history_required)
        self.asset_catalog = PocketAssetCatalog(assets=())
        self.unknown_events: dict[str, int] = {}
        self.last_error: str | None = None
        self._running = False
        self._known_periods_by_asset: dict[str, set[int]] = {}

    def start(self, *, live_connection: bool = False) -> None:
        if live_connection or self.config.pocket_live_connection_enabled:
            self.last_error = POCKET_LIVE_CONNECTION_DISABLED
            raise PocketRuntimeError(POCKET_LIVE_CONNECTION_DISABLED, "Pocket live connection is disabled in this sprint.")
        self._running = True
        self.context = self.context.with_connection("ONLINE", "AUTHORIZED_REPLAY")

    def stop(self) -> None:
        self._running = False
        self.builder.clear()
        self._known_periods_by_asset.clear()
        self.context = self.context.with_connection("STOPPED", "DISCONNECTED")
        if not self.config.preserve_store_on_stop:
            self.store.clear()

    def process(self, event: PocketDomainEvent) -> None:
        self.metrics.events_received += 1
        route = self.router.route(event)
        try:
            if route == "auth/success":
                self.guard.ensure_allowed("UPDATE_SESSION_STATE")
                self.context = self.context.with_connection("ONLINE", "AUTHORIZED_REPLAY")
            elif route == "updateAssets":
                self.guard.ensure_allowed("PROCESS_ASSET_CATALOG")
                self.asset_catalog = PocketAssetCatalog(assets=tuple(event.payload or ()))
            elif route == "changeSymbol":
                self.guard.ensure_allowed("UPDATE_SESSION_STATE")
                self._apply_asset_changed(event.payload)
            elif route == "updateHistoryNewFast":
                self.guard.ensure_allowed("PROCESS_HISTORY")
                self._apply_history(event.payload)
            elif route == "updateStream":
                self.guard.ensure_allowed("PROCESS_REALTIME")
                self._apply_tick(event.payload)
            elif route == "updateCharts":
                self.guard.ensure_allowed("PROCESS_CHART_METADATA")
            elif route in {"disconnect", "reconnect"}:
                self.guard.ensure_allowed("UPDATE_SESSION_STATE")
                state = "RECONNECTING" if route == "reconnect" else "OFFLINE"
                self.context = self.context.with_connection(state)
            else:
                self.metrics.unknown_events += 1
                self.unknown_events[str(event.event_type)] = self.unknown_events.get(str(event.event_type), 0) + 1
                self.last_error = POCKET_UNKNOWN_EVENT
            self.metrics.events_processed += 1
        except PocketRuntimeError as error:
            self.metrics.events_rejected += 1
            self.last_error = error.code
            if error.code.endswith("GUARD_BLOCKED"):
                self.metrics.guard_blocks += 1

    def status(self) -> dict:
        return {
            "running": self._running,
            "connection_state": self.context.connection_state,
            "current_context": asdict(self.context),
            "metrics": asdict(self.metrics),
            "buckets": {key: self.store.count(key) for key in self.store.list_buckets()},
            "readiness": {key: self.readiness.state_for(key) for key in self.store.list_buckets()},
            "asset_catalog_count": len(self.asset_catalog.assets),
            "unknown_events": self.unknown_events,
            "guard_blocks": self.guard.blocked_count,
            "last_error": self.last_error,
        }

    def _apply_asset_changed(self, payload: object) -> None:
        if not isinstance(payload, PocketAssetChanged):
            return
        key = self.store.key(payload.asset, payload.period)
        state = self.readiness.start_bootstrap(key)
        self.context = PocketSessionContext(
            connection_state=self.context.connection_state,
            session_state=self.context.session_state,
            asset=payload.asset,
            display_name=payload.display_name,
            market_type=payload.market_type,
            is_otc=payload.is_otc,
            period=payload.period,
            timeframe=payload.timeframe,
            last_price=self.context.last_price,
            history_count=self.readiness.count_for(key),
            history_required=self.config.pocket_history_required,
            history_state=state,
            bootstrap_complete=False,
            last_update=payload.timestamp,
            analysis_blocked=True,
            analysis_block_reason="HISTORY_NOT_READY",
        )

    def _apply_history(self, payload: object) -> None:
        if not isinstance(payload, PocketHistoryBatch):
            self.metrics.events_rejected += 1
            return
        self.metrics.history_batches += 1
        written = self.store.add_historical(payload.candles)
        self._known_periods_by_asset.setdefault(payload.asset, set()).add(payload.period)
        self.metrics.historical_candles_written += len(payload.candles)
        self.metrics.duplicate_candles += max(0, len(payload.candles) - written)
        key = self.store.key(payload.asset, payload.period)
        count = self.store.count(key)
        state = self.readiness.update_history(key, count)
        self.context = replace(
            self.context,
            asset=payload.asset,
            display_name=payload.asset.replace("_otc", " OTC").upper(),
            market_type="OTC" if payload.asset.endswith("_otc") else "REGULAR",
            is_otc=payload.asset.endswith("_otc"),
            period=payload.period,
            timeframe=payload.timeframe,
            history_count=count,
            history_state=state,
            bootstrap_complete=state == "READY",
            analysis_blocked=state != "READY",
            analysis_block_reason="READY" if state == "READY" else "HISTORY_NOT_READY",
            last_update=payload.last_timestamp,
        )

    def _apply_tick(self, payload: object) -> None:
        if not isinstance(payload, PocketRealtimeTick):
            self.metrics.ticks_rejected += 1
            return
        self.metrics.ticks_received += 1
        self.metrics.ticks_processed += 1
        self.context = replace(self.context, asset=payload.asset, last_price=payload.price, last_update=payload.timestamp)
        periods = sorted(self._known_periods_by_asset.get(payload.asset) or set(SUPPORTED_PERIODS))
        for period in periods:
            candle, status = self.builder.update(payload, period)
            self.store.add_realtime(candle)
            if status == "created":
                self.metrics.realtime_candles_created += 1
            else:
                self.metrics.realtime_candles_updated += 1
