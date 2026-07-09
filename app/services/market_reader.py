from app.models.candle import Candle, MarketSnapshot, Timeframe
from app.providers.base import MarketDataProvider
from app.providers.manager import ProviderManager


class MarketReaderService:
    """Serviço central de leitura de mercado.

    A partir da Sprint 9, o Market Reader conversa com o ProviderManager, não
    diretamente com providers concretos. Isso permite trocar a fonte de dados no
    futuro sem alterar Signal Engine, Scanner, Decision Engine ou Backtesting.
    """

    def __init__(self, provider: MarketDataProvider | None = None, provider_manager: ProviderManager | None = None) -> None:
        self.provider_manager = provider_manager or ProviderManager()
        self.provider = provider or self.provider_manager.get_active_provider()

    def get_symbols(self) -> list[str]:
        """Retorna os ativos disponíveis no provider ativo."""
        return self.provider.get_symbols()

    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        """Retorna uma lista de candles normalizados."""
        clean_symbol = symbol.strip().upper()
        if not clean_symbol:
            raise ValueError("symbol é obrigatório")
        return self.provider.get_candles(symbol=clean_symbol, timeframe=timeframe, limit=limit)

    def get_snapshot(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> MarketSnapshot:
        """Retorna um resumo do mercado com o último candle."""
        clean_symbol = symbol.strip().upper()
        candles = self.get_candles(symbol=clean_symbol, timeframe=timeframe, limit=limit)
        return MarketSnapshot(
            provider=self.provider.name,
            symbol=clean_symbol,
            timeframe=timeframe,
            candles_count=len(candles),
            last_candle=candles[-1],
        )
