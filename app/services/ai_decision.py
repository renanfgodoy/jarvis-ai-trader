from app.models.candle import Candle, Timeframe
from app.models.decision import DecisionResponse, SignalAction, SignalGrade, TrendDirection
from app.services.market_reader import MarketReaderService


class AIDecisionEngine:
    """Motor inicial de decisão do J.A.R.V.I.S AI TRADER.

    Sprint 3: versão baseada em regras simples e auditáveis.
    O objetivo é criar uma camada de decisão explicável antes de adicionar
    indicadores técnicos, backtesting e machine learning.
    """

    def __init__(self, market_reader: MarketReaderService | None = None) -> None:
        self.market_reader = market_reader or MarketReaderService()

    def analyze(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 20) -> DecisionResponse:
        """Analisa candles e retorna uma decisão probabilística."""
        candles = self.market_reader.get_candles(symbol=symbol, timeframe=timeframe, limit=limit)
        return self.analyze_candles(candles=candles, symbol=symbol, timeframe=timeframe)

    def analyze_candles(self, candles: list[Candle], symbol: str, timeframe: Timeframe = "M1") -> DecisionResponse:
        """Executa análise sobre candles já carregados.

        Esse método facilita testes e permite que, no futuro, o backtesting
        injete candles históricos diretamente no motor de decisão.
        """
        if len(candles) < 5:
            raise ValueError("São necessários pelo menos 5 candles para análise")

        clean_symbol = symbol.strip().upper()
        trend = self._detect_trend(candles)
        momentum = self._calculate_momentum(candles)
        volatility = self._calculate_volatility(candles)
        bullish_count, bearish_count = self._count_recent_direction(candles)

        score = 0
        reasons: list[str] = []
        warnings: list[str] = []

        if trend == "UP":
            score += 30
            reasons.append("Tendência de alta detectada pelos últimos candles")
        elif trend == "DOWN":
            score += 30
            reasons.append("Tendência de baixa detectada pelos últimos candles")
        else:
            warnings.append("Mercado sem direção clara")

        if abs(momentum) >= 0.00020:
            score += 25
            reasons.append("Momentum relevante no movimento recente")
        else:
            warnings.append("Momentum fraco")

        if bullish_count >= 3 and trend == "UP":
            score += 20
            reasons.append("Maioria dos candles recentes fechando em alta")
        elif bearish_count >= 3 and trend == "DOWN":
            score += 20
            reasons.append("Maioria dos candles recentes fechando em baixa")
        else:
            warnings.append("Direção recente ainda inconsistente")

        if 0.00010 <= volatility <= 0.00120:
            score += 15
            reasons.append("Volatilidade dentro de faixa aceitável para análise")
        else:
            warnings.append("Volatilidade fora da faixa ideal")

        if score >= 80:
            grade: SignalGrade = "A+"
        elif score >= 70:
            grade = "A"
        elif score >= 55:
            grade = "B"
        elif score >= 45:
            grade = "C"
        else:
            grade = "NO_TRADE"

        signal = self._resolve_signal(trend=trend, score=score, momentum=momentum)
        confidence = min(100, max(0, score))

        if signal == "WAIT":
            if "Aguardar melhor confluência antes de operar" not in warnings:
                warnings.append("Aguardar melhor confluência antes de operar")
            if not reasons:
                reasons.append("Condições insuficientes para compra ou venda")

        return DecisionResponse(
            symbol=clean_symbol,
            timeframe=timeframe,
            signal=signal,
            grade=grade,
            confidence=confidence,
            trend=trend,
            momentum=round(momentum, 6),
            volatility=round(volatility, 6),
            score=score,
            reasons=reasons,
            warnings=warnings,
        )

    @staticmethod
    def _detect_trend(candles: list[Candle]) -> TrendDirection:
        first_close = candles[0].close
        last_close = candles[-1].close
        variation = last_close - first_close

        if variation > 0.00025:
            return "UP"
        if variation < -0.00025:
            return "DOWN"
        return "SIDEWAYS"

    @staticmethod
    def _calculate_momentum(candles: list[Candle]) -> float:
        recent = candles[-5:]
        return recent[-1].close - recent[0].open

    @staticmethod
    def _calculate_volatility(candles: list[Candle]) -> float:
        ranges = [candle.high - candle.low for candle in candles[-10:]]
        return sum(ranges) / len(ranges)

    @staticmethod
    def _count_recent_direction(candles: list[Candle]) -> tuple[int, int]:
        recent = candles[-5:]
        bullish = sum(1 for candle in recent if candle.close > candle.open)
        bearish = sum(1 for candle in recent if candle.close < candle.open)
        return bullish, bearish

    @staticmethod
    def _resolve_signal(trend: TrendDirection, score: int, momentum: float) -> SignalAction:
        if score < 55:
            return "WAIT"
        if trend == "UP" and momentum > 0:
            return "BUY"
        if trend == "DOWN" and momentum < 0:
            return "SELL"
        return "WAIT"
