from app.core.config import settings
from app.models.candle import Timeframe
from app.models.intelligence import MarketIntelligenceResponse, MarketIntelligenceScannerResponse
from app.services.confluence_engine import ConfluenceEngineService
from app.services.market_reader import MarketReaderService


class MarketIntelligenceService:
    """Scanner Pro que ranqueia ativos por confluência técnica explicável."""

    def __init__(
        self,
        confluence_engine: ConfluenceEngineService | None = None,
        market_reader: MarketReaderService | None = None,
    ) -> None:
        self.market_reader = market_reader or MarketReaderService()
        self.confluence_engine = confluence_engine or ConfluenceEngineService()

    def scan(
        self,
        timeframe: Timeframe = "M1",
        top: int = 12,
        payout: float = 80.0,
        minimum_score: int = 80,
        minimum_payout: float | None = None,
        candle_limit: int = 80,
        symbols: list[str] | None = None,
    ) -> MarketIntelligenceScannerResponse:
        symbols_to_scan = self._symbols(symbols)
        min_payout = minimum_payout if minimum_payout is not None else settings.minimum_payout
        results: list[MarketIntelligenceResponse] = []

        for index, symbol in enumerate(symbols_to_scan):
            # Simula variações de payout por ativo enquanto não há provider real.
            symbol_payout = max(60.0, min(96.0, payout + ((index % 7) - 3) * 2.5))
            results.append(
                self.confluence_engine.analyze(
                    symbol=symbol,
                    timeframe=timeframe,
                    payout=symbol_payout,
                    minimum_score=minimum_score,
                    minimum_payout=min_payout,
                    candle_limit=candle_limit,
                )
            )

        ordered = sorted(results, key=lambda item: (item.status == "APPROVED", item.score, item.payout), reverse=True)[:top]
        return MarketIntelligenceScannerResponse(
            timeframe=timeframe,
            assets_scanned=len(symbols_to_scan),
            top_limit=top,
            minimum_score=minimum_score,
            minimum_payout=min_payout,
            approved_count=sum(1 for item in ordered if item.status == "APPROVED"),
            watchlist_count=sum(1 for item in ordered if item.status == "WATCHLIST"),
            blocked_count=sum(1 for item in ordered if item.status == "BLOCKED"),
            results=ordered,
        )

    def _symbols(self, symbols: list[str] | None) -> list[str]:
        if symbols:
            normalized: list[str] = []
            for symbol in symbols:
                clean = symbol.strip().upper()
                if clean and clean not in normalized:
                    normalized.append(clean)
            if normalized:
                return normalized
        return self.market_reader.get_symbols()
