import { useMemo } from 'react';
import type { RealChartCandle } from '../components/chart/RealCandleChart';

type RealCandleSeries = {
  activeId: number;
  rawSize: number;
  candles: RealChartCandle[];
  source: string;
};

const candleStoreSnapshot: RealChartCandle[] = [
  { time: 1778475660, open: 1.201705, high: 1.201825, low: 1.201405, close: 1.201425 },
  { time: 1783721940, open: 1.162275, high: 1.162395, low: 1.162145, close: 1.162145 },
  { time: 1783722000, open: 1.162965, high: 1.163335, low: 1.162715, close: 1.162765 }
];

export function useRealCandles(): RealCandleSeries {
  return useMemo(() => ({
    activeId: 76,
    rawSize: 60,
    candles: candleStoreSnapshot,
    source: 'Candle Store snapshot sanitizado'
  }), []);
}
