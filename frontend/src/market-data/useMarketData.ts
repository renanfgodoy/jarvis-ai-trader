import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getCurrentProvider, getMarketAssets, getPolariumStatus } from '../services/api';
import { useMarketAvailability } from './useMarketAvailability';
import { useMarketContext } from './useMarketContext';
import type { MarketAsset, MarketSnapshot, MarketSource, MarketStatus } from './types';

export function useMarketData() {
  const marketAssets = useQuery({ queryKey: ['market-assets'], queryFn: getMarketAssets, refetchInterval: 10000 });
  const provider = useQuery({ queryKey: ['provider-current'], queryFn: getCurrentProvider, refetchInterval: 10000 });
  const polarium = useQuery({ queryKey: ['polarium-status'], queryFn: getPolariumStatus, refetchInterval: 10000 });
  const context = useMarketContext({ marketAssets: marketAssets.data, provider: provider.data, account: polarium.data });
  const availability = useMarketAvailability(marketAssets.data, context.asset);

  const lastUpdate = useMemo(() => new Date().toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }), [marketAssets.dataUpdatedAt, provider.dataUpdatedAt, polarium.dataUpdatedAt]);

  const assets = useMemo<MarketAsset[]>(() => (marketAssets.data?.assets ?? []).map((asset) => ({
    symbol: asset.symbol,
    displayName: asset.display_name,
    status: asset.status,
    payout: asset.payout,
    category: asset.category,
    provider: asset.provider,
    dataQuality: asset.data_quality,
    updatedAt: asset.updated_at
  })), [marketAssets.data]);

  const source = useMemo<MarketSource>(() => ({
    provider: context.broker,
    origin: marketAssets.data?.provider ?? 'Não disponível',
    dataQuality: marketAssets.data?.data_quality ?? 'Não disponível',
    connectorStatus: polarium.data?.connected ? 'Conectado' : 'Não disponível',
    syncStatus: polarium.data?.sync_status ?? 'Não disponível'
  }), [context.broker, marketAssets.data, polarium.data]);

  const status = useMemo<MarketStatus>(() => ({
    market: marketAssets.data?.data_quality ?? 'Não disponível',
    connection: polarium.data?.connected ? 'Conectado' : 'Não disponível',
    availability: marketAssets.data ? `${marketAssets.data.open_assets}/${marketAssets.data.total_assets} ativos abertos` : 'Não disponível',
    lastUpdate
  }), [lastUpdate, marketAssets.data, polarium.data]);

  const snapshot = useMemo<MarketSnapshot>(() => ({
    context,
    source,
    status,
    marketReady: Boolean(marketAssets.data && context.asset && context.timeframe && source.provider !== 'Não disponível')
  }), [context, marketAssets.data, source, status]);

  return {
    assets,
    availability,
    context,
    marketAssets,
    provider,
    polarium,
    snapshot,
    source,
    status,
    loading: marketAssets.isLoading || provider.isLoading || polarium.isLoading
  };
}
