from app.core.config import settings
from app.indicators.signal_engine import SignalEngineService
from app.models.candle import Timeframe
from app.models.risk import RiskCheckRequest
from app.models.scanner import AssetScannerResponse, AssetScanResult, ScannerStatus
from app.models.signal import SignalAnalysisResponse
from app.services.risk_manager import RiskManagerService
from app.services.market_reader import MarketReaderService

class AssetScannerService:
    """Varre múltiplos ativos e ranqueia as melhores oportunidades técnicas.

    Esta Sprint ainda usa o provider configurado no Market Reader. Em ambiente de
    desenvolvimento, isso normalmente será o provider simulado. O objetivo é criar
    a arquitetura do scanner Top 12 sem depender de integração real com corretora.
    """

    def __init__(
        self,
        signal_engine: SignalEngineService | None = None,
        risk_manager: RiskManagerService | None = None,
        market_reader: MarketReaderService | None = None,
    ) -> None:
        self.market_reader = market_reader or MarketReaderService()
        self.signal_engine = signal_engine or SignalEngineService(market_reader=self.market_reader)
        self.risk_manager = risk_manager or RiskManagerService()

    def scan(
        self,
        timeframe: Timeframe = "M1",
        candle_limit: int = 50,
        top: int = 12,
        symbols: list[str] | None = None,
        bankroll: float | None = None,
        payout: float = 80.0,
    ) -> AssetScannerResponse:
        """Analisa múltiplos ativos e retorna o Top N ordenado por score."""
        selected_symbols = self._normalize_symbols(symbols)
        results: list[AssetScanResult] = []

        for symbol in selected_symbols:
            analysis = self.signal_engine.analyze(symbol=symbol, timeframe=timeframe, limit=candle_limit)
            risk = self.risk_manager.check(
                RiskCheckRequest(
                    bankroll=bankroll or settings.bankroll_base,
                    entry_value=None,
                    daily_wins=0,
                    daily_losses=0,
                    gale_used=0,
                    payout=payout,
                )
            )

            status = self._status_for(analysis=analysis, risk_allowed=risk.allowed)
            score = self._score_for(analysis=analysis, risk_score=risk.risk_score, status=status)

            results.append(
                AssetScanResult(
                    rank=1,
                    symbol=symbol,
                    timeframe=timeframe,
                    signal=analysis.trend,
                    score=score,
                    strength=analysis.strength,
                    risk_level=risk.risk_level,
                    risk_score=risk.risk_score,
                    status=status,
                    ema9=analysis.ema9,
                    ema21=analysis.ema21,
                    rsi14=analysis.rsi14,
                    atr14=analysis.atr14,
                    momentum=analysis.momentum,
                    volatility=analysis.volatility,
                    reasons=self._build_reasons(analysis=analysis, status=status),
                    warnings=analysis.warnings + risk.warnings,
                )
            )

        ordered = sorted(results, key=lambda item: item.score, reverse=True)[:top]
        ranked = [item.model_copy(update={"rank": index + 1}) for index, item in enumerate(ordered)]

        return AssetScannerResponse(
            timeframe=timeframe,
            assets_scanned=len(selected_symbols),
            top_limit=top,
            approved_count=sum(1 for item in ranked if item.status == "APPROVED"),
            watchlist_count=sum(1 for item in ranked if item.status == "WATCHLIST"),
            blocked_count=sum(1 for item in ranked if item.status == "BLOCKED"),
            results=ranked,
        )

    @staticmethod
    def _normalize_symbols(symbols: list[str] | None) -> list[str]:
        if not symbols:
            return MarketReaderService().get_symbols()

        normalized: list[str] = []
        for symbol in symbols:
            clean_symbol = symbol.strip().upper()
            if clean_symbol and clean_symbol not in normalized:
                normalized.append(clean_symbol)
        return normalized or MarketReaderService().get_symbols()

    @staticmethod
    def _status_for(analysis: SignalAnalysisResponse, risk_allowed: bool) -> ScannerStatus:
        if not risk_allowed:
            return "BLOCKED"
        if analysis.trend == "NEUTRAL" or analysis.strength < 60:
            return "WATCHLIST"
        return "APPROVED"

    @staticmethod
    def _score_for(analysis: SignalAnalysisResponse, risk_score: int, status: ScannerStatus) -> int:
        base_score = analysis.strength

        if analysis.trend in {"BUY", "SELL"}:
            base_score += 10
        if analysis.momentum != "NEUTRAL":
            base_score += 5
        if analysis.volatility == "NORMAL":
            base_score += 5
        if status == "WATCHLIST":
            base_score -= 10
        if status == "BLOCKED":
            base_score -= 40

        base_score -= max(0, risk_score - 20) // 3
        return max(0, min(100, base_score))

    @staticmethod
    def _build_reasons(analysis: SignalAnalysisResponse, status: ScannerStatus) -> list[str]:
        reasons = list(analysis.reasons)
        if status == "APPROVED":
            reasons.append("Ativo aprovado para observação operacional pelo scanner")
        elif status == "WATCHLIST":
            reasons.append("Ativo em observação: aguardar confluência mais forte")
        else:
            reasons.append("Ativo bloqueado por risco ou baixa qualidade técnica")
        return reasons
