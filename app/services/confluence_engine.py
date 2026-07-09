from app.indicators.signal_engine import SignalEngineService
from app.models.candle import Timeframe
from app.models.intelligence import (
    ConfluenceFactor,
    ConfluenceStatus,
    MarketIntelligenceResponse,
    RiskBias,
)
from app.models.signal import SignalAnalysisResponse, SignalTrend


class ConfluenceEngineService:
    """Calcula score operacional combinando indicadores e contexto técnico.

    A V0.15.0 ainda é um motor determinístico e explicável. A ideia é evitar
    sinais mágicos: todo score precisa nascer de fatores técnicos auditáveis.
    """

    def __init__(self, signal_engine: SignalEngineService | None = None) -> None:
        self.signal_engine = signal_engine or SignalEngineService()

    def analyze(
        self,
        symbol: str = "EURUSD-OTC",
        timeframe: Timeframe = "M1",
        payout: float = 80.0,
        minimum_score: int = 80,
        minimum_payout: float = 75.0,
        candle_limit: int = 80,
    ) -> MarketIntelligenceResponse:
        signal = self.signal_engine.analyze(symbol=symbol, timeframe=timeframe, limit=candle_limit)
        factors = self._build_factors(signal=signal, payout=payout, minimum_payout=minimum_payout)
        score = max(0, min(100, sum(factor.points for factor in factors)))
        status = self._status(score=score, signal=signal.trend, payout=payout, minimum_score=minimum_score, minimum_payout=minimum_payout)
        risk_bias = self._risk_bias(score=score, payout=payout, signal=signal)

        reasons = [factor.explanation for factor in factors if factor.passed]
        warnings = list(signal.warnings)
        if payout < minimum_payout:
            warnings.append(f"Payout abaixo do mínimo operacional: {payout:.0f}% < {minimum_payout:.0f}%.")
        if signal.trend == "NEUTRAL":
            warnings.append("Tendência neutra: aguardar confluência direcional antes de operar.")
        if score < minimum_score:
            warnings.append(f"Score abaixo do mínimo configurado: {score}% < {minimum_score}%.")

        return MarketIntelligenceResponse(
            symbol=symbol.strip().upper(),
            timeframe=timeframe,
            signal=signal.trend,
            score=score,
            status=status,
            confidence_label=self._confidence_label(score),
            payout=round(payout, 2),
            minimum_score=minimum_score,
            minimum_payout=round(minimum_payout, 2),
            risk_bias=risk_bias,
            trend=signal.trend,
            momentum=signal.momentum,
            volatility=signal.volatility,
            ema9=signal.ema9,
            ema21=signal.ema21,
            rsi14=signal.rsi14,
            atr14=signal.atr14,
            strength=signal.strength,
            factors=factors,
            reasons=reasons,
            warnings=warnings,
            action=self._action(status=status, trend=signal.trend),
        )

    def _build_factors(self, signal: SignalAnalysisResponse, payout: float, minimum_payout: float) -> list[ConfluenceFactor]:
        directional = signal.trend in {"BUY", "SELL"}
        ema_aligned = (signal.ema9 > signal.ema21 and signal.trend == "BUY") or (signal.ema9 < signal.ema21 and signal.trend == "SELL")
        rsi_favorable = self._rsi_favorable(signal)
        atr_ok = signal.volatility in {"NORMAL", "LOW"}
        momentum_ok = (signal.trend == "BUY" and signal.momentum == "BULLISH") or (signal.trend == "SELL" and signal.momentum == "BEARISH")
        strength_ok = signal.strength >= 70
        payout_ok = payout >= minimum_payout

        return [
            ConfluenceFactor(
                name="EMA 9 x EMA 21",
                max_points=20,
                points=20 if ema_aligned else 8 if directional else 0,
                passed=ema_aligned,
                explanation="EMA9 alinhada com EMA21 na direção do sinal." if ema_aligned else "EMAs ainda sem alinhamento ideal.",
            ),
            ConfluenceFactor(
                name="RSI 14",
                max_points=15,
                points=15 if rsi_favorable else 7 if 35 <= signal.rsi14 <= 65 else 0,
                passed=rsi_favorable,
                explanation=f"RSI favorável para {signal.trend}: {signal.rsi14:.1f}." if rsi_favorable else f"RSI sem vantagem clara: {signal.rsi14:.1f}.",
            ),
            ConfluenceFactor(
                name="ATR / Volatilidade",
                max_points=10,
                points=10 if atr_ok else 3,
                passed=atr_ok,
                explanation=f"Volatilidade {signal.volatility.lower()} dentro da faixa operacional." if atr_ok else "Volatilidade alta: reduzir prioridade da oportunidade.",
            ),
            ConfluenceFactor(
                name="Momentum",
                max_points=15,
                points=15 if momentum_ok else 6 if signal.momentum != "NEUTRAL" else 0,
                passed=momentum_ok,
                explanation=f"Momentum {signal.momentum.lower()} confirma o sinal." if momentum_ok else "Momentum não confirmou totalmente a direção.",
            ),
            ConfluenceFactor(
                name="Força técnica",
                max_points=20,
                points=20 if strength_ok else max(0, int(signal.strength * 0.2)),
                passed=strength_ok,
                explanation=f"Força técnica elevada: {signal.strength}%." if strength_ok else f"Força técnica moderada/baixa: {signal.strength}%.",
            ),
            ConfluenceFactor(
                name="Payout",
                max_points=10,
                points=10 if payout_ok else max(0, int(payout / max(minimum_payout, 1) * 7)),
                passed=payout_ok,
                explanation=f"Payout aprovado: {payout:.0f}%." if payout_ok else f"Payout insuficiente: {payout:.0f}%.",
            ),
            ConfluenceFactor(
                name="Direção operacional",
                max_points=10,
                points=10 if directional else 0,
                passed=directional,
                explanation=f"Sinal direcional {signal.trend} detectado." if directional else "Sem direção operacional: aguardar.",
            ),
        ]

    @staticmethod
    def _rsi_favorable(signal: SignalAnalysisResponse) -> bool:
        if signal.trend == "BUY":
            return 28 <= signal.rsi14 <= 64
        if signal.trend == "SELL":
            return 36 <= signal.rsi14 <= 72
        return False

    @staticmethod
    def _status(score: int, signal: SignalTrend, payout: float, minimum_score: int, minimum_payout: float) -> ConfluenceStatus:
        if signal == "NEUTRAL" or payout < minimum_payout:
            return "BLOCKED"
        if score >= minimum_score:
            return "APPROVED"
        if score >= max(60, minimum_score - 15):
            return "WATCHLIST"
        return "BLOCKED"

    @staticmethod
    def _risk_bias(score: int, payout: float, signal: SignalAnalysisResponse) -> RiskBias:
        if score >= 85 and payout >= 80 and signal.volatility != "HIGH":
            return "LOW"
        if score >= 70:
            return "MEDIUM"
        return "HIGH"

    @staticmethod
    def _confidence_label(score: int) -> str:
        if score >= 90:
            return "ELITE"
        if score >= 80:
            return "HIGH"
        if score >= 65:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _action(status: ConfluenceStatus, trend: SignalTrend) -> str:
        if status == "APPROVED" and trend in {"BUY", "SELL"}:
            return f"PREPARAR {trend} SOMENTE SE O AUTOTRADE GATE APROVAR EM DEMO."
        if status == "WATCHLIST":
            return "MANTER EM OBSERVAÇÃO. AGUARDAR MELHOR CONFLUÊNCIA."
        return "NÃO OPERAR."
