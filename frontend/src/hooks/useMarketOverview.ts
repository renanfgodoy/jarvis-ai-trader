import { useMemo } from 'react';
import type { MarketAssetsResponse, Timeframe } from '../types/api';

export function useMarketOverview({
  marketAssets,
  scannerActive,
  selectedTimeframe,
  lastUpdated
}: {
  marketAssets?: MarketAssetsResponse;
  scannerActive: boolean;
  selectedTimeframe: Timeframe;
  lastUpdated: string;
}) {
  return useMemo(() => {
    const assets = marketAssets?.assets ?? [];
    const otcCount = assets.filter((asset) => asset.symbol.includes('-OTC') || asset.category.toUpperCase().includes('OTC')).length;

    return {
      totalAssets: marketAssets?.total_assets ?? assets.length,
      otcCount,
      synchronized: marketAssets ? (marketAssets.data_quality !== 'UNAVAILABLE' ? 'Sim' : 'Não disponível') : 'Não disponível',
      scannerStatus: scannerActive ? 'Ativo' : 'Não disponível',
      lastUpdated
    };
  }, [lastUpdated, marketAssets, scannerActive, selectedTimeframe]);
}
