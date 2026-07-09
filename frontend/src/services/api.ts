import axios from 'axios';
import type {
  AssetScannerResponse,
  ExecutionStatus,
  HealthResponse,
  ProviderStatus,
  RiskCheck,
  SignalAnalysis
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000
});

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get('/health');
  return data;
}

export async function getTopAssets(): Promise<AssetScannerResponse> {
  const { data } = await api.get('/scanner/top-assets', {
    params: { timeframe: 'M1', candle_limit: 60, top: 12, bankroll: 200, payout: 80 }
  });
  return data;
}

export async function getSignalAnalysis(): Promise<SignalAnalysis> {
  const { data } = await api.get('/signal/analyze', {
    params: { symbol: 'EURUSD-OTC', timeframe: 'M1', limit: 60 }
  });
  return data;
}

export async function getRiskCheck(): Promise<RiskCheck> {
  const { data } = await api.get('/risk/check', {
    params: { bankroll: 200, entry_value: 10, daily_wins: 0, daily_losses: 0, gale_used: 1, payout: 80 }
  });
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
