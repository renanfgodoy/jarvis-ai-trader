import { useMemo } from 'react';
import type { MarketAssetsResponse, PolariumAccountState, ProviderStatus } from '../types/api';
import { useMarketDataContext } from './MarketDataContext';
import type { MarketContext } from './types';

export function useMarketContext({
  marketAssets,
  provider,
  account
}: {
  marketAssets?: MarketAssetsResponse;
  provider?: ProviderStatus;
  account?: PolariumAccountState;
} = {}) {
  const context = useMarketDataContext();

  return useMemo<MarketContext & typeof context>(() => ({
    ...context,
    broker: provider?.provider ?? provider?.active_provider ?? marketAssets?.provider ?? 'Não disponível',
    environment: account ? (account.demo_only === false ? 'REAL' : 'DEMO') : 'Não disponível',
    account: account?.email_masked ?? 'Não disponível',
    currency: account?.is_balance_synced && account.currency ? account.currency : 'Não disponível'
  }), [account, context, marketAssets, provider]);
}
