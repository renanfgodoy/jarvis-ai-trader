import { useMemo } from 'react';
import type { MarketAssetsResponse } from '../types/api';
import type { MarketAvailability } from './types';

export function useMarketAvailability(marketAssets: MarketAssetsResponse | undefined, selectedAsset: string): MarketAvailability {
  return useMemo(() => {
    const asset = marketAssets?.assets.find((item) => item.symbol === selectedAsset);
    return {
      totalAssets: marketAssets?.total_assets ?? 'Não disponível',
      openAssets: marketAssets?.open_assets ?? 'Não disponível',
      closedAssets: marketAssets?.closed_assets ?? 'Não disponível',
      selectedAssetStatus: asset?.status ?? 'Não disponível',
      selectedAssetAvailable: Boolean(asset?.is_tradable && asset.status === 'OPEN')
    };
  }, [marketAssets, selectedAsset]);
}
