import { useEffect, useState } from 'react';
import type { RealChartCandle } from '../components/chart/RealCandleChart';
import { reconcileRealCandleSeries } from '../components/chart/RealCandleChart/sync';

type RealCandleSeries = {
  activeId: number | null;
  rawSize: number | null;
  candles: RealChartCandle[];
  source: string;
  assetLabel: string;
  timeframeLabel: string;
  bridgeOnline: boolean;
  pipelineOnline: boolean;
  storeOnline: boolean;
  chartOnline: boolean;
  pipelineSuccessCount: number;
  activeIdsSeen: number[];
  rawSizesSeen: number[];
  lastEventName: string | null;
  lastEventAt: string | null;
  isLoading: boolean;
  error: string | null;
};

type MarketChartResponse = {
  active_id: number;
  raw_size: number;
  count: number;
  candles: RealChartCandle[];
};

type BrowserBridgeStatus = {
  connected: boolean;
  bridge_active: boolean;
  last_event_name: string | null;
  last_event_at: string | null;
  pipeline_success_count: number;
  active_ids_seen: number[];
  raw_sizes_seen: number[];
  data_classification: string;
  last_trace?: {
    chart_api_probe?: {
      params?: {
        active_id?: number;
        raw_size?: number;
      };
      count?: number;
    } | null;
    pipeline_result?: {
      success?: boolean;
    } | null;
    candle_store?: {
      saved_candles?: Array<{ series_count_after?: number }>;
    } | null;
  };
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const DEFAULT_LIMIT = 200;
const SYNC_INTERVAL_MS = 1500;

export function useRealCandles(): RealCandleSeries {
  const [activeId, setActiveId] = useState<number | null>(null);
  const [rawSize, setRawSize] = useState<number | null>(null);
  const [candles, setCandles] = useState<RealChartCandle[]>([]);
  const [source, setSource] = useState('DISCONNECTED');
  const [bridgeStatus, setBridgeStatus] = useState<BrowserBridgeStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let isMounted = true;
    let isFirstLoad = true;
    let isRequestInFlight = false;

    async function loadCandles() {
      if (isRequestInFlight) return;
      isRequestInFlight = true;
      if (isFirstLoad) {
        setIsLoading(true);
      }
      try {
        const statusResponse = await fetch(`${API_BASE_URL}/polarium/browser-bridge/status`, {
          signal: controller.signal
        });
        if (!statusResponse.ok) {
          throw new Error(`Browser Bridge status returned ${statusResponse.status}`);
        }
        const statusPayload = (await statusResponse.json()) as BrowserBridgeStatus;
        const nextContext = resolveActiveSeries(statusPayload);
        if (!isMounted) return;
        setBridgeStatus(statusPayload);
        setSource(statusPayload.data_classification || (statusPayload.bridge_active ? 'POLARIUM AUTHORIZED BROWSER LIVE' : 'DISCONNECTED'));

        if (!nextContext) {
          setActiveId(null);
          setRawSize(null);
          setCandles([]);
          setError(null);
          return;
        }

        const params = new URLSearchParams({
          active_id: String(nextContext.activeId),
          raw_size: String(nextContext.rawSize),
          limit: String(DEFAULT_LIMIT)
        });
        const response = await fetch(`${API_BASE_URL}/market/chart?${params.toString()}`, {
          signal: controller.signal
        });
        if (!response.ok) {
          throw new Error(`Market chart API returned ${response.status}`);
        }
        const payload = (await response.json()) as MarketChartResponse;
        if (!isMounted) return;
        setActiveId(payload.active_id);
        setRawSize(payload.raw_size);
        setError(null);
        setCandles((previousCandles) => {
          if (activeId !== payload.active_id || rawSize !== payload.raw_size) {
            return payload.candles;
          }
          const { candles: updatedCandles } = reconcileRealCandleSeries(previousCandles, payload.candles);
          return Object.is(updatedCandles, previousCandles) ? previousCandles : updatedCandles;
        });
      } catch (requestError) {
        if (controller.signal.aborted) return;
        if (!isMounted) return;
        setError(requestError instanceof Error ? requestError.message : 'Falha ao carregar candles');
      } finally {
        if (!controller.signal.aborted && isMounted && isFirstLoad) {
          setIsLoading(false);
          isFirstLoad = false;
        }
        isRequestInFlight = false;
      }
    }

    void loadCandles();
    const syncTimer = window.setInterval(() => {
      void loadCandles();
    }, SYNC_INTERVAL_MS);

    return () => {
      isMounted = false;
      window.clearInterval(syncTimer);
      controller.abort();
    };
  }, [activeId, rawSize]);

  const timeframeLabel = rawSize ? rawSizeToTimeframe(rawSize) : 'Não disponível';
  const activeIdsSeen = bridgeStatus?.active_ids_seen ?? [];
  const rawSizesSeen = bridgeStatus?.raw_sizes_seen ?? [];
  const pipelineOnline = Boolean(bridgeStatus?.last_trace?.pipeline_result?.success || (bridgeStatus?.pipeline_success_count ?? 0) > 0);
  const storeOnline = Boolean(candles.length || (bridgeStatus?.last_trace?.candle_store?.saved_candles?.[0]?.series_count_after ?? 0) > 0);
  const chartOnline = Boolean(activeId && rawSize && candles.length);

  return {
    activeId,
    rawSize,
    candles,
    source,
    assetLabel: activeId ? `Active ID ${activeId}` : 'Não disponível',
    timeframeLabel,
    bridgeOnline: Boolean(bridgeStatus?.bridge_active && bridgeStatus.connected),
    pipelineOnline,
    storeOnline,
    chartOnline,
    pipelineSuccessCount: bridgeStatus?.pipeline_success_count ?? 0,
    activeIdsSeen,
    rawSizesSeen,
    lastEventName: bridgeStatus?.last_event_name ?? null,
    lastEventAt: bridgeStatus?.last_event_at ?? null,
    isLoading,
    error
  };
}

function resolveActiveSeries(status: BrowserBridgeStatus): { activeId: number; rawSize: number } | null {
  const tracedActiveId = status.last_trace?.chart_api_probe?.params?.active_id;
  const tracedRawSize = status.last_trace?.chart_api_probe?.params?.raw_size;
  if (typeof tracedActiveId === 'number' && typeof tracedRawSize === 'number') {
    return { activeId: tracedActiveId, rawSize: tracedRawSize };
  }

  const activeId = status.active_ids_seen?.[status.active_ids_seen.length - 1];
  const rawSize = status.raw_sizes_seen?.[status.raw_sizes_seen.length - 1];
  if (typeof activeId === 'number' && typeof rawSize === 'number') {
    return { activeId, rawSize };
  }
  return null;
}

function rawSizeToTimeframe(rawSize: number): string {
  if (rawSize === 60) return 'M1';
  if (rawSize === 300) return 'M5';
  if (rawSize === 900) return 'M15';
  return `${rawSize}s`;
}
