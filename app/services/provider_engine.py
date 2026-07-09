from app.models.provider import ProviderInfo, TradingViewWebhookPayload, TradingViewWebhookResponse
from app.providers.tradingview_webhook import TradingViewWebhookProvider


class ProviderEngineService:
    """Orquestra os provedores disponíveis para o J.A.R.V.I.S AI TRADER.

    Esta camada evita que módulos como Market Reader, AI Decision Engine ou
    Risk Manager dependam diretamente de ferramentas externas.
    """

    def __init__(self, tradingview_provider: TradingViewWebhookProvider | None = None) -> None:
        self.tradingview_provider = tradingview_provider or TradingViewWebhookProvider()

    def receive_tradingview_webhook(
        self,
        payload: TradingViewWebhookPayload,
    ) -> TradingViewWebhookResponse:
        """Recebe alertas do TradingView para futura análise interna."""
        return self.tradingview_provider.receive(payload)

    def list_providers(self) -> list[ProviderInfo]:
        """Lista providers disponíveis nesta etapa do projeto."""
        return [
            ProviderInfo(
                name="simulated",
                type="market_data",
                status="active",
                description="Provider simulado usado para desenvolvimento e testes.",
            ),
            ProviderInfo(
                name="TradingView",
                type="webhook",
                status="active",
                description="Recebe alertas via webhook. Não executa ordens.",
            ),
        ]
