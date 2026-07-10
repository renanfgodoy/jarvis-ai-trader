import EmptyState from '../../EmptyState';
import Loading from '../../Loading';
import TopAssets from '../../TopAssets';
import type { AssetScannerResult, MarketAssetsResponse, MarketIntelligenceScannerResponse } from '../../../types/api';
import type { MarketWorkspaceTimeframe } from '../../../hooks/useMarketStatus';

export default function MarketScannerWidget({
  scanner,
  marketAssets,
  selectedTimeframe,
  selectedSymbol,
  onSelectSymbol,
  loading
}: {
  scanner?: MarketIntelligenceScannerResponse;
  marketAssets?: MarketAssetsResponse;
  selectedTimeframe: MarketWorkspaceTimeframe;
  selectedSymbol?: string;
  onSelectSymbol: (symbol: string) => void;
  loading: boolean;
}) {
  if (loading && !scanner) return <Loading label="Carregando scanner de mercado" />;

  const assets: AssetScannerResult[] = (scanner?.results ?? []).map((asset, index) => ({
    rank: index + 1,
    symbol: asset.symbol,
    timeframe: asset.timeframe,
    signal: asset.signal,
    score: asset.score,
    risk_level: asset.risk_bias,
    status: asset.status,
    trend: asset.trend,
    volatility: asset.volatility,
    reasons: asset.reasons,
    payout: asset.payout,
    data_quality: marketAssets?.data_quality,
    market_status: marketAssets?.assets.find((item) => item.symbol === asset.symbol)?.status ?? 'Não disponível'
  }));

  if (!assets.length) {
    return <EmptyState title="Nenhum ativo disponível" message="A fonte atual não retornou ativos para o scanner. Nenhum ativo será inventado." />;
  }

  return (
    <TopAssets
      assets={assets}
      selectedSymbol={selectedSymbol}
      onSelect={onSelectSymbol}
      dataQuality={marketAssets?.data_quality ?? 'Não disponível'}
      totalAssets={marketAssets?.total_assets ?? 0}
      openAssets={marketAssets?.open_assets ?? 0}
    />
  );
}
