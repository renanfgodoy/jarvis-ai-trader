from app.models.candle import Candle, Timeframe
from app.providers.base import MarketDataProvider


class TradingViewMarketDataProvider(MarketDataProvider):
    """Provider estrutural para integração futura com TradingView.

    Nesta Sprint ele não consome dados reais. O objetivo é deixar a arquitetura
    pronta para receber dados autorizados ou webhooks normalizados sem acoplar
    o restante do sistema à implementação específica.
    """

    name = "tradingview"
    display_name = "TradingView Provider"
    supports_realtime = True
    supports_trading = False

    def get_symbols(self) -> list[str]:
        return []

    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        raise NotImplementedError("TradingView market data ainda não foi implementado nesta Sprint.")

    def health(self) -> dict:
        return {
            "provider": self.name,
            "connected": False,
            "status": "not_implemented",
            "supportsRealtime": self.supports_realtime,
            "supportsTrading": self.supports_trading,
            "message": "Estrutura criada. Integração real depende de fonte autorizada.",
        }
