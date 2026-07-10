import { useMemo } from 'react';
import MarketOverviewWidget from '../components/markets/MarketOverviewWidget';
import MarketScannerWidget from '../components/markets/MarketScannerWidget';
import MarketStatusWidget, { type MarketStatusItem } from '../components/markets/MarketStatusWidget';
import TimeframeSelector from '../components/markets/TimeframeSelector';
import WatchlistWidget from '../components/markets/WatchlistWidget';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import { brand } from '../branding/brand';
import { useMarketOverview } from '../hooks/useMarketOverview';
import { useMarketStatus } from '../hooks/useMarketStatus';
import { useWatchlist } from '../hooks/useWatchlist';
import { useMarketDataContext } from '../market-data/MarketDataContext';

export default function Markets() {
  const marketContext = useMarketDataContext();
  const market = useMarketStatus(marketContext.timeframe);
  const watchlist = useWatchlist(market.marketAssets.data?.assets ?? []);
  const overview = useMarketOverview({
    marketAssets: market.marketAssets.data,
    scannerActive: Boolean(market.scanner.data),
    selectedTimeframe: marketContext.timeframe,
    lastUpdated: market.lastUpdated
  });

  const currentMarket = market.marketAssets.data?.data_quality ?? 'Não disponível';
  const broker = market.provider.data?.provider ?? market.provider.data?.active_provider ?? 'Não disponível';
  const environment = market.polarium.data?.demo_only === false ? 'REAL' : 'DEMO';

  const statusItems = useMemo<MarketStatusItem[]>(() => [
    { label: 'Mercado', value: currentMarket, tone: currentMarket === 'Não disponível' ? 'neutral' : 'success' },
    { label: 'Aberto', value: market.marketAssets.data ? String(market.marketAssets.data.open_assets) : 'Não disponível', tone: market.marketAssets.data ? 'success' : 'neutral' },
    { label: 'Fechado', value: market.marketAssets.data ? String(market.marketAssets.data.closed_assets) : 'Não disponível', tone: market.marketAssets.data ? 'warning' : 'neutral' },
    { label: 'OTC', value: String(overview.otcCount), tone: overview.otcCount > 0 ? 'success' : 'neutral' },
    { label: 'Conectividade', value: broker, tone: broker === 'Não disponível' ? 'neutral' : 'success' },
    { label: 'Latência', value: 'Não disponível', tone: 'neutral' },
    { label: 'Última sincronização', value: market.lastUpdated, tone: 'success' }
  ], [broker, currentMarket, market.lastUpdated, market.marketAssets.data, overview.otcCount]);

  return (
    <PageContainer>
      <PageTitle eyebrow={brand.name} title="Markets">
        <StatusBadge status={currentMarket} tone={currentMarket === 'REAL' ? 'success' : currentMarket === 'Não disponível' ? 'neutral' : 'warning'} />
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <HeaderMetric label="Última atualização" value={market.lastUpdated} />
        <HeaderMetric label="Timeframe" value={marketContext.timeframe} />
        <HeaderMetric label="Mercado atual" value={currentMarket} />
        <HeaderMetric label="Broker conectado" value={broker} />
        <HeaderMetric label="Ambiente" value={environment} />
      </div>

      <TimeframeSelector selected={marketContext.timeframe} onSelect={marketContext.setTimeframe} />

      <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_360px]">
        <MarketScannerWidget
          scanner={market.scanner.data}
          marketAssets={market.marketAssets.data}
          selectedTimeframe={marketContext.timeframe}
          selectedSymbol={marketContext.asset}
          onSelectSymbol={marketContext.setAsset}
          loading={market.scanner.isLoading}
        />
        <WatchlistWidget items={watchlist.items} onSelect={(symbol) => {
          watchlist.setSelectedSymbol(symbol);
          marketContext.setAsset(symbol);
        }} />
      </div>

      <MarketStatusWidget items={statusItems} />
      <MarketOverviewWidget overview={overview} />
    </PageContainer>
  );
}

function HeaderMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </div>
  );
}
