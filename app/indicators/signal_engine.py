from app.indicators.atr import calculate_atr
from app.indicators.ema import calculate_ema
from app.indicators.rsi import calculate_rsi
from app.models.candle import Candle, Timeframe
from app.models.signal import MomentumLevel, SignalAnalysisResponse, SignalTrend, VolatilityLevel
from app.services.market_reader import MarketReaderService


class SignalEngineService:
    """Motor técnico responsável por transformar candles em leitura objetiva.

    Esta Sprint ainda não executa operações. O Signal Engine apenas calcula
    indicadores e gera uma leitura técnica para ser usada por módulos futuros.
    """

    def __init__(self, market_reader: MarketReaderService | None = None) -> None:
        self.market_reader = market_reader or MarketReaderService()

    def analyze(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 50) -> SignalAnalysisResponse:
        """Busca candles e retorna indicadores técnicos consolidados."""
        clean_symbol = symbol.strip().upper()
        candles = self.market_reader.get_candles(symbol=clean_symbol, timeframe=timeframe, limit=limit)
        return self.analyze_candles(candles=candles, symbol=clean_symbol, timeframe=timeframe)

    def analyze_candles(
        self,
        candles: list[Candle],
        symbol: str,
        timeframe: Timeframe = "M1",
    ) -> SignalAnalysisResponse:
        """Analisa uma lista de candles já normalizada."""
        if len(candles) < 22:
            raise ValueError("São necessários pelo menos 22 candles para EMA21, RSI14 e ATR14")

        closes = [candle.close for candle in candles]
        ema9 = calculate_ema(closes, 9)
        ema21 = calculate_ema(closes, 21)
        rsi14 = calculate_rsi(closes, 14)
        atr14 = calculate_atr(candles, 14)

        trend = self._detect_trend(ema9=ema9, ema21=ema21, rsi=rsi14)
        momentum = self._detect_momentum(candles)
        volatility = self._classify_volatility(atr=atr14)
        strength, reasons, warnings = self._calculate_strength(
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            ema9=ema9,
            ema21=ema21,
            rsi=rsi14,
            atr=atr14,
        )

        return SignalAnalysisResponse(
            symbol=symbol.strip().upper(),
            timeframe=timeframe,
            candles_analyzed=len(candles),
            ema9=ema9,
            ema21=ema21,
            rsi14=rsi14,
            atr14=atr14,
            trend=trend,
            momentum=momentum,
            volatility=volatility,
            strength=strength,
            reasons=reasons,
            warnings=warnings,
        )

    @staticmethod
    def _detect_trend(ema9: float, ema21: float, rsi: float) -> SignalTrend:
        ema_distance = abs(ema9 - ema21)
        if ema_distance < 0.00003 or 45 <= rsi <= 55:
            return "NEUTRAL"
        if ema9 > ema21 and rsi > 50:
            return "BUY"
        if ema9 < ema21 and rsi < 50:
            return "SELL"
        return "NEUTRAL"

    @staticmethod
    def _detect_momentum(candles: list[Candle]) -> MomentumLevel:
        recent = candles[-5:]
        bullish = sum(1 for candle in recent if candle.close > candle.open)
        bearish = sum(1 for candle in recent if candle.close < candle.open)
        if bullish >= 4:
            return "BULLISH"
        if bearish >= 4:
            return "BEARISH"
        return "NEUTRAL"

    @staticmethod
    def _classify_volatility(atr: float) -> VolatilityLevel:
        if atr < 0.00018:
            return "LOW"
        if atr > 0.00075:
            return "HIGH"
        return "NORMAL"

    @staticmethod
    def _calculate_strength(
        trend: SignalTrend,
        momentum: MomentumLevel,
        volatility: VolatilityLevel,
        ema9: float,
        ema21: float,
        rsi: float,
        atr: float,
    ) -> tuple[int, list[str], list[str]]:
        score = 0
        reasons: list[str] = []
        warnings: list[str] = []

        if trend in {"BUY", "SELL"}:
            score += 35
            reasons.append(f"Tendência técnica detectada para {trend}")
        else:
            warnings.append("Tendência neutra ou sem confluência suficiente")

        if (trend == "BUY" and momentum == "BULLISH") or (trend == "SELL" and momentum == "BEARISH"):
            score += 25
            reasons.append("Momentum alinhado com a tendência")
        elif momentum == "NEUTRAL":
            warnings.append("Momentum recente neutro")
        else:
            warnings.append("Momentum divergente da tendência")

        ema_gap = abs(ema9 - ema21)
        if ema_gap >= 0.00010:
            score += 15
            reasons.append("Distância entre EMAs indica direção mais clara")
        else:
            warnings.append("EMAs ainda muito próximas")

        if 35 <= rsi <= 70:
            score += 15
            reasons.append("RSI dentro de faixa operacional aceitável")
        else:
            warnings.append("RSI em região extrema ou pouco favorável")

        if volatility == "NORMAL":
            score += 10
            reasons.append("Volatilidade dentro da faixa normal")
        elif volatility == "LOW":
            warnings.append("Volatilidade baixa pode reduzir qualidade do sinal")
        else:
            warnings.append("Volatilidade alta pode aumentar o risco")

        if atr <= 0:
            warnings.append("ATR inválido ou sem variação")

        return min(score, 100), reasons, warnings
