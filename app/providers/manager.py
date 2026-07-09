from app.core.config import settings
from app.models.candle import Candle, Timeframe
from app.models.provider import ProviderCurrentResponse, ProviderManagerItem
from app.models.market_asset import MarketAsset, MarketAssetsResponse
from app.providers.base import MarketDataProvider
from app.providers.quadcode import QuadcodePolariumProvider
from app.providers.simulated import SimulatedMarketDataProvider
from app.providers.tradingview import TradingViewMarketDataProvider


class ProviderManager:
    """Seleciona e abstrai o provider de dados ativo do J.A.R.V.I.S.

    A partir desta Sprint, módulos como Market Reader e Scanner não precisam
    conhecer classes concretas de providers. Eles conversam com o Manager, que
    entrega o provider configurado e centraliza a troca futura de fonte de dados.
    """

    def __init__(self, active_provider_name: str | None = None) -> None:
        self.active_provider_name = (active_provider_name or settings.default_market_provider).strip().lower()
        self._providers: dict[str, MarketDataProvider] = {
            "simulated": SimulatedMarketDataProvider(),
            "tradingview": TradingViewMarketDataProvider(),
            "quadcode": QuadcodePolariumProvider(),
        }

    def get_active_provider(self) -> MarketDataProvider:
        provider = self._providers.get(self.active_provider_name)
        if provider is None:
            raise ValueError(f"Provider não suportado: {self.active_provider_name}")
        return provider

    def get_symbols(self) -> list[str]:
        return self.get_active_provider().get_symbols()

    def get_assets(self) -> list[MarketAsset]:
        return self.get_active_provider().get_assets()

    def get_assets_response(self) -> MarketAssetsResponse:
        provider = self.get_active_provider()
        assets = provider.get_assets()
        data_quality = "SIMULATED" if provider.name == "simulated" else "UNAVAILABLE"
        if assets:
            data_quality = assets[0].data_quality
        return MarketAssetsResponse(
            provider=provider.name,
            data_quality=data_quality,
            total_assets=len(assets),
            open_assets=sum(1 for asset in assets if asset.status == "OPEN"),
            closed_assets=sum(1 for asset in assets if asset.status != "OPEN"),
            simulated=data_quality == "SIMULATED",
            assets=assets,
            message=(
                "Provider simulado ativo: estrutura pronta para receber dados reais."
                if data_quality == "SIMULATED"
                else "Provider real/externo ainda não conectado nesta versão."
            ),
        )

    def get_candles(self, symbol: str, timeframe: Timeframe = "M1", limit: int = 100) -> list[Candle]:
        return self.get_active_provider().get_candles(symbol=symbol, timeframe=timeframe, limit=limit)

    def current(self) -> ProviderCurrentResponse:
        provider = self.get_active_provider()
        health = provider.health()
        return ProviderCurrentResponse(
            provider=provider.name,
            display_name=provider.display_name,
            connected=bool(health.get("connected", False)),
            status=str(health.get("status", "unknown")),
            supports_realtime=provider.supports_realtime,
            supports_trading=provider.supports_trading,
            account_mode="DEMO_ONLY" if provider.name == "quadcode" else "DEVELOPMENT",
            health=health,
        )

    def list_providers(self) -> list[ProviderManagerItem]:
        active = self.get_active_provider().name
        items: list[ProviderManagerItem] = []
        for provider in self._providers.values():
            health = provider.health()
            is_active = provider.name == active
            items.append(
                ProviderManagerItem(
                    name=provider.name,
                    display_name=provider.display_name,
                    status="active" if is_active else str(health.get("status", "available")),
                    active=is_active,
                    connected=bool(health.get("connected", False)),
                    supports_realtime=provider.supports_realtime,
                    supports_trading=provider.supports_trading,
                    description=self._description_for(provider.name),
                )
            )
        return items

    @staticmethod
    def _description_for(name: str) -> str:
        descriptions = {
            "simulated": "Provider simulado com múltiplos ativos para desenvolvimento e testes.",
            "tradingview": "Estrutura para alertas/dados autorizados do TradingView. Não executa ordens.",
            "quadcode": "Estrutura futura para Polarium/Quadcode em conta DEMO. Sem ordem real nesta Sprint.",
        }
        return descriptions.get(name, "Provider registrado no Manager.")
