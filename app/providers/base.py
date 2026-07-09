from abc import ABC, abstractmethod
from typing import Literal

from app.models.candle import Candle, Timeframe

ProviderName = Literal["simulated", "tradingview", "quadcode"]
ProviderStatus = Literal["active", "available", "disabled", "error", "not_implemented"]


class MarketDataProvider(ABC):
    """Contrato para qualquer fonte de dados de mercado.

    A IA não deve depender diretamente de uma corretora ou API específica.
    Cada integração futura deve implementar este contrato para que Market Reader,
    Signal Engine, Scanner, Backtesting e Execution Engine possam trocar de fonte
    sem reescrever suas regras internas.
    """

    name: ProviderName
    display_name: str
    supports_realtime: bool = False
    supports_trading: bool = False

    @abstractmethod
    def get_symbols(self) -> list[str]:
        """Retorna a lista de ativos disponíveis neste provider."""
        raise NotImplementedError

    @abstractmethod
    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        """Retorna candles normalizados."""
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict:
        """Retorna o estado operacional do provider."""
        raise NotImplementedError
