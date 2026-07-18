export type VisionDecision = 'CALL' | 'PUT' | 'WAIT' | 'DO_NOT_TRADE';
export type VisionTrend = 'BULLISH' | 'BEARISH' | 'SIDEWAYS' | 'UNCLEAR';
export type VisionMarketState = 'TRENDING' | 'RANGING' | 'BREAKOUT' | 'REVERSAL_ATTEMPT' | 'EXHAUSTION' | 'CHOPPY' | 'UNCLEAR';
export type VisionRiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME';
export type VisionImageQuality = 'GOOD' | 'ACCEPTABLE' | 'POOR' | 'UNUSABLE';
export type VisionStrategyMode = 'COMPLETE' | 'PRICE_ACTION' | 'SUPPORT_RESISTANCE' | 'TREND';
export type VisionUiState = 'IDLE' | 'IMAGE_READY' | 'VALIDATING' | 'ANALYZING' | 'SUCCESS' | 'ERROR' | 'COOLDOWN';

export interface VisionStatus {
  enabled: boolean;
  mode: 'VISION_FIRST';
  provider: string;
  analysis_available: boolean;
  allowed_formats: string[];
  max_image_mb: number;
  require_auth: boolean;
}

export interface VisionAnalysisRequestPayload {
  image: File;
  asset?: string;
  timeframe: 'M1' | 'M5' | 'M15';
  expiration: '1 minuto' | '5 minutos' | '15 minutos';
  strategy_mode: VisionStrategyMode;
  user_notes?: string;
  requestId: string;
  signal?: AbortSignal;
}

export interface VisionAnalysisResult {
  analysis_id: string;
  decision: VisionDecision;
  asset_detected: string | null;
  timeframe_detected: string | null;
  expiration_considered: string;
  trend: VisionTrend;
  market_state: VisionMarketState;
  risk: VisionRiskLevel;
  confidence: number;
  image_quality: VisionImageQuality;
  chart_visible: boolean;
  candles_visible: boolean;
  summary: string;
  market_reading: string;
  entry_condition: string;
  invalidation_condition: string;
  support_zones: string[];
  resistance_zones: string[];
  warnings: string[];
  limitations: string[];
  created_at: string;
  model: string;
  processing_time_ms: number;
}

export interface VisionHistoryItem {
  analysis_id: string;
  image_hash: string;
  asset_informed: string | null;
  asset_detected: string | null;
  timeframe_informed: string;
  timeframe_detected: string | null;
  expiration: string;
  decision: VisionDecision;
  trend: VisionTrend;
  market_state: VisionMarketState;
  risk: VisionRiskLevel;
  confidence: number;
  summary: string;
  warnings: string[];
  limitations: string[];
  model: string;
  processing_time_ms: number;
  created_at: string;
}
