from app.models.candle import Candle, Timeframe
from app.models.quadcode import (
    QuadcodeConnectionResponse,
    QuadcodeDemoConnectRequest,
    QuadcodeDemoOrderRequest,
    QuadcodeDemoOrderResponse,
    QuadcodeSymbolInfo,
    QuadcodeSymbolsResponse,
)
from app.providers.base import MarketDataProvider

QUADCODE_DEMO_SYMBOLS: tuple[str, ...] = (
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
    "GOOGLE/MSFT-OTC",
    "APPLE/AMZN-OTC",
    "TESLA/FACEBOOK-OTC",
    "AUDCAD-OTC",
    "EURCAD-OTC",
    "AUDJPY-OTC",
)

SAFETY_RULES = [
    "Conta real bloqueada durante desenvolvimento",
    "Somente DEMO/DRY_RUN nesta Sprint",
    "Nenhuma ordem é enviada para a Polarium",
    "Toda execução futura deve passar pelo Risk Manager",
    "Primeiro proteger a banca. Depois crescer a banca.",
]


class QuadcodePolariumProvider(MarketDataProvider):
    """Adapter seguro para Polarium/Quadcode em modo DEMO/Discovery.

    Esta Sprint cria a camada de integração e contratos de dados, mas não realiza
    autenticação real, scraping, bypass, nem envio de ordens. A intenção é preparar
    o J.A.R.V.I.S para uma futura integração permitida e validada em conta DEMO.
    """

    name = "quadcode"
    display_name = "Quadcode / Polarium Provider"
    supports_realtime = True
    supports_trading = True

    def __init__(self) -> None:
        self._demo_connected = False
        self._last_mode = "DEMO"

    def connect(self, request: QuadcodeDemoConnectRequest | None = None) -> QuadcodeConnectionResponse:
        request = request or QuadcodeDemoConnectRequest()

        if request.account_type != "DEMO" or request.allow_real_orders:
            self._demo_connected = False
            return QuadcodeConnectionResponse(
                mode="DEMO",
                status="BLOCKED",
                connected=False,
                dry_run=True,
                accountType="DEMO_ONLY",
                canTrade=False,
                message="Conexão bloqueada: o J.A.R.V.I.S só permite DEMO/DRY_RUN nesta fase.",
                safetyRules=SAFETY_RULES,
            )

        self._demo_connected = True
        self._last_mode = request.mode
        return QuadcodeConnectionResponse(
            mode=request.mode,
            status="CONNECTED",
            connected=True,
            dry_run=True,
            accountType="DEMO",
            canTrade=False,
            message="Adapter Quadcode/Polarium preparado em modo DEMO/DRY_RUN. Nenhuma ordem real será enviada.",
            safetyRules=SAFETY_RULES,
        )

    def disconnect(self) -> QuadcodeConnectionResponse:
        self._demo_connected = False
        return QuadcodeConnectionResponse(
            mode="DEMO",
            status="DISCONNECTED",
            connected=False,
            dry_run=True,
            accountType="DEMO",
            canTrade=False,
            message="Adapter Quadcode/Polarium desconectado do modo DEMO.",
            safetyRules=SAFETY_RULES,
        )

    def authenticate(self) -> dict:
        return {
            "authenticated": False,
            "mode": "DEMO_DISCOVERY",
            "message": "Autenticação real ainda não implementada. Não informe senha no J.A.R.V.I.S nesta fase.",
        }

    def get_symbols(self) -> list[str]:
        return list(QUADCODE_DEMO_SYMBOLS)

    def get_symbol_catalog(self) -> QuadcodeSymbolsResponse:
        symbols = [QuadcodeSymbolInfo(symbol=symbol) for symbol in QUADCODE_DEMO_SYMBOLS]
        return QuadcodeSymbolsResponse(total=len(symbols), symbols=symbols)

    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        raise NotImplementedError(
            "Quadcode/Polarium candles reais ainda não foram implementados. Use simulated provider para dados de desenvolvimento."
        )

    def dry_run_order(self, request: QuadcodeDemoOrderRequest) -> QuadcodeDemoOrderResponse:
        if not request.dry_run:
            return QuadcodeDemoOrderResponse(
                accepted=False,
                executed=False,
                symbol=request.symbol,
                signal=request.signal,
                entryValue=request.entry_value,
                timeframe=request.timeframe,
                message="Ordem bloqueada: dryRun=false não é permitido nesta Sprint.",
                blockedReason="REAL_ORDER_BLOCKED",
            )

        return QuadcodeDemoOrderResponse(
            accepted=True,
            executed=False,
            symbol=request.symbol,
            signal=request.signal,
            entryValue=request.entry_value,
            timeframe=request.timeframe,
            message="Ordem recebida em DRY_RUN. Nenhum clique, API ou ordem foi enviado para a Polarium.",
            blockedReason=None,
        )

    def get_balance(self) -> dict:
        return {
            "balance": None,
            "account_type": "DEMO",
            "message": "Leitura de saldo demo será implementada somente após validação técnica da integração.",
        }

    def health(self) -> dict:
        return {
            "provider": self.name,
            "connected": self._demo_connected,
            "status": "demo_ready" if self._demo_connected else "ready",
            "supportsRealtime": self.supports_realtime,
            "supportsTrading": self.supports_trading,
            "accountType": "DEMO_ONLY",
            "symbols": len(QUADCODE_DEMO_SYMBOLS),
            "canTrade": False,
            "mode": self._last_mode,
            "message": "Adapter seguro pronto para DEMO/Discovery. Nenhuma ordem real será executada.",
        }
