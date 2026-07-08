from app.core.config import settings
from app.models.candle import Candle, MarketSnapshot, Timeframe
from app.providers.base import MarketDataProvider
from app.providers.simulated import SimulatedMarketDataProvider


class MarketReaderService:
    """Serviço central de leitura de mercado.

    Ele isola o restante do sistema das fontes de dados. Amanhã podemos trocar
    o provider simulado por CSV, API pública, broker autorizado ou WebSocket
    sem alterar o Decision Engine.
    """

    def __init__(self, provider: MarketDataProvider | None = None) -> None:
        self.provider = provider or self._build_default_provider()

    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        """Retorna uma lista de candles normalizados."""
        clean_symbol = symbol.strip().upper()
        if not clean_symbol:
            raise ValueError("symbol é obrigatório")
        return self.provider.get_candles(symbol=clean_symbol, timeframe=timeframe, limit=limit)

    def get_snapshot(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> MarketSnapshot:
        """Retorna um resumo do mercado com o último candle."""
        candles = self.get_candles(symbol=symbol, timeframe=timeframe, limit=limit)
        return MarketSnapshot(
            provider=self.provider.name,
            symbol=symbol.strip().upper(),
            timeframe=timeframe,
            candles_count=len(candles),
            last_candle=candles[-1],
        )

    @staticmethod
    def _build_default_provider() -> MarketDataProvider:
        if settings.default_market_provider == "simulated":
            return SimulatedMarketDataProvider()
        raise ValueError(f"Provider não suportado: {settings.default_market_provider}")
