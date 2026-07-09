export type Timeframe = 'M1' | 'M5' | 'M15';
export type AccountCurrency = 'BRL' | 'USD';
export type AccountType = 'DEMO' | 'REAL';


export type DataQuality = 'SIMULATED' | 'REAL' | 'DELAYED' | 'UNAVAILABLE';
export type PolariumDataSource = 'REAL_SESSION' | 'DEVTOOLS_PAYLOAD' | 'SIMULATED' | 'CACHE' | 'UNAVAILABLE';
export type PolariumSyncStatus = 'SYNCED' | 'NOT_SYNCED' | 'FAILED' | 'CACHE_ONLY';

export type MarketAsset = {
  symbol: string;
  display_name: string;
  category: string;
  status: 'OPEN' | 'CLOSED' | 'SUSPENDED';
  payout: number;
  supported_timeframes: Timeframe[];
  data_quality: DataQuality;
  provider: string;
  is_tradable: boolean;
  updated_at: string;
};

export type MarketAssetsResponse = {
  provider: string;
  data_quality: DataQuality;
  total_assets: number;
  open_assets: number;
  closed_assets: number;
  simulated: boolean;
  assets: MarketAsset[];
  message: string;
  disclaimer?: string;
};

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
  timeframe?: string;
  signal?: string;
  score?: number;
  risk_level?: string;
  status?: string;
  trend?: string;
  volatility?: string;
  reasons?: string[];
  payout?: number;
  data_quality?: DataQuality;
  market_status?: string;
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
  countdown_seconds?: number;
  last_price?: number;
  events?: string[];
  disclaimer?: string;
};

export type LiveTick = {
  type: string;
  mode: string;
  symbol: string;
  timeframe: string;
  provider: string;
  server_time: string;
  price: number;
  candle: Candle;
  candles: Candle[];
  countdown_seconds: number;
  signal: SignalAnalysis;
  top_assets: AssetScannerResult[];
  scanner_total: number;
  events: string[];
  demo_only: boolean;
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
  account_currency?: AccountCurrency;
  currency_symbol?: string;
  minimum_entry?: number;
};

export type ExecutionStatus = {
  mode?: string;
  status?: string;
  executions?: number;
  demo_only?: boolean;
  dry_run?: boolean;
  last_execution?: unknown;
  supported_timeframes?: Timeframe[];
  supported_currencies?: AccountCurrency[];
};

export type AutoTradeGateRequest = {
  symbol: string;
  timeframe: Timeframe | null;
  account_type: AccountType;
  currency: AccountCurrency;
  balance: number;
  entry_value?: number | null;
  score: number;
  minimum_score: number;
  risk_approved: boolean;
  websocket_online: boolean;
  execution_ready: boolean;
  asset_valid: boolean;
  autotrade_requested: boolean;
};

export type AutoTradeGateResponse = {
  allowed: boolean;
  status: 'READY' | 'BLOCKED' | 'WAITING';
  symbol: string;
  timeframe: Timeframe | null;
  account_type: AccountType;
  currency: AccountCurrency;
  currency_symbol: string;
  balance: number;
  entry_value: number;
  minimum_entry: number;
  score: number;
  minimum_score: number;
  can_analyze: boolean;
  autotrade_enabled: boolean;
  reasons: string[];
  warnings: string[];
  safety_rules: string[];
};

export type IntelligenceFactor = {
  name: string;
  points: number;
  max_points: number;
  passed: boolean;
  explanation: string;
};

export type MarketIntelligence = {
  symbol: string;
  timeframe: Timeframe;
  signal: string;
  score: number;
  status: string;
  confidence_label: string;
  payout: number;
  minimum_score: number;
  minimum_payout: number;
  risk_bias: string;
  trend: string;
  momentum: string;
  volatility: string;
  ema9: number;
  ema21: number;
  rsi14: number;
  atr14: number;
  strength: number;
  factors: IntelligenceFactor[];
  reasons: string[];
  warnings: string[];
  action: string;
};

export type MarketIntelligenceScannerResponse = {
  timeframe: Timeframe;
  assets_scanned: number;
  top_limit: number;
  minimum_score: number;
  minimum_payout: number;
  approved_count: number;
  watchlist_count: number;
  blocked_count: number;
  results: MarketIntelligence[];
};


export type PolariumAccountState = {
  connected: boolean;
  status: 'CONNECTED' | 'DISCONNECTED' | 'BLOCKED';
  account_mode: AccountType;
  currency?: AccountCurrency | null;
  currency_symbol?: string | null;
  balance?: number | null;
  minimum_entry?: number | null;
  demo_only: boolean;
  email_masked?: string | null;
  session_cached: boolean;
  session_id?: string | null;
  provider: string;
  data_source: PolariumDataSource;
  sync_status: PolariumSyncStatus;
  is_balance_synced: boolean;
  last_sync?: string | null;
  last_sync_error?: string | null;
  warnings: string[];
  safety_rules: string[];
};

export type PolariumLoginRequest = {
  email: string;
  password: string;
  force_demo?: boolean;
  remember_session?: boolean;
};

export type PolariumLoginResponse = {
  success: boolean;
  message: string;
  account: PolariumAccountState;
};

export type PolariumSyncResponse = {
  success: boolean;
  message: string;
  account: PolariumAccountState;
};

export type PolariumLogoutResponse = {
  success: boolean;
  message: string;
};

export type HealthResponse = {
  status: string;
  app: string;
  version: string;
  environment?: string;
};


export type PolariumWsDebugRequest = {
  payload: Record<string, unknown>;
  force_demo?: boolean;
};

export type PolariumWsDebugResponse = {
  accepted: boolean;
  message: string;
  account: PolariumAccountState;
};

export type PolariumOAuthConfig = {
  configured: boolean;
  client_id_configured: boolean;
  authorize_url_configured: boolean;
  token_url_configured: boolean;
  redirect_uri: string;
  token_url: string;
  authorize_url?: string | null;
  message: string;
};

export type PolariumPkceStartResponse = {
  ready: boolean;
  status: 'READY' | 'MISSING_CONFIG' | 'TOKEN_STORED' | 'EXCHANGE_FAILED' | 'CALLBACK_RECEIVED';
  state: string;
  code_verifier_preview: string;
  code_challenge: string;
  code_challenge_method: string;
  redirect_uri: string;
  authorize_url?: string | null;
  message: string;
  warnings: string[];
};

export type PolariumOAuthSessionState = {
  has_token: boolean;
  status: 'READY' | 'MISSING_CONFIG' | 'TOKEN_STORED' | 'EXCHANGE_FAILED' | 'CALLBACK_RECEIVED';
  token_type?: string | null;
  expires_at?: string | null;
  scope?: string | null;
  last_error?: string | null;
  message: string;
  safety_rules: string[];
};


export type PolariumDirectConfig = {
  configured: boolean;
  login_url_configured: boolean;
  email_configured: boolean;
  password_configured: boolean;
  websocket_url_configured: boolean;
  login_url?: string | null;
  websocket_url?: string | null;
  message: string;
  safety_rules: string[];
};

export type PolariumDirectProbeRequest = {
  dry_run: boolean;
  force_demo?: boolean;
};

export type PolariumDirectProbeResponse = {
  success: boolean;
  status: 'READY' | 'MISSING_CONFIG' | 'DRY_RUN' | 'LOGIN_FAILED' | 'SESSION_STORED' | 'NOT_AUTHORIZED';
  dry_run: boolean;
  token_stored: boolean;
  token_type?: string | null;
  response_keys: string[];
  http_status?: number | null;
  message: string;
  warnings: string[];
};

export type PolariumDirectSessionState = {
  has_session: boolean;
  status: 'READY' | 'MISSING_CONFIG' | 'DRY_RUN' | 'LOGIN_FAILED' | 'SESSION_STORED' | 'NOT_AUTHORIZED';
  token_type?: string | null;
  response_keys: string[];
  message: string;
  safety_rules: string[];
};
