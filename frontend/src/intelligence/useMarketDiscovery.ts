import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getCurrentProvider, getMarketAssets, getPolariumStatus } from '../services/api';
import type { Timeframe } from '../types/api';
import { useMarketSnapshot } from './useMarketSnapshot';
import type { DiscoveryTimelineItem, MarketDiscoveryItem, MarketDiscoveryReadiness, MarketSource } from './types';

export function useMarketDiscovery(asset: string, timeframe: Timeframe) {
  const marketAssets = useQuery({ queryKey: ['market-assets'], queryFn: getMarketAssets, refetchInterval: 10000 });
  const provider = useQuery({ queryKey: ['provider-current'], queryFn: getCurrentProvider, refetchInterval: 10000 });
  const polarium = useQuery({ queryKey: ['polarium-status'], queryFn: getPolariumStatus, refetchInterval: 10000 });

  const updatedAt = useMemo(() => new Date().toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }), [marketAssets.dataUpdatedAt, provider.dataUpdatedAt, polarium.dataUpdatedAt]);

  const snapshot = useMarketSnapshot({
    asset,
    timeframe,
    marketAssets: marketAssets.data,
    provider: provider.data,
    account: polarium.data,
    updatedAt
  });

  const source: MarketSource = useMemo(() => ({
    provider: snapshot.broker,
    connectorStatus: polarium.data?.connected ? 'Conectado' : 'Não conectado',
    marketDataQuality: marketAssets.data?.data_quality ?? 'Não disponível',
    syncStatus: polarium.data?.sync_status ?? 'Não disponível',
    lastSync: polarium.data?.last_sync ?? 'Não disponível',
    availability: marketAssets.data ? `${marketAssets.data.open_assets}/${marketAssets.data.total_assets} ativos abertos` : 'Não disponível'
  }), [marketAssets.data, polarium.data, snapshot.broker]);

  const discovery: MarketDiscoveryItem[] = useMemo(() => [
    { label: 'Ativo selecionado', value: snapshot.asset, status: snapshot.asset ? 'success' : 'blocked' },
    { label: 'Timeframe', value: snapshot.timeframe, status: snapshot.timeframe ? 'success' : 'blocked' },
    { label: 'Status do mercado', value: marketAssets.data?.data_quality ?? 'Não disponível', status: marketAssets.data ? 'success' : 'neutral' },
    { label: 'Status do Connector', value: source.connectorStatus, status: polarium.data?.connected ? 'success' : 'warning' },
    { label: 'Última atualização', value: snapshot.updatedAt, status: 'success' },
    { label: 'Fonte dos dados', value: source.provider, status: source.provider === 'Não disponível' ? 'neutral' : 'success' },
    { label: 'Disponibilidade', value: source.availability, status: marketAssets.data ? 'success' : 'neutral' }
  ], [marketAssets.data, polarium.data?.connected, snapshot, source]);

  const readiness: MarketDiscoveryReadiness = snapshot.marketReady
    ? (polarium.data?.connected ? 'ready' : 'partial')
    : 'blocked';

  const timeline: DiscoveryTimelineItem[] = useMemo(() => [
    {
      time: snapshot.updatedAt,
      title: 'Ativo observado',
      description: `${snapshot.asset} em ${snapshot.timeframe}`,
      status: 'success'
    },
    {
      time: snapshot.updatedAt,
      title: 'Fonte verificada',
      description: source.provider,
      status: source.provider === 'Não disponível' ? 'neutral' : 'success'
    },
    {
      time: snapshot.updatedAt,
      title: 'Conta avaliada',
      description: snapshot.account,
      status: snapshot.account === 'Não identificada' ? 'warning' : 'success'
    },
    {
      time: snapshot.updatedAt,
      title: 'Market Ready',
      description: snapshot.marketReady ? 'Dados mínimos disponíveis para futura IA.' : 'Dados insuficientes para discovery completo.',
      status: snapshot.marketReady ? 'success' : 'blocked'
    }
  ], [snapshot, source.provider]);

  return {
    snapshot,
    discovery,
    source,
    readiness,
    timeline,
    marketAssets,
    provider,
    polarium,
    loading: marketAssets.isLoading || provider.isLoading || polarium.isLoading
  };
}
