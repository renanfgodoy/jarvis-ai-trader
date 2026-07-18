from __future__ import annotations

from dataclasses import dataclass

from app.market.providers.pocket.models import ConnectionState, HistoryState, SessionState


@dataclass(frozen=True)
class PocketSessionContext:
    provider: str = "POCKET"
    connection_state: ConnectionState = "STOPPED"
    session_state: SessionState = "EMPTY"
    asset: str | None = None
    display_name: str | None = None
    market_type: str | None = None
    is_otc: bool | None = None
    period: int | None = None
    timeframe: str | None = None
    last_price: float | None = None
    history_count: int = 0
    history_required: int = 50
    history_state: HistoryState = "EMPTY"
    bootstrap_complete: bool = False
    last_update: float | None = None
    analysis_blocked: bool = True
    analysis_block_reason: str = "HISTORY_NOT_READY"

    def with_connection(self, connection_state: ConnectionState, session_state: SessionState | None = None) -> "PocketSessionContext":
        return PocketSessionContext(
            provider=self.provider,
            connection_state=connection_state,
            session_state=session_state or self.session_state,
            asset=self.asset,
            display_name=self.display_name,
            market_type=self.market_type,
            is_otc=self.is_otc,
            period=self.period,
            timeframe=self.timeframe,
            last_price=self.last_price,
            history_count=self.history_count,
            history_required=self.history_required,
            history_state=self.history_state,
            bootstrap_complete=self.bootstrap_complete,
            last_update=self.last_update,
            analysis_blocked=self.analysis_blocked,
            analysis_block_reason=self.analysis_block_reason,
        )

