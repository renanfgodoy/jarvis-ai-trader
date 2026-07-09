from app.models.candle import Candle


def calculate_atr(candles: list[Candle], period: int = 14) -> float:
    """Calcula o ATR final a partir de candles OHLC."""
    if period <= 0:
        raise ValueError("period deve ser maior que zero")
    if len(candles) < period + 1:
        raise ValueError("candles insuficientes para calcular ATR")

    true_ranges: list[float] = []

    for index in range(1, len(candles)):
        current = candles[index]
        previous = candles[index - 1]
        true_range = max(
            current.high - current.low,
            abs(current.high - previous.close),
            abs(current.low - previous.close),
        )
        true_ranges.append(true_range)

    atr = sum(true_ranges[:period]) / period

    for true_range in true_ranges[period:]:
        atr = ((atr * (period - 1)) + true_range) / period

    return round(atr, 6)
