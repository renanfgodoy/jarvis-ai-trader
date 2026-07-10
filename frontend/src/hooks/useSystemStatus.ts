import { useQuery } from '@tanstack/react-query';
import { getCurrentProvider, getHealth, getMarketAssets } from '../services/api';

export function useSystemStatus() {
  const health = useQuery({ queryKey: ['health'], queryFn: getHealth, refetchInterval: 5000 });
  const provider = useQuery({ queryKey: ['provider'], queryFn: getCurrentProvider, refetchInterval: 5000 });
  const marketAssets = useQuery({ queryKey: ['market-assets'], queryFn: getMarketAssets, refetchInterval: 5000 });

  return { health, provider, marketAssets };
}
