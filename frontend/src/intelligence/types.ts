import type { AccountCurrency, DataQuality, Timeframe } from '../types/api';

export type MarketDiscoveryReadiness = 'ready' | 'partial' | 'blocked';

export type MarketSnapshot = {
  asset: string;
  timeframe: Timeframe;
  broker: string;
  account: string;
  currency: AccountCurrency | 'Não identificada';
  environment: 'DEMO' | 'REAL';
  updatedAt: string;
  dataSource: DataQuality | 'Não disponível';
  marketReady: boolean;
};

export type MarketDiscoveryItem = {
  label: string;
  value: string;
  status: 'success' | 'warning' | 'blocked' | 'neutral';
};

export type MarketSource = {
  provider: string;
  connectorStatus: string;
  marketDataQuality: string;
  syncStatus: string;
  lastSync: string;
  availability: string;
};

export type DiscoveryTimelineItem = {
  time: string;
  title: string;
  description: string;
  status: 'success' | 'warning' | 'blocked' | 'neutral';
};
