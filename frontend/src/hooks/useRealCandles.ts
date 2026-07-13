import { useEffect, useMemo, useRef, useState } from 'react';
import type { RealChartCandle } from '../components/chart/RealCandleChart';
import { reconcileRealCandleSeries } from '../components/chart/RealCandleChart/sync';

export type RealCandleSeriesSummary = {
  provider: string;
  activeId: number | null;
  symbol: string | null;
  rawSize: number;
  count: number;
  latestTime: number | null;
};

type UseRealCandlesOptions = {
  activeId?: number | null;
  rawSize?: number | null;
  followPolarium?: boolean;
  enabled?: boolean;
};

export type RealCandleSeries = {
  activeId: number | null;
  rawSize: number | null;
  autoActiveId: number | null;
  autoRawSize: number | null;
  candles: RealChartCandle[];
  availableSeries: RealCandleSeriesSummary[];
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
  symbol: string | null;
  raw_size: number;
  count: number;
  candles: RealChartCandle[];
};

type MarketChartSeriesResponse = {
  series: Array<{
    active_id: number | null;
    provider?: string;
    symbol: string | null;
    raw_size: number;
    count: number;
    latest_time: number | null;
  }>;
};

type BrowserBridgeStatus = {
  connected: boolean;
  bridge_active: boolean;
  last_event_name: string | null;
  last_event_at: string | null;
  pipeline_success_count: number;
  active_ids_seen: number[];
  raw_sizes_seen: number[];
  current_symbol?: string | null;
  symbol_found?: boolean;
  symbol_source?: string | null;
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

type SeriesContext = {
  activeId: number;
  rawSize: number;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const DEFAULT_LIMIT = 200;
const SYNC_INTERVAL_MS = 1500;

export function useRealCandles(options: UseRealCandlesOptions = {}): RealCandleSeries {
  const requestedActiveId = options.activeId ?? null;
  const requestedRawSize = options.rawSize ?? null;
  const followPolarium = options.followPolarium ?? true;
  const enabled = options.enabled ?? true;
  const [activeId, setActiveId] = useState<number | null>(null);
  const [rawSize, setRawSize] = useState<number | null>(null);
  const [autoActiveId, setAutoActiveId] = useState<number | null>(null);
  const [autoRawSize, setAutoRawSize] = useState<number | null>(null);
  const [candles, setCandles] = useState<RealChartCandle[]>([]);
  const [availableSeries, setAvailableSeries] = useState<RealCandleSeriesSummary[]>([]);
  const [source, setSource] = useState('DISCONNECTED');
  const [bridgeStatus, setBridgeStatus] = useState<BrowserBridgeStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const displayedContextRef = useRef<SeriesContext | null>(null);
  const candlesLengthRef = useRef(0);
  const lastValidAutoContextRef = useRef<SeriesContext | null>(null);
  const requestSequenceRef = useRef(0);
  const lastAppliedRequestRef = useRef(0);

  useEffect(() => {
    displayedContextRef.current = activeId !== null && rawSize !== null ? { activeId, rawSize } : null;
    candlesLengthRef.current = candles.length;
  }, [activeId, candles.length, rawSize]);

  useEffect(() => {
    if (!enabled) {
      setIsLoading(false);
      setError(null);
      return;
    }
    const controller = new AbortController();
    let isMounted = true;
    let isFirstLoad = true;
    let isRequestInFlight = false;

    async function loadCandles() {
      if (isRequestInFlight) return;
      isRequestInFlight = true;
      const requestSequence = requestSequenceRef.current + 1;
      requestSequenceRef.current = requestSequence;
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
        const seriesResponse = await fetch(`${API_BASE_URL}/market/chart/series`, {
          signal: controller.signal
        });
        if (!seriesResponse.ok) {
          throw new Error(`Market chart series API returned ${seriesResponse.status}`);
        }
        const seriesPayload = (await seriesResponse.json()) as MarketChartSeriesResponse;
        const nextAvailableSeries = seriesPayload.series.map((item) => ({
          activeId: item.active_id,
          provider: item.provider ?? 'POLARIUM',
          symbol: item.symbol ?? null,
          rawSize: item.raw_size,
          count: item.count,
          latestTime: item.latest_time
        }));
        const autoContext = resolveActiveSeries(statusPayload, nextAvailableSeries);
        if (autoContext) {
          lastValidAutoContextRef.current = autoContext;
        }
        const manualContext =
          typeof requestedActiveId === 'number' && typeof requestedRawSize === 'number'
            ? { activeId: requestedActiveId, rawSize: requestedRawSize }
            : null;
        const displayedContext = displayedContextRef.current;
        const fallbackContext = firstAvailableSeries(nextAvailableSeries);
        const validManualContext = manualContext && (hasAvailableSeries(nextAvailableSeries, manualContext) || sameSeries(manualContext, displayedContext))
          ? manualContext
          : null;
        const nextContext = followPolarium
          ? autoContext ?? lastValidAutoContextRef.current ?? displayedContext ?? fallbackContext
          : validManualContext ?? displayedContext ?? fallbackContext;
        const shouldPreserveDisplayedCandles = !nextContext && displayedContext && candlesLengthRef.current > 0;
        const nextDisplayedContext = nextContext ?? (shouldPreserveDisplayedCandles ? displayedContext : null);
        if (!isMounted) return;
        setBridgeStatus(statusPayload);
        setAvailableSeries(nextAvailableSeries);
        setAutoActiveId(autoContext?.activeId ?? null);
        setAutoRawSize(autoContext?.rawSize ?? null);
        setSource(statusPayload.data_classification || (statusPayload.bridge_active ? 'POLARIUM AUTHORIZED BROWSER LIVE' : 'DISCONNECTED'));

        if (!nextDisplayedContext) {
          if (!candles.length) {
            setActiveId(null);
            setRawSize(null);
            setCandles([]);
          }
          setError(null);
          return;
        }

        const params = new URLSearchParams({
          active_id: String(nextDisplayedContext.activeId),
          raw_size: String(nextDisplayedContext.rawSize),
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
        if (requestSequence <= lastAppliedRequestRef.current) {
          return;
        }
        const currentDisplayedContext = displayedContextRef.current;
        const payloadContext = { activeId: payload.active_id, rawSize: payload.raw_size };
        if (!sameSeries(payloadContext, nextDisplayedContext)) {
          return;
        }
        const isSwitchingSeries = !sameSeries(currentDisplayedContext, payloadContext);
        const shouldKeepPreviousCandles = payload.candles.length === 0 && candlesLengthRef.current > 0;
        if (shouldKeepPreviousCandles || (isSwitchingSeries && payload.candles.length === 0)) {
          setError(null);
          return;
        }

        lastAppliedRequestRef.current = requestSequence;
        setActiveId(payload.active_id);
        setRawSize(payload.raw_size);
        displayedContextRef.current = payloadContext;
        if (followPolarium && payload.candles.length > 0) {
          lastValidAutoContextRef.current = payloadContext;
        }
        setError(null);
        setCandles((previousCandles) => {
          if (!sameSeries(currentDisplayedContext, payloadContext)) {
            return payload.candles;
          }
          if (!payload.candles.length && previousCandles.length) {
            return previousCandles;
          }
          const { candles: updatedCandles } = reconcileRealCandleSeries(previousCandles, payload.candles, DEFAULT_LIMIT);
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
  }, [enabled, followPolarium, requestedActiveId, requestedRawSize]);

  const activeSymbol = resolveSeriesSymbol(activeId, rawSize, availableSeries) ?? bridgeStatus?.current_symbol ?? null;
  const timeframeLabel = rawSize ? rawSizeToTimeframe(rawSize) : 'Não disponível';
  const activeIdsSeen = bridgeStatus?.active_ids_seen ?? [];
  const rawSizesSeen = bridgeStatus?.raw_sizes_seen ?? [];
  const pipelineOnline = Boolean(bridgeStatus?.last_trace?.pipeline_result?.success || (bridgeStatus?.pipeline_success_count ?? 0) > 0);
  const storeOnline = Boolean(candles.length || (bridgeStatus?.last_trace?.candle_store?.saved_candles?.[0]?.series_count_after ?? 0) > 0);
  const chartOnline = Boolean(activeId && rawSize && candles.length);

  return {
    activeId,
    rawSize,
    autoActiveId,
    autoRawSize,
    candles,
    availableSeries,
    source,
    assetLabel: activeSymbol ?? 'Não disponível',
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

export function useAvailableTimeframes(series: RealCandleSeriesSummary[], activeId: number | null): RealCandleSeriesSummary[] {
  return useMemo(() => {
    if (activeId === null) return [];
    return series.filter((item) => item.activeId === activeId).sort((left, right) => left.rawSize - right.rawSize);
  }, [activeId, series]);
}

export function resolveActiveSeries(status: BrowserBridgeStatus, availableSeries: RealCandleSeriesSummary[]): SeriesContext | null {
  const tracedActiveId = status.last_trace?.chart_api_probe?.params?.active_id;
  const tracedRawSize = status.last_trace?.chart_api_probe?.params?.raw_size;
  const tracedCount = status.last_trace?.chart_api_probe?.count;
  if (
    typeof tracedActiveId === 'number' &&
    typeof tracedRawSize === 'number' &&
    typeof tracedCount === 'number' &&
    tracedCount > 0
  ) {
    const tracedContext = { activeId: tracedActiveId, rawSize: tracedRawSize };
    return hasAvailableSeries(availableSeries, tracedContext) ? tracedContext : null;
  }

  return null;
}

export function hasAvailableSeries(series: RealCandleSeriesSummary[], context: SeriesContext): boolean {
  return series.some((item) => item.provider === 'POLARIUM' && item.activeId === context.activeId && item.rawSize === context.rawSize && item.count > 0);
}

function sameSeries(left: SeriesContext | null, right: SeriesContext | null): boolean {
  return Boolean(left && right && left.activeId === right.activeId && left.rawSize === right.rawSize);
}

function firstAvailableSeries(series: RealCandleSeriesSummary[]): SeriesContext | null {
  const first = series.find((item) => item.provider === 'POLARIUM' && item.activeId !== null && item.count > 0);
  return first
    ? { activeId: first.activeId as number, rawSize: first.rawSize }
    : null;
}

function resolveSeriesSymbol(activeId: number | null, rawSize: number | null, series: RealCandleSeriesSummary[]): string | null {
  if (activeId === null || rawSize === null) return null;
  return series.find((item) => item.activeId === activeId && item.rawSize === rawSize)?.symbol ?? null;
}

function rawSizeToTimeframe(rawSize: number): string {
  if (rawSize === 60) return 'M1';
  if (rawSize === 300) return 'M5';
  if (rawSize === 900) return 'M15';
  return `${rawSize}s`;
}

export function formatRawSize(rawSize: number): string {
  return rawSizeToTimeframe(rawSize);
}
