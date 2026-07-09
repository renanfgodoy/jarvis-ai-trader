from app.models.market_asset import MarketAssetsResponse
from app.models.provider import (
    ProviderCurrentResponse,
    ProviderInfo,
    ProviderManagerItem,
    TradingViewWebhookPayload,
    TradingViewWebhookResponse,
)
from app.providers.manager import ProviderManager
from app.providers.tradingview_webhook import TradingViewWebhookProvider


class ProviderEngineService:
    """Orquestra os provedores disponíveis para o J.A.R.V.I.S AI TRADER.

    Esta camada evita que módulos como Market Reader, AI Decision Engine ou
    Risk Manager dependam diretamente de ferramentas externas.
    """

    def __init__(
        self,
        tradingview_provider: TradingViewWebhookProvider | None = None,
        provider_manager: ProviderManager | None = None,
    ) -> None:
        self.tradingview_provider = tradingview_provider or TradingViewWebhookProvider()
        self.provider_manager = provider_manager or ProviderManager()

    def receive_tradingview_webhook(
        self,
        payload: TradingViewWebhookPayload,
    ) -> TradingViewWebhookResponse:
        """Recebe alertas do TradingView para futura análise interna."""
        return self.tradingview_provider.receive(payload)

    def list_providers(self) -> list[ProviderInfo]:
        """Lista providers disponíveis nesta etapa do projeto.

        Mantém compatibilidade com o endpoint /providers criado na Sprint 5.
        """
        manager_items = self.provider_manager.list_providers()
        legacy_items = [
            ProviderInfo(
                name=item.display_name if item.name != "simulated" else "simulated",
                type="market_data" if item.name in {"simulated", "quadcode"} else "webhook",
                status=item.status,
                description=item.description,
            )
            for item in manager_items
        ]
        legacy_items.append(
            ProviderInfo(
                name="TradingView",
                type="webhook",
                status="active",
                description="Recebe alertas via webhook. Não executa ordens.",
            )
        )
        return legacy_items

    def current_provider(self) -> ProviderCurrentResponse:
        """Retorna o provider ativo usado por Market Reader e Scanner."""
        return self.provider_manager.current()

    def market_assets(self) -> MarketAssetsResponse:
        """Retorna ativos do provider ativo com payout/status/qualidade."""
        return self.provider_manager.get_assets_response()

    def list_provider_manager_items(self) -> list[ProviderManagerItem]:
        """Lista providers registrados no Provider Manager."""
        return self.provider_manager.list_providers()
