export type ExecutionStatus = 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED';
export type ProviderStatus = 'success' | 'placeholder' | 'not_configured' | 'error';
export type PipelineStepStatus = 'WAITING' | 'RUNNING' | 'SUCCESS' | 'ERROR';

export interface CoreDemoExecutionRequest {
  module: string;
  identity: string;
  provider: string;
  language: string;
  message: string;
  market?: 'OTC' | 'Forex' | 'Crypto';
  symbol?: string;
  timeframe?: 'M1' | 'M5' | 'M15' | 'H1';
  strategy?: 'Trend' | 'Price Action' | 'Support Resistance' | 'SMC' | 'ICT';
  metadata: Record<string, unknown>;
}

export interface ProviderUsage {
  input_units: number;
  output_units: number;
  total_units: number;
}

export interface ProviderResponse {
  provider: string;
  provider_version: string;
  request_id: string;
  response: string;
  usage: ProviderUsage;
  latency: number;
  metadata: Record<string, unknown>;
  status: ProviderStatus;
  fingerprint: string;
  timestamp: string;
}

export interface ExecutionMetadata {
  execution_id: string;
  request_id: string;
  started_at: string;
  finished_at: string | null;
  duration: number | null;
  provider: string | null;
  provider_version: string | null;
  identity: string | null;
  module: string;
  pipeline_version: string;
  fingerprint: string;
  status: ExecutionStatus;
}

export interface ExecutionResponse {
  request_id: string;
  identity: string;
  provider: string;
  provider_response: ProviderResponse;
  latency: number;
  status: ExecutionStatus;
  metadata: ExecutionMetadata;
  fingerprint: string;
  timestamp: string;
}

export interface TradingResponse {
  status: ExecutionStatus;
  trend: string;
  support: string;
  resistance: string;
  decision: 'WAIT' | 'OBSERVE' | 'DO_NOT_TRADE';
  confidence: number;
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
  analysis: string;
  execution: {
    status: ExecutionStatus;
    module: string;
    identity: string;
    provider: string;
    execution: ExecutionResponse;
    response: string;
    latency: number;
    metadata: Record<string, unknown>;
    timestamp: string;
  };
  metadata: Record<string, unknown>;
  timestamp: string;
}

export type CoreDemoResponse = ExecutionResponse | TradingResponse;

export interface PipelineStep {
  id: 'validation' | 'identity' | 'prompt' | 'provider' | 'response';
  label: string;
  status: PipelineStepStatus;
}

export type LatencyClassification = 'Excelente' | 'Boa' | 'Moderada' | 'Lenta';

export interface ExecutionHistoryItem {
  id: string;
  time: string;
  market: string;
  symbol: string;
  strategy: string;
  decision: string;
  confidence: number | null;
  status: ExecutionStatus;
  latency: number;
}

export interface ExecutionStats {
  count: number;
  averageLatency: number | null;
  lastExecutionAt: string | null;
  latencyClassification: LatencyClassification | 'Aguardando';
}
