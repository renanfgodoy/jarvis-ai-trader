from abc import ABC, abstractmethod

from app.models.candle import Candle, Timeframe


class MarketDataProvider(ABC):
    """Contrato para qualquer fonte de dados de mercado.

    A IA não deve depender diretamente de uma corretora ou API específica.
    Cada integração futura deve implementar este contrato.
    """

    name: str

    @abstractmethod
    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        """Retorna candles normalizados."""
        raise NotImplementedError
