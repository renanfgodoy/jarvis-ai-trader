import axios from 'axios';
import type {
  AccountCurrency,
  AssetScannerResponse,
  AutoTradeGateRequest,
  AutoTradeGateResponse,
  ExecutionStatus,
  HealthResponse,
  LiveWorkspaceResponse,
  LiveTick,
  MarketCandlesResponse,
  MarketIntelligence,
  MarketIntelligenceScannerResponse,
  ProviderStatus,
  RiskCheck,
  SignalAnalysis,
  Timeframe
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws').replace('/api/v1', '');

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000
});

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get('/health');
  return data;
}

export async function getTopAssets(timeframe: Timeframe = 'M1'): Promise<AssetScannerResponse> {
  const { data } = await api.get('/scanner/top-assets', {
    params: { timeframe, candle_limit: 60, top: 12, bankroll: 200, payout: 80 }
  });
  return data;
}


export async function getMarketIntelligence(symbol = 'EURUSD-OTC', timeframe: Timeframe = 'M1'): Promise<MarketIntelligence> {
  const { data } = await api.get('/intelligence/analyze', {
    params: { symbol, timeframe, payout: 84, minimum_score: 80, minimum_payout: 75, candle_limit: 80 }
  });
  return data;
}

export async function getMarketIntelligenceTop(timeframe: Timeframe = 'M1'): Promise<MarketIntelligenceScannerResponse> {
  const { data } = await api.get('/intelligence/scanner/top', {
    params: { timeframe, top: 12, payout: 84, minimum_score: 80, minimum_payout: 75, candle_limit: 80 }
  });
  return data;
}

export async function getSignalAnalysis(symbol = 'EURUSD-OTC', timeframe: Timeframe = 'M1'): Promise<SignalAnalysis> {
  const { data } = await api.get('/signal/analyze', {
    params: { symbol, timeframe, limit: 60 }
  });
  return data;
}

export async function getMarketCandles(symbol = 'EURUSD-OTC', timeframe: Timeframe = 'M1'): Promise<MarketCandlesResponse> {
  const { data } = await api.get('/market/candles', {
    params: { symbol, timeframe, limit: 80 }
  });
  return data;
}

export async function getLiveWorkspace(symbol = 'EURUSD-OTC', timeframe: Timeframe = 'M1'): Promise<LiveWorkspaceResponse> {
  const { data } = await api.get('/live/workspace', {
    params: { symbol, timeframe, limit: 120 }
  });
  return data;
}

export async function getRiskCheck(currency: AccountCurrency = 'BRL', entryValue = 10): Promise<RiskCheck> {
  const { data } = await api.get('/risk/check', {
    params: {
      bankroll: 200,
      entry_value: entryValue,
      daily_wins: 0,
      daily_losses: 0,
      gale_used: 1,
      payout: 80,
      account_currency: currency
    }
  });
  return data;
}

export async function checkAutoTradeGate(payload: AutoTradeGateRequest): Promise<AutoTradeGateResponse> {
  const { data } = await api.post('/execution/autotrade/gate', payload);
  return data;
}

export async function getExecutionStatus(): Promise<ExecutionStatus> {
  const { data } = await api.get('/execution/status');
  return data;
}

export async function getCurrentProvider(): Promise<ProviderStatus> {
  const { data } = await api.get('/providers/current');
  return data;
}

export async function getLiveTick(symbol = 'EURUSD-OTC', timeframe: Timeframe = 'M1'): Promise<LiveTick> {
  const { data } = await api.get('/live/tick', {
    params: { symbol, timeframe, limit: 120 }
  });
  return data;
}

export function getLiveWorkspaceWebSocketUrl(symbol = 'EURUSD-OTC', timeframe: Timeframe = 'M1'): string {
  const safeSymbol = encodeURIComponent(symbol);
  return `${WS_BASE_URL}/api/v1/live/workspace/ws?symbol=${safeSymbol}&timeframe=${timeframe}`;
}
