import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import type { MarketDataTimeframe } from './types';

type MarketDataState = {
  asset: string;
  timeframe: MarketDataTimeframe;
  setAsset: (asset: string) => void;
  setTimeframe: (timeframe: MarketDataTimeframe) => void;
};

const MarketDataContext = createContext<MarketDataState | null>(null);

export function MarketDataProvider({ children }: { children: ReactNode }) {
  const [asset, setAssetState] = useState('');
  const [timeframe, setTimeframe] = useState<MarketDataTimeframe>('M1');

  const value = useMemo<MarketDataState>(() => ({
    asset,
    timeframe,
    setAsset: (nextAsset) => setAssetState(nextAsset.trim().toUpperCase()),
    setTimeframe
  }), [asset, timeframe]);

  return <MarketDataContext.Provider value={value}>{children}</MarketDataContext.Provider>;
}

export function useMarketDataContext() {
  const context = useContext(MarketDataContext);
  if (!context) {
    throw new Error('useMarketDataContext must be used inside MarketDataProvider');
  }
  return context;
}
