import { useQuery } from '@tanstack/react-query';
import { getMarketIntelligenceTop } from '../services/api';
import type { Timeframe } from '../types/api';

export function useMarketScanner(timeframe: Timeframe, enabled: boolean) {
  return useQuery({
    queryKey: ['market-workspace-scanner', timeframe],
    queryFn: () => getMarketIntelligenceTop(timeframe),
    refetchInterval: enabled ? 5000 : false,
    enabled
  });
}
