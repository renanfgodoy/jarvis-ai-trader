from datetime import datetime, timedelta, timezone
import random

from app.models.candle import Candle, Timeframe
from app.providers.base import MarketDataProvider


class SimulatedMarketDataProvider(MarketDataProvider):
    """Provider simulado para desenvolvimento seguro da arquitetura.

    Esta Sprint não integra com corretoras. O objetivo é validar a estrutura
    de leitura e normalização de candles sem depender de APIs externas.
    """

    name = "simulated"

    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        if limit <= 0:
            raise ValueError("limit deve ser maior que zero")
        if limit > 500:
            raise ValueError("limit máximo permitido nesta Sprint é 500")

        minutes = self._timeframe_to_minutes(timeframe)
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        start = now - timedelta(minutes=minutes * (limit - 1))

        candles: list[Candle] = []
        last_close = 1.10000
        random.seed(f"{symbol}-{timeframe}-{limit}")

        for index in range(limit):
            timestamp = start + timedelta(minutes=minutes * index)
            movement = random.uniform(-0.00045, 0.00045)
            open_price = last_close
            close_price = max(0.00001, open_price + movement)
            high_price = max(open_price, close_price) + random.uniform(0.00005, 0.00025)
            low_price = min(open_price, close_price) - random.uniform(0.00005, 0.00025)
            volume = random.uniform(100, 1000)

            candle = Candle(
                symbol=symbol.upper(),
                timeframe=timeframe,
                timestamp=timestamp,
                open=round(open_price, 5),
                high=round(high_price, 5),
                low=round(max(0.00001, low_price), 5),
                close=round(close_price, 5),
                volume=round(volume, 2),
            )
            candles.append(candle)
            last_close = candle.close

        return candles

    @staticmethod
    def _timeframe_to_minutes(timeframe: Timeframe) -> int:
        mapping = {
            "M1": 1,
            "M5": 5,
            "M15": 15,
            "M30": 30,
            "H1": 60,
            "H4": 240,
            "D1": 1440,
        }
        return mapping[timeframe]
