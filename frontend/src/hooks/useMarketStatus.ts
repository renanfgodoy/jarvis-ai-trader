import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getCurrentProvider, getMarketAssets, getMarketIntelligenceTop, getPolariumStatus } from '../services/api';
import type { Timeframe } from '../types/api';

export type MarketWorkspaceTimeframe = Timeframe;

export function useMarketStatus(selectedTimeframe: MarketWorkspaceTimeframe, enabled = true) {
  const apiTimeframe: Timeframe = selectedTimeframe;
  const marketAssets = useQuery({ queryKey: ['market-assets'], queryFn: getMarketAssets, refetchInterval: enabled ? 10000 : false, enabled });
  const provider = useQuery({ queryKey: ['provider-current'], queryFn: getCurrentProvider, refetchInterval: enabled ? 10000 : false, enabled });
  const polarium = useQuery({ queryKey: ['polarium-status'], queryFn: getPolariumStatus, refetchInterval: enabled ? 10000 : false, enabled });
  const scanner = useQuery({
    queryKey: ['market-workspace-scanner', apiTimeframe],
    queryFn: () => getMarketIntelligenceTop(apiTimeframe),
    refetchInterval: enabled ? 5000 : false,
    enabled
  });

  const lastUpdated = useMemo(() => {
    if (!enabled) return 'Não disponível';
    return new Date().toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }, [enabled, marketAssets.dataUpdatedAt, provider.dataUpdatedAt, polarium.dataUpdatedAt, scanner.dataUpdatedAt]);

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
