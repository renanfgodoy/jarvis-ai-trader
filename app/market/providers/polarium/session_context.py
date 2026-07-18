from __future__ import annotations

from dataclasses import dataclass

from app.market.providers.polarium.models import POLARIUM_MARKET_TYPE, POLARIUM_PROVIDER

UNKNOWN_ASSET_LABEL = "ATIVO NÃO IDENTIFICADO"


@dataclass(frozen=True)
class PolariumSessionContext:
    provider: str
    websocket_state: str
    authenticated: bool
    connection_status: str
    active_id: int | None
    symbol: str | None
    display_name: str
    market_type: str
    raw_size: int | None
    timeframe: str | None
    visible_active_id: int | None
    visible_symbol: str | None
    visible_display_name: str
    visible_market_type: str
    visible_raw_size: int | None
    visible_timeframe: str | None
    latest_market_event_active_id: int | None
    latest_market_event_raw_sizes: tuple[int, ...]
    available_raw_sizes: tuple[int, ...]
    background_market_contexts: tuple[dict, ...]
    latest_price: float | None
    feed_status: str
    history_state: str
    history_count: int
    history_required: int
    history_progress: int
    bootstrap_complete: bool
    last_update: int | None
    analysis_blocked: bool
    analysis_block_reason: str | None

    @classmethod
    def disconnected(cls) -> "PolariumSessionContext":
        return cls(
            provider=POLARIUM_PROVIDER,
            websocket_state="DISCONNECTED",
            authenticated=False,
            connection_status="OFFLINE",
            active_id=None,
            symbol=None,
            display_name="Não disponível",
            market_type=POLARIUM_MARKET_TYPE,
            raw_size=None,
            timeframe=None,
            visible_active_id=None,
            visible_symbol=None,
            visible_display_name="Não disponível",
            visible_market_type=POLARIUM_MARKET_TYPE,
            visible_raw_size=None,
            visible_timeframe=None,
            latest_market_event_active_id=None,
            latest_market_event_raw_sizes=(),
            available_raw_sizes=(),
            background_market_contexts=(),
            latest_price=None,
            feed_status="OFFLINE",
            history_state="NO_HISTORY",
            history_count=0,
            history_required=0,
            history_progress=0,
            bootstrap_complete=False,
            last_update=None,
            analysis_blocked=True,
            analysis_block_reason="POLARIUM_SESSION_OFFLINE",
        )

    def sanitized(self) -> dict:
        return {
            "provider": self.provider,
            "websocket_state": self.websocket_state,
            "authenticated": self.authenticated,
            "connection_status": self.connection_status,
            "active_id": self.active_id,
            "symbol": self.symbol,
            "display_name": self.display_name,
            "market_type": self.market_type,
            "raw_size": self.raw_size,
            "timeframe": self.timeframe,
            "visible_active_id": self.visible_active_id,
            "visible_symbol": self.visible_symbol,
            "visible_display_name": self.visible_display_name,
            "visible_market_type": self.visible_market_type,
            "visible_raw_size": self.visible_raw_size,
            "visible_timeframe": self.visible_timeframe,
            "latest_market_event_active_id": self.latest_market_event_active_id,
            "latest_market_event_raw_sizes": list(self.latest_market_event_raw_sizes),
            "available_raw_sizes": list(self.available_raw_sizes),
            "background_market_contexts": list(self.background_market_contexts),
            "latest_price": self.latest_price,
            "feed_status": self.feed_status,
            "history_state": self.history_state,
            "history_count": self.history_count,
            "history_required": self.history_required,
            "history_progress": self.history_progress,
            "bootstrap_complete": self.bootstrap_complete,
            "last_update": self.last_update,
            "analysis_blocked": self.analysis_blocked,
            "analysis_block_reason": self.analysis_block_reason,
        }


def build_polarium_session_context(
    *,
    websocket_state: str,
    authenticated: bool,
    active_id: int | None,
    symbol: str | None,
    raw_size: int | None,
    latest_price: float | None,
    last_update: int | None,
    feed_status: str,
    history: dict | None = None,
    latest_market_event_active_id: int | None = None,
    latest_market_event_raw_sizes: tuple[int, ...] = (),
    available_raw_sizes: tuple[int, ...] = (),
    background_market_contexts: tuple[dict, ...] = (),
) -> PolariumSessionContext:
    has_session = active_id is not None
    display_name = symbol if symbol else (UNKNOWN_ASSET_LABEL if has_session else "Não disponível")
    history_state = str((history or {}).get("state") or "NO_HISTORY")
    history_count = int((history or {}).get("history_count") or 0)
    history_required = int((history or {}).get("required_candles") or 0)
    history_progress = int((history or {}).get("progress") or 0)
    bootstrap_complete = history_state == "READY"
    return PolariumSessionContext(
        provider=POLARIUM_PROVIDER,
        websocket_state=websocket_state,
        authenticated=authenticated,
        connection_status="ONLINE" if websocket_state == "ONLINE" else "OFFLINE",
        active_id=active_id,
        symbol=symbol,
        display_name=display_name,
        market_type=POLARIUM_MARKET_TYPE,
        raw_size=raw_size,
        timeframe=_timeframe(raw_size),
        visible_active_id=active_id,
        visible_symbol=symbol,
        visible_display_name=display_name,
        visible_market_type=POLARIUM_MARKET_TYPE,
        visible_raw_size=raw_size,
        visible_timeframe=_timeframe(raw_size),
        latest_market_event_active_id=latest_market_event_active_id,
        latest_market_event_raw_sizes=latest_market_event_raw_sizes,
        available_raw_sizes=available_raw_sizes,
        background_market_contexts=background_market_contexts,
        latest_price=latest_price,
        feed_status=feed_status,
        history_state=history_state,
        history_count=history_count,
        history_required=history_required,
        history_progress=history_progress,
        bootstrap_complete=bootstrap_complete,
        last_update=last_update,
        analysis_blocked=symbol is None or history_state != "READY",
        analysis_block_reason=(
            "POLARIUM_SYMBOL_UNRESOLVED"
            if symbol is None and has_session
            else "POLARIUM_SESSION_OFFLINE"
            if symbol is None
            else "POLARIUM_HISTORY_NOT_READY"
            if history_state != "READY"
            else None
        ),
    )


def _timeframe(raw_size: int | None) -> str | None:
    if raw_size == 60:
        return "M1"
    if raw_size == 300:
        return "M5"
    if raw_size == 900:
        return "M15"
    if raw_size is None:
        return None
    return f"{raw_size}s"
