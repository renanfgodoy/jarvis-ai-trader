def calculate_rsi(values: list[float], period: int = 14) -> float:
    """Calcula o RSI final de uma lista de fechamentos."""
    if period <= 0:
        raise ValueError("period deve ser maior que zero")
    if len(values) < period + 1:
        raise ValueError("valores insuficientes para calcular RSI")

    gains: list[float] = []
    losses: list[float] = []

    for index in range(1, len(values)):
        change = values[index] - values[index - 1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for index in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[index]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[index]) / period

    if avg_loss == 0:
        return 100.0

    relative_strength = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + relative_strength))
    return round(rsi, 2)
