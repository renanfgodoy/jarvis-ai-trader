import type { AccountCurrency, DataQuality, MarketAsset as ApiMarketAsset, Timeframe } from '../types/api';

export type MarketDataTimeframe = Timeframe;
export type MarketDataEnvironment = 'DEMO' | 'REAL';

export type MarketAsset = {
  symbol: string;
  displayName: string;
  status: ApiMarketAsset['status'] | 'Não disponível';
  payout: number | null;
  category: string;
  provider: string;
  dataQuality: DataQuality | 'Não disponível';
  updatedAt: string;
};

export type MarketContext = {
  asset: string;
  timeframe: MarketDataTimeframe;
  broker: string;
  environment: MarketDataEnvironment;
  account: string;
  currency: AccountCurrency | 'Não disponível';
};

export type MarketSource = {
  provider: string;
  origin: string;
  dataQuality: DataQuality | 'Não disponível';
  connectorStatus: string;
  syncStatus: string;
};

export type MarketStatus = {
  market: string;
  connection: string;
  availability: string;
  lastUpdate: string;
};

export type MarketSnapshot = {
  context: MarketContext;
  source: MarketSource;
  status: MarketStatus;
  marketReady: boolean;
};

export type MarketAvailability = {
  totalAssets: number | 'Não disponível';
  openAssets: number | 'Não disponível';
  closedAssets: number | 'Não disponível';
  selectedAssetStatus: string;
  selectedAssetAvailable: boolean;
};
