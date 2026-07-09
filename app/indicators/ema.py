def calculate_ema(values: list[float], period: int) -> float:
    """Calcula a EMA final de uma sequência de valores.

    A função usa Python puro para manter a Sprint 6 simples, testável e sem
    dependências pesadas. Retorna apenas o último valor da média móvel exponencial.
    """
    if period <= 0:
        raise ValueError("period deve ser maior que zero")
    if len(values) < period:
        raise ValueError("valores insuficientes para calcular EMA")

    multiplier = 2 / (period + 1)
    ema = sum(values[:period]) / period

    for price in values[period:]:
        ema = (price - ema) * multiplier + ema

    return round(ema, 6)
