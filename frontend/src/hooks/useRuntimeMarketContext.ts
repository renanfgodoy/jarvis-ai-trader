import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getCurrentProvider, getPolariumStatus } from '../services/api';
import { useMarketDataContext } from '../market-data/MarketDataContext';
import type { MarketContext, MarketSource, MarketStatus } from '../market-data/types';

export function useRuntimeMarketContext() {
  const shared = useMarketDataContext();
  const provider = useQuery({ queryKey: ['provider-current'], queryFn: getCurrentProvider, refetchInterval: 10000 });
  const polarium = useQuery({ queryKey: ['polarium-status'], queryFn: getPolariumStatus, refetchInterval: 10000 });

  const context = useMemo<MarketContext>(() => ({
    ...shared,
    broker: provider.data?.provider ?? provider.data?.active_provider ?? 'Não disponível',
    environment: polarium.data ? (polarium.data.demo_only === false ? 'REAL' : 'DEMO') : 'Não disponível',
    account: polarium.data?.email_masked ?? 'Não disponível',
    currency: polarium.data?.is_balance_synced && polarium.data.currency ? polarium.data.currency : 'Não disponível'
  }), [polarium.data, provider.data, shared]);

  const source = useMemo<MarketSource>(() => ({
    provider: context.broker,
    origin: context.broker,
    dataQuality: 'Não disponível',
    connectorStatus: polarium.data?.connected ? 'Conectado' : 'Não disponível',
    syncStatus: polarium.data?.sync_status ?? 'Não disponível'
  }), [context.broker, polarium.data]);

  const status = useMemo<MarketStatus>(() => ({
    market: 'Não disponível',
    connection: polarium.data?.connected ? 'Conectado' : 'Não disponível',
    availability: 'Não disponível',
    lastUpdate: polarium.data?.last_sync ?? 'Não verificada'
  }), [polarium.data]);

  return {
    context,
    polarium,
    provider,
    source,
    status,
    loading: provider.isLoading || polarium.isLoading
  };
}
