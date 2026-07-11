import { useEffect, useState } from 'react';
import type { RealChartCandle } from '../components/chart/RealCandleChart';

type RealCandleSeries = {
  activeId: number;
  rawSize: number;
  candles: RealChartCandle[];
  source: string;
  isLoading: boolean;
  error: string | null;
};

type MarketChartResponse = {
  active_id: number;
  raw_size: number;
  count: number;
  candles: RealChartCandle[];
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const DEFAULT_ACTIVE_ID = 76;
const DEFAULT_RAW_SIZE = 60;
const DEFAULT_LIMIT = 200;

export function useRealCandles(): RealCandleSeries {
  const [candles, setCandles] = useState<RealChartCandle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({
      active_id: String(DEFAULT_ACTIVE_ID),
      raw_size: String(DEFAULT_RAW_SIZE),
      limit: String(DEFAULT_LIMIT)
    });

    async function loadCandles() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/market/chart?${params.toString()}`, {
          signal: controller.signal
        });
        if (!response.ok) {
          throw new Error(`Market chart API returned ${response.status}`);
        }
        const payload = (await response.json()) as MarketChartResponse;
        setCandles(payload.candles);
      } catch (requestError) {
        if (controller.signal.aborted) return;
        setCandles([]);
        setError(requestError instanceof Error ? requestError.message : 'Falha ao carregar candles');
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    }

    void loadCandles();
    return () => controller.abort();
  }, []);

  return {
    activeId: DEFAULT_ACTIVE_ID,
    rawSize: DEFAULT_RAW_SIZE,
    candles,
    source: 'Candle Store API read-only',
    isLoading,
    error
  };
}
