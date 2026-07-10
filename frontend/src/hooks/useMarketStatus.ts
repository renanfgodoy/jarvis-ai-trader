import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getCurrentProvider, getMarketAssets, getMarketIntelligenceTop, getPolariumStatus } from '../services/api';
import type { Timeframe } from '../types/api';

export type MarketWorkspaceTimeframe = Timeframe;

export function useMarketStatus(selectedTimeframe: MarketWorkspaceTimeframe) {
  const apiTimeframe: Timeframe = selectedTimeframe;
  const marketAssets = useQuery({ queryKey: ['market-assets'], queryFn: getMarketAssets, refetchInterval: 10000 });
  const provider = useQuery({ queryKey: ['provider-current'], queryFn: getCurrentProvider, refetchInterval: 10000 });
  const polarium = useQuery({ queryKey: ['polarium-status'], queryFn: getPolariumStatus, refetchInterval: 10000 });
  const scanner = useQuery({
    queryKey: ['market-workspace-scanner', apiTimeframe],
    queryFn: () => getMarketIntelligenceTop(apiTimeframe),
    refetchInterval: 5000,
    enabled: true
  });

  const lastUpdated = useMemo(() => new Date().toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }), [marketAssets.dataUpdatedAt, provider.dataUpdatedAt, polarium.dataUpdatedAt, scanner.dataUpdatedAt]);

  return {
    marketAssets,
    provider,
    polarium,
    scanner,
    apiTimeframe,
    lastUpdated,
    loading: marketAssets.isLoading || provider.isLoading || polarium.isLoading || scanner.isLoading
  };
}
