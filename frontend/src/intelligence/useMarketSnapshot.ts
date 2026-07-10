import { useMemo } from 'react';
import type { MarketAssetsResponse, PolariumAccountState, ProviderStatus, Timeframe } from '../types/api';
import type { MarketSnapshot } from './types';

export function useMarketSnapshot({
  asset,
  timeframe,
  marketAssets,
  provider,
  account,
  updatedAt
}: {
  asset: string;
  timeframe: Timeframe;
  marketAssets?: MarketAssetsResponse;
  provider?: ProviderStatus;
  account?: PolariumAccountState;
  updatedAt: string;
}): MarketSnapshot {
  return useMemo(() => {
    const broker = provider?.provider ?? provider?.active_provider ?? marketAssets?.provider ?? 'Não disponível';
    const syncedCurrency = account?.is_balance_synced && account.currency ? account.currency : 'Não identificada';
    const marketReady = Boolean(
      asset &&
      timeframe &&
      marketAssets &&
      marketAssets.data_quality !== 'UNAVAILABLE' &&
      broker !== 'Não disponível'
    );

    return {
      asset,
      timeframe,
      broker,
      account: account?.email_masked ?? 'Não identificada',
      currency: syncedCurrency,
      environment: account?.demo_only === false ? 'REAL' : 'DEMO',
      updatedAt,
      dataSource: marketAssets?.data_quality ?? 'Não disponível',
      marketReady
    };
  }, [account, asset, marketAssets, provider, timeframe, updatedAt]);
}
