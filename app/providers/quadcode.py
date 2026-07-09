from app.models.candle import Candle, Timeframe
from app.providers.base import MarketDataProvider


class QuadcodePolariumProvider(MarketDataProvider):
    """Provider estrutural para Polarium/Quadcode em modo seguro.

    Nenhuma autenticação, leitura real ou execução de ordem é feita nesta Sprint.
    Este adapter apenas define o contrato que será usado futuramente para conta
    DEMO, respeitando a regra oficial: desenvolvimento sempre em ambiente demo.
    """

    name = "quadcode"
    display_name = "Quadcode / Polarium Provider"
    supports_realtime = True
    supports_trading = True

    def connect(self) -> dict:
        return {
            "connected": False,
            "mode": "DEMO_DISCOVERY",
            "message": "Conexão real ainda não implementada.",
        }

    def authenticate(self) -> dict:
        return {
            "authenticated": False,
            "mode": "DEMO_DISCOVERY",
            "message": "Autenticação real ainda não implementada.",
        }

    def get_symbols(self) -> list[str]:
        return []

    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        raise NotImplementedError("Quadcode/Polarium market data ainda não foi implementado nesta Sprint.")

    def get_balance(self) -> dict:
        return {
            "balance": None,
            "account_type": "DEMO",
            "message": "Leitura de saldo demo ainda não implementada.",
        }

    def health(self) -> dict:
        return {
            "provider": self.name,
            "connected": False,
            "status": "not_implemented",
            "supportsRealtime": self.supports_realtime,
            "supportsTrading": self.supports_trading,
            "accountType": "DEMO_ONLY",
            "message": "Adapter estrutural pronto. Nenhuma ordem real será executada.",
        }
