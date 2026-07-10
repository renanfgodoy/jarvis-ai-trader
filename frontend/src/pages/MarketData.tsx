import MarketAvailabilityCard from '../components/market-data/MarketAvailabilityCard';
import MarketContextCard from '../components/market-data/MarketContextCard';
import MarketDataSummaryCard from '../components/market-data/MarketDataSummaryCard';
import MarketDataTimeline from '../components/market-data/MarketDataTimeline';
import MarketSnapshotCard from '../components/market-data/MarketSnapshotCard';
import MarketSourceCard from '../components/market-data/MarketSourceCard';
import Loading from '../components/Loading';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import { brand } from '../branding/brand';
import { useMarketData } from '../market-data/useMarketData';

export default function MarketData() {
  const marketData = useMarketData();

  return (
    <PageContainer>
      <PageTitle eyebrow={brand.name} title="Market Data">
        <StatusBadge status={marketData.snapshot.marketReady ? 'ENGINE READY' : 'NÃO DISPONÍVEL'} tone={marketData.snapshot.marketReady ? 'success' : 'warning'} />
      </PageTitle>

      {marketData.loading && <Loading label="Carregando Market Data Engine" />}

      <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_380px]">
        <MarketDataSummaryCard snapshot={marketData.snapshot} />
        <MarketContextCard context={marketData.context} setAsset={marketData.context.setAsset} setTimeframe={marketData.context.setTimeframe} />
      </div>

      <MarketSnapshotCard snapshot={marketData.snapshot} />

      <div className="grid gap-3 xl:grid-cols-2">
        <MarketSourceCard source={marketData.source} />
        <MarketAvailabilityCard availability={marketData.availability} />
      </div>

      <MarketDataTimeline snapshot={marketData.snapshot} />
    </PageContainer>
  );
}
