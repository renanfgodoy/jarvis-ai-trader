from datetime import datetime, timedelta, timezone
import random

from app.models.candle import Candle, Timeframe
from app.providers.base import MarketDataProvider

DEFAULT_SIMULATED_SYMBOLS: tuple[str, ...] = (
    "EURUSD-OTC",
    "GBPUSD-OTC",
    "USDJPY-OTC",
    "USDCHF-OTC",
    "USDCAD-OTC",
    "AUDUSD-OTC",
    "NZDUSD-OTC",
    "EURJPY-OTC",
    "GBPJPY-OTC",
    "EURGBP-OTC",
    "BTCUSD-OTC",
    "ETHUSD-OTC",
    "SOLUSD-OTC",
    "XAUUSD-OTC",
    "EURCAD-OTC",
    "AUDJPY-OTC",
)


class SimulatedMarketDataProvider(MarketDataProvider):
    """Provider simulado para desenvolvimento seguro da arquitetura.

    Ele fornece múltiplos ativos e candles determinísticos por símbolo/timeframe,
    permitindo que Scanner, Signal Engine e Decision Engine sejam testados sem
    depender de APIs externas ou da conta demo da corretora.
    """

    name = "simulated"
    display_name = "Simulated Provider"
    supports_realtime = False
    supports_trading = False

    def get_symbols(self) -> list[str]:
        """Retorna ativos simulados usados pelo scanner Top 12."""
        return list(DEFAULT_SIMULATED_SYMBOLS)

    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        if limit <= 0:
            raise ValueError("limit deve ser maior que zero")
        if limit > 500:
            raise ValueError("limit máximo permitido nesta Sprint é 500")

        clean_symbol = symbol.strip().upper()
        minutes = self._timeframe_to_minutes(timeframe)
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        start = now - timedelta(minutes=minutes * (limit - 1))

        candles: list[Candle] = []
        last_close = self._base_price_for(clean_symbol)
        random.seed(f"{clean_symbol}-{timeframe}-{limit}")

        for index in range(limit):
            timestamp = start + timedelta(minutes=minutes * index)
            movement = random.uniform(-0.00045, 0.00045)
            open_price = last_close
            close_price = max(0.00001, open_price + movement)
            high_price = max(open_price, close_price) + random.uniform(0.00005, 0.00025)
            low_price = min(open_price, close_price) - random.uniform(0.00005, 0.00025)
            volume = random.uniform(100, 1000)

            candle = Candle(
                symbol=clean_symbol,
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

    def health(self) -> dict:
        return {
            "provider": self.name,
            "connected": True,
            "status": "active",
            "supportsRealtime": self.supports_realtime,
            "supportsTrading": self.supports_trading,
            "symbols": len(DEFAULT_SIMULATED_SYMBOLS),
            "mode": "safe_development",
        }

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

    @staticmethod
    def _base_price_for(symbol: str) -> float:
        if "BTC" in symbol:
            return 65000.0
        if "ETH" in symbol:
            return 3500.0
        if "SOL" in symbol:
            return 150.0
        if "XAU" in symbol:
            return 2300.0
        return 1.10000
