export type ProviderStatus = {
  provider?: string;
  active_provider?: string;
  connected?: boolean;
  supportsRealtime?: boolean;
  supportsTrading?: boolean;
  mode?: string;
  description?: string;
};

export type AssetScannerResult = {
  rank: number;
  symbol: string;
  signal?: string;
  score?: number;
  risk_level?: string;
  status?: string;
  trend?: string;
  volatility?: string;
  reasons?: string[];
};

export type AssetScannerResponse = {
  timeframe?: string;
  total_assets?: number;
  top_assets?: AssetScannerResult[];
  results?: AssetScannerResult[];
  disclaimer?: string;
};

export type SignalAnalysis = {
  symbol: string;
  timeframe: string;
  trend: string;
  ema9?: number;
  ema21?: number;
  rsi?: number;
  rsi14?: number;
  atr?: number;
  atr14?: number;
  volatility?: string;
  strength?: number;
  momentum?: string;
  reasons?: string[];
  warnings?: string[];
};

export type Candle = {
  symbol: string;
  timeframe: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
};

export type MarketCandlesResponse = {
  provider: string;
  symbol: string;
  timeframe: string;
  count: number;
  candles: Candle[];
  disclaimer?: string;
};

export type LiveWorkspaceResponse = {
  mode: string;
  symbol: string;
  timeframe: string;
  provider: string;
  candles: Candle[];
  signal: SignalAnalysis;
  top_assets: AssetScannerResult[];
  scanner_total: number;
  disclaimer?: string;
};

export type RiskCheck = {
  decision?: string;
  allowed?: boolean;
  risk_level?: string;
  risk_score?: number;
  bankroll?: number;
  recommended_entry?: number;
  max_entry_allowed?: number;
  official_rule?: string;
};

export type ExecutionStatus = {
  mode?: string;
  status?: string;
  executions?: number;
  demo_only?: boolean;
  dry_run?: boolean;
  last_execution?: unknown;
};

export type HealthResponse = {
  status: string;
  app: string;
  version: string;
  environment?: string;
};
