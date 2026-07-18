import { useEffect, useMemo, useRef, useState } from 'react';
import type { RealChartCandle } from '../components/chart/RealCandleChart';
import { reconcileRealCandleSeries } from '../components/chart/RealCandleChart/sync';
import {
  disconnectedPolariumSessionContext,
  normalizePolariumSessionContext,
  publishPolariumSessionUpdate,
  type PolariumSessionContext,
  type RawPolariumSessionContext
} from '../contexts/PolariumSessionContext';
import { recordChartBindingTrace, summarizeChartBindingCandles } from '../debug/chartBindingTrace';
import { measureFridayLatencyAudit, recordFridayLatencyAudit } from '../utils/latencyAudit';

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
  provider: string;
  activeKey: string | null;
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
  sessionContext: PolariumSessionContext;
  readiness: string | null;
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

type ProviderChartResponse = {
  provider: string;
  active_id: number | null;
  symbol: string | null;
  raw_size: number;
  period?: number;
  timeframe?: string;
  count: number;
  readiness?: {
    state?: string;
    history_count?: number;
    required_history_count?: number;
    analysis_blocked?: boolean;
    reason?: string | null;
  };
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

type MarketProvidersResponse = {
  providers: Array<{
    provider: string;
    runtime?: {
      connected?: boolean;
      market_socket_ready?: boolean;
      processed?: number;
      received?: number;
      latest_active_id?: number | null;
      latest_symbol?: string | null;
      latest_raw_sizes?: number[];
      session_context?: RawPolariumSessionContext | null;
    };
    live_source?: {
      connected?: boolean;
      received_events?: number;
    };
  }>;
};

type ProviderV2StatusResponse = {
  enabled: boolean;
  current_provider: string;
  provider_running: boolean;
  context: {
    provider?: string;
    asset?: string | null;
    symbol?: string | null;
    timeframe?: string | null;
    period?: number | null;
    history_count?: number;
  } | null;
  readiness: {
    state?: string;
    history_count?: number;
    required_history_count?: number;
    analysis_blocked?: boolean;
    reason?: string | null;
  } | null;
  outbound_messages_originated_by_friday?: number;
};

type SeriesContext = {
  activeId: number;
  rawSize: number;
};

type PolariumRuntimeStatus = {
  connected: boolean;
  market_socket_ready: boolean;
  processed: number;
  received: number;
  latestActiveId: number | null;
  latestSymbol: string | null;
  latestRawSizes: number[];
  sessionContext: PolariumSessionContext;
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
  const [providerName, setProviderName] = useState('POLARIUM');
  const [activeKey, setActiveKey] = useState<string | null>(null);
  const [readiness, setReadiness] = useState<string | null>(null);
  const [polariumStatus, setPolariumStatus] = useState<PolariumRuntimeStatus | null>(null);
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
        const providerV2Status = await loadProviderV2Status(controller.signal);
        if (providerV2Status?.enabled && providerV2Status.current_provider === 'POCKET') {
          const contextSymbol = providerV2Status.context?.symbol ?? providerV2Status.context?.asset ?? null;
          const contextPeriod = typeof providerV2Status.context?.period === 'number' ? providerV2Status.context.period : null;
          const seriesResponse = await fetch(`${API_BASE_URL}/market/chart/series`, {
            signal: controller.signal
          });
          if (!seriesResponse.ok) {
            throw new Error(`Market chart series API returned ${seriesResponse.status}`);
          }
          const seriesPayload = (await seriesResponse.json()) as MarketChartSeriesResponse;
          const nextAvailableSeries = seriesPayload.series.map((item) => ({
            activeId: item.active_id,
            provider: item.provider ?? 'POCKET',
            symbol: item.symbol ?? null,
            rawSize: item.raw_size,
            count: item.count,
            latestTime: item.latest_time
          }));
          const selectedSeries =
            nextAvailableSeries.find((item) => item.provider === 'POCKET' && item.symbol === contextSymbol && item.rawSize === contextPeriod) ??
            nextAvailableSeries.find((item) => item.provider === 'POCKET' && item.count > 0) ??
            nextAvailableSeries.find((item) => item.provider === 'POCKET') ??
            null;
          const selectedSymbol = selectedSeries?.symbol ?? contextSymbol;
          const selectedPeriod = selectedSeries?.rawSize ?? contextPeriod;
          const nextActiveKey = selectedSymbol && selectedPeriod ? `POCKET:${selectedSymbol}:${selectedPeriod}` : null;
          if (!selectedSymbol || !selectedPeriod) {
            if (!candlesLengthRef.current) {
              setCandles([]);
            }
            setProviderName('POCKET');
            setActiveKey(nextActiveKey);
            setActiveId(null);
            setRawSize(selectedPeriod);
            setAutoActiveId(null);
            setAutoRawSize(selectedPeriod);
            setAvailableSeries(nextAvailableSeries);
            setSource('POCKET READ ONLY');
            setReadiness(providerV2Status.readiness?.state ?? null);
            setError(null);
            return;
          }
          const params = new URLSearchParams({
            provider: 'POCKET',
            symbol: selectedSymbol,
            period: String(selectedPeriod),
            limit: String(DEFAULT_LIMIT)
          });
          const chartEndpoint = `${API_BASE_URL}/market/chart?${params.toString()}`;
          recordChartBindingTrace('CHART_FETCH_START', {
            provider: 'POCKET',
            symbol: selectedSymbol,
            raw_size: selectedPeriod,
            endpoint: chartEndpoint,
            request_sequence: requestSequence,
            selected_source: 'PROVIDER_V2'
          });
          const response = await fetch(chartEndpoint, { signal: controller.signal });
          if (!response.ok) {
            throw new Error(`Market chart API returned ${response.status}`);
          }
          const payload = (await response.json()) as ProviderChartResponse;
          if (!isMounted) return;
          const responseActiveKey = payload.symbol ? `${payload.provider}:${payload.symbol}:${payload.period ?? payload.raw_size}` : nextActiveKey;
          if (responseActiveKey !== nextActiveKey) {
            recordChartBindingTrace('STALE_RESPONSE_IGNORED', {
              provider: payload.provider,
              symbol: payload.symbol,
              raw_size: payload.raw_size,
              endpoint: chartEndpoint,
              response_count: payload.candles.length,
              request_sequence: requestSequence,
              response_ignored: true,
              reason: 'PROVIDER_V2_ACTIVE_KEY_MISMATCH'
            });
            return;
          }
          if (requestSequence <= lastAppliedRequestRef.current) {
            recordChartBindingTrace('STALE_RESPONSE_IGNORED', {
              provider: payload.provider,
              symbol: payload.symbol,
              raw_size: payload.raw_size,
              endpoint: chartEndpoint,
              response_count: payload.candles.length,
              request_sequence: requestSequence,
              response_ignored: true,
              reason: 'OLDER_THAN_LAST_APPLIED'
            });
            return;
          }
          const shouldKeepPreviousPocketCandles = payload.candles.length === 0 && activeKey === nextActiveKey && candlesLengthRef.current > 0;
          if (shouldKeepPreviousPocketCandles) {
            setError(null);
            return;
          }
          lastAppliedRequestRef.current = requestSequence;
          setProviderName('POCKET');
          setActiveKey(nextActiveKey);
          setActiveId(null);
          setRawSize(payload.period ?? payload.raw_size);
          setAutoActiveId(null);
          setAutoRawSize(payload.period ?? payload.raw_size);
          setAvailableSeries(nextAvailableSeries);
          setSource('POCKET READ ONLY');
          setPolariumStatus(null);
          setReadiness(payload.readiness?.state ?? providerV2Status.readiness?.state ?? null);
          setError(null);
          setCandles((previousCandles) => {
            const { candles: updatedCandles } = measureFridayLatencyAudit(
              't6_frontend_merge_finished',
              () => reconcileRealCandleSeries(previousCandles, payload.candles, DEFAULT_LIMIT),
              {
                provider: 'POCKET',
                symbol: payload.symbol,
                raw_size: payload.raw_size,
                previous_count: previousCandles.length,
                incoming_count: payload.candles.length
              }
            );
            const finalCandles = Object.is(updatedCandles, previousCandles) ? previousCandles : updatedCandles;
            recordChartBindingTrace('CANDLE_STATE_UPDATED', {
              provider: 'POCKET',
              symbol: payload.symbol,
              raw_size: payload.raw_size,
              endpoint: chartEndpoint,
              response_count: payload.count,
              normalized_count: payload.candles.length,
              state_count: finalCandles.length,
              request_sequence: requestSequence,
              response_applied: true,
              selected_source: 'PROVIDER_V2',
              ...summarizeChartBindingCandles(finalCandles)
            });
            return finalCandles;
          });
          return;
        }
        setProviderName('POLARIUM');
        setActiveKey(null);
        setReadiness(null);
        const statusPayload = await loadPolariumProviderStatus(controller.signal);
        recordChartBindingTrace('SESSION_CONTEXT_RECEIVED', {
          active_id: statusPayload.sessionContext.visibleActiveId,
          raw_size: statusPayload.sessionContext.visibleRawSize,
          symbol: statusPayload.sessionContext.visibleSymbol,
          state_count: candlesLengthRef.current,
          request_sequence: requestSequence,
          reason: statusPayload.connected ? 'CONNECTED' : 'DISCONNECTED'
        });
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
        const fallbackContext = followPolarium ? null : firstAvailableSeries(nextAvailableSeries);
        const validManualContext = manualContext && (hasAvailableSeries(nextAvailableSeries, manualContext) || sameSeries(manualContext, displayedContext))
          ? manualContext
          : null;
        const nextContext = followPolarium
          ? autoContext ?? lastValidAutoContextRef.current ?? displayedContext ?? fallbackContext
          : validManualContext ?? displayedContext ?? fallbackContext;
        const shouldPreserveDisplayedCandles = !nextContext && displayedContext && candlesLengthRef.current > 0;
        const nextDisplayedContext = nextContext ?? (shouldPreserveDisplayedCandles ? displayedContext : null);
        recordChartBindingTrace('ACTIVE_KEY_RESOLVED', {
          active_id: nextDisplayedContext?.activeId ?? null,
          raw_size: nextDisplayedContext?.rawSize ?? null,
          symbol: statusPayload.sessionContext.visibleSymbol,
          state_count: candlesLengthRef.current,
          request_sequence: requestSequence,
          reason: followPolarium ? 'FOLLOW_POLARIUM' : 'MANUAL_OR_FALLBACK'
        });
        if (!isMounted) return;
        setPolariumStatus(statusPayload);
        setAvailableSeries(nextAvailableSeries);
        setAutoActiveId(autoContext?.activeId ?? null);
        setAutoRawSize(autoContext?.rawSize ?? null);
        setSource(statusPayload.connected ? 'POLARIUM AUTHORIZED CDP LIVE' : 'DISCONNECTED');
        publishPolariumSessionUpdate({ ...statusPayload.sessionContext, candles });

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
        const chartEndpoint = `${API_BASE_URL}/market/chart?${params.toString()}`;
        recordChartBindingTrace('CHART_FETCH_START', {
          active_id: nextDisplayedContext.activeId,
          raw_size: nextDisplayedContext.rawSize,
          symbol: statusPayload.sessionContext.visibleSymbol,
          endpoint: chartEndpoint,
          request_sequence: requestSequence,
          requested_active_id: nextDisplayedContext.activeId,
          requested_raw_size: nextDisplayedContext.rawSize,
          current_context_active_id: displayedContextRef.current?.activeId ?? null,
          current_context_raw_size: displayedContextRef.current?.rawSize ?? null
        });
        const response = await fetch(chartEndpoint, {
          signal: controller.signal
        });
        if (!response.ok) {
          recordChartBindingTrace('CHART_FETCH_ERROR', {
            active_id: nextDisplayedContext.activeId,
            raw_size: nextDisplayedContext.rawSize,
            symbol: statusPayload.sessionContext.visibleSymbol,
            endpoint: chartEndpoint,
            http_status: response.status,
            request_sequence: requestSequence,
            requested_active_id: nextDisplayedContext.activeId,
            requested_raw_size: nextDisplayedContext.rawSize,
            current_context_active_id: displayedContextRef.current?.activeId ?? null,
            current_context_raw_size: displayedContextRef.current?.rawSize ?? null,
            response_ignored: true,
            reason: 'HTTP_ERROR'
          });
          throw new Error(`Market chart API returned ${response.status}`);
        }
        const payload = (await response.json()) as MarketChartResponse;
        const responseCount = Number.isFinite(payload.count) ? payload.count : payload.candles.length;
        recordChartBindingTrace(payload.candles.length ? 'CHART_FETCH_SUCCESS' : 'CHART_FETCH_EMPTY', {
          active_id: payload.active_id,
          raw_size: payload.raw_size,
          symbol: payload.symbol,
          endpoint: chartEndpoint,
          http_status: response.status,
          response_count: responseCount,
          request_sequence: requestSequence,
          requested_active_id: nextDisplayedContext.activeId,
          requested_raw_size: nextDisplayedContext.rawSize,
          response_active_id: payload.active_id,
          response_raw_size: payload.raw_size,
          current_context_active_id: displayedContextRef.current?.activeId ?? null,
          current_context_raw_size: displayedContextRef.current?.rawSize ?? null,
          reason: payload.candles.length ? 'OK' : 'EMPTY_CANDLES'
        });
        if (!isMounted) return;
        recordFridayLatencyAudit('t5_frontend_received', {
          provider: 'POLARIUM',
          active_id: payload.active_id,
          raw_size: payload.raw_size,
          candle_count: payload.candles.length
        });
        if (requestSequence <= lastAppliedRequestRef.current) {
          recordChartBindingTrace('STALE_RESPONSE_IGNORED', {
            active_id: payload.active_id,
            raw_size: payload.raw_size,
            symbol: payload.symbol,
            endpoint: chartEndpoint,
            response_count: responseCount,
            state_count: candlesLengthRef.current,
            request_sequence: requestSequence,
            requested_active_id: nextDisplayedContext.activeId,
            requested_raw_size: nextDisplayedContext.rawSize,
            response_active_id: payload.active_id,
            response_raw_size: payload.raw_size,
            current_context_active_id: displayedContextRef.current?.activeId ?? null,
            current_context_raw_size: displayedContextRef.current?.rawSize ?? null,
            response_ignored: true,
            reason: 'OLDER_THAN_LAST_APPLIED'
          });
          return;
        }
        const currentDisplayedContext = displayedContextRef.current;
        const payloadContext = { activeId: payload.active_id, rawSize: payload.raw_size };
        if (!sameSeries(payloadContext, nextDisplayedContext)) {
          recordChartBindingTrace('STALE_ACTIVE_KEY_RESPONSE_IGNORED', {
            active_id: payload.active_id,
            raw_size: payload.raw_size,
            symbol: payload.symbol,
            endpoint: chartEndpoint,
            response_count: responseCount,
            state_count: candlesLengthRef.current,
            request_sequence: requestSequence,
            requested_active_id: nextDisplayedContext.activeId,
            requested_raw_size: nextDisplayedContext.rawSize,
            response_active_id: payload.active_id,
            response_raw_size: payload.raw_size,
            current_context_active_id: currentDisplayedContext?.activeId ?? null,
            current_context_raw_size: currentDisplayedContext?.rawSize ?? null,
            response_ignored: true,
            reason: 'PAYLOAD_CONTEXT_MISMATCH'
          });
          return;
        }
        const isSwitchingSeries = !sameSeries(currentDisplayedContext, payloadContext);
        if (isSwitchingSeries && payload.candles.length === 0 && followPolarium) {
          lastAppliedRequestRef.current = requestSequence;
          setActiveId(payload.active_id);
          setRawSize(payload.raw_size);
          displayedContextRef.current = payloadContext;
          recordChartBindingTrace('CANDLE_STATE_UPDATED', {
            active_id: payload.active_id,
            raw_size: payload.raw_size,
            symbol: payload.symbol,
            endpoint: chartEndpoint,
            response_count: responseCount,
            normalized_count: 0,
            state_count: 0,
            request_sequence: requestSequence,
            requested_active_id: nextDisplayedContext.activeId,
            requested_raw_size: nextDisplayedContext.rawSize,
            response_active_id: payload.active_id,
            response_raw_size: payload.raw_size,
            current_context_active_id: currentDisplayedContext?.activeId ?? null,
            current_context_raw_size: currentDisplayedContext?.rawSize ?? null,
            response_applied: true,
            reason: 'SWITCHED_TO_EMPTY_FOLLOW_CONTEXT'
          });
          setCandles([]);
          publishPolariumSessionUpdate({ ...statusPayload.sessionContext, activeId: payload.active_id, rawSize: payload.raw_size, candles: [] });
          setError(null);
          return;
        }
        const shouldKeepPreviousCandles = payload.candles.length === 0 && candlesLengthRef.current > 0;
        if (shouldKeepPreviousCandles) {
          recordChartBindingTrace('STALE_RESPONSE_IGNORED', {
            active_id: payload.active_id,
            raw_size: payload.raw_size,
            symbol: payload.symbol,
            endpoint: chartEndpoint,
            response_count: responseCount,
            state_count: candlesLengthRef.current,
            request_sequence: requestSequence,
            requested_active_id: nextDisplayedContext.activeId,
            requested_raw_size: nextDisplayedContext.rawSize,
            response_active_id: payload.active_id,
            response_raw_size: payload.raw_size,
            current_context_active_id: currentDisplayedContext?.activeId ?? null,
            current_context_raw_size: currentDisplayedContext?.rawSize ?? null,
            response_ignored: true,
            reason: 'EMPTY_RESPONSE_PRESERVED_PREVIOUS_STATE'
          });
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
          let nextCandles = payload.candles;
          recordChartBindingTrace('CANDLES_NORMALIZED', {
            active_id: payload.active_id,
            raw_size: payload.raw_size,
            symbol: payload.symbol,
            endpoint: chartEndpoint,
            response_count: responseCount,
            normalized_count: nextCandles.length,
            request_sequence: requestSequence,
            requested_active_id: nextDisplayedContext.activeId,
            requested_raw_size: nextDisplayedContext.rawSize,
            response_active_id: payload.active_id,
            response_raw_size: payload.raw_size,
            current_context_active_id: currentDisplayedContext?.activeId ?? null,
            current_context_raw_size: currentDisplayedContext?.rawSize ?? null,
            ...summarizeChartBindingCandles(nextCandles)
          });
          if (!sameSeries(currentDisplayedContext, payloadContext)) {
            publishPolariumSessionUpdate({ ...statusPayload.sessionContext, activeId: payload.active_id, rawSize: payload.raw_size, candles: nextCandles });
            recordChartBindingTrace('CANDLE_STATE_UPDATED', {
              active_id: payload.active_id,
              raw_size: payload.raw_size,
              symbol: payload.symbol,
              endpoint: chartEndpoint,
              response_count: responseCount,
              normalized_count: nextCandles.length,
              state_count: nextCandles.length,
              request_sequence: requestSequence,
              requested_active_id: nextDisplayedContext.activeId,
              requested_raw_size: nextDisplayedContext.rawSize,
              response_active_id: payload.active_id,
              response_raw_size: payload.raw_size,
              current_context_active_id: currentDisplayedContext?.activeId ?? null,
              current_context_raw_size: currentDisplayedContext?.rawSize ?? null,
              response_applied: true,
              response_ignored: false,
              reason: 'SERIES_SWITCH',
              ...summarizeChartBindingCandles(nextCandles)
            });
            return nextCandles;
          }
          if (!nextCandles.length && previousCandles.length) {
            nextCandles = previousCandles;
            publishPolariumSessionUpdate({ ...statusPayload.sessionContext, activeId: payload.active_id, rawSize: payload.raw_size, candles: nextCandles });
            recordChartBindingTrace('CANDLE_STATE_UPDATED', {
              active_id: payload.active_id,
              raw_size: payload.raw_size,
              symbol: payload.symbol,
              endpoint: chartEndpoint,
              response_count: responseCount,
              normalized_count: 0,
              state_count: nextCandles.length,
              request_sequence: requestSequence,
              requested_active_id: nextDisplayedContext.activeId,
              requested_raw_size: nextDisplayedContext.rawSize,
              response_active_id: payload.active_id,
              response_raw_size: payload.raw_size,
              current_context_active_id: currentDisplayedContext?.activeId ?? null,
              current_context_raw_size: currentDisplayedContext?.rawSize ?? null,
              response_applied: true,
              response_ignored: false,
              reason: 'PRESERVED_PREVIOUS_STATE',
              ...summarizeChartBindingCandles(nextCandles)
            });
            return nextCandles;
          }
          const { candles: updatedCandles } = measureFridayLatencyAudit(
            't6_frontend_merge_finished',
            () => reconcileRealCandleSeries(previousCandles, nextCandles, DEFAULT_LIMIT),
            {
              provider: 'POLARIUM',
              active_id: payload.active_id,
              raw_size: payload.raw_size,
              previous_count: previousCandles.length,
              incoming_count: nextCandles.length
            }
          );
          const finalCandles = Object.is(updatedCandles, previousCandles) ? previousCandles : updatedCandles;
          publishPolariumSessionUpdate({ ...statusPayload.sessionContext, activeId: payload.active_id, rawSize: payload.raw_size, candles: finalCandles });
          recordChartBindingTrace('CANDLE_STATE_UPDATED', {
            active_id: payload.active_id,
            raw_size: payload.raw_size,
            symbol: payload.symbol,
            endpoint: chartEndpoint,
            response_count: responseCount,
            normalized_count: nextCandles.length,
            state_count: finalCandles.length,
            request_sequence: requestSequence,
            requested_active_id: nextDisplayedContext.activeId,
            requested_raw_size: nextDisplayedContext.rawSize,
            response_active_id: payload.active_id,
            response_raw_size: payload.raw_size,
            current_context_active_id: currentDisplayedContext?.activeId ?? null,
            current_context_raw_size: currentDisplayedContext?.rawSize ?? null,
            response_applied: true,
            response_ignored: false,
            reason: Object.is(updatedCandles, previousCandles) ? 'UNCHANGED_AFTER_RECONCILE' : 'UPDATED_AFTER_RECONCILE',
            ...summarizeChartBindingCandles(finalCandles)
          });
          return finalCandles;
        });
      } catch (requestError) {
        if (controller.signal.aborted) return;
        if (!isMounted) return;
        recordChartBindingTrace('CHART_FETCH_ERROR', {
          active_id: displayedContextRef.current?.activeId ?? null,
          raw_size: displayedContextRef.current?.rawSize ?? null,
          state_count: candlesLengthRef.current,
          request_sequence: requestSequence,
          current_context_active_id: displayedContextRef.current?.activeId ?? null,
          current_context_raw_size: displayedContextRef.current?.rawSize ?? null,
          response_ignored: true,
          reason: requestError instanceof Error ? requestError.name : 'UNKNOWN_ERROR'
        });
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

  const activeSymbol =
    providerName === 'POCKET'
      ? availableSeries.find((item) => item.provider === 'POCKET' && item.rawSize === rawSize && item.count >= 0)?.symbol ?? null
      :
    resolveSeriesSymbol(activeId, rawSize, availableSeries) ??
    (activeId !== null && activeId === polariumStatus?.sessionContext.visibleActiveId ? polariumStatus.sessionContext.visibleSymbol : null);
  const timeframeLabel = rawSize ? rawSizeToTimeframe(rawSize) : 'Não disponível';
  const activeIdsSeen = uniqueNumbers(availableSeries.map((item) => item.activeId));
  const rawSizesSeen = uniqueNumbers(availableSeries.map((item) => item.rawSize));
  const pipelineOnline = Boolean((polariumStatus?.processed ?? 0) > 0);
  const storeOnline = Boolean(candles.length || availableSeries.some((item) => item.provider === 'POLARIUM' && item.count > 0));
  const chartOnline = Boolean(activeId && rawSize && candles.length);
  const sessionContext =
    providerName === 'POCKET'
      ? {
          ...disconnectedPolariumSessionContext(candles),
          displayName: activeSymbol ?? 'Não disponível',
          rawSize,
          timeframe: rawSize ? rawSizeToTimeframe(rawSize) : null,
          historyState: readiness ?? 'NO_HISTORY',
          historyCount: candles.length,
          historyRequired: 50,
          historyProgress: candles.length ? Math.min(1, candles.length / 50) : 0,
          bootstrapComplete: readiness === 'READY',
          analysisBlocked: readiness !== 'READY',
          analysisBlockReason: readiness === 'READY' ? null : 'POCKET_HISTORY_NOT_READY'
        }
      : polariumStatus?.sessionContext ??
        disconnectedPolariumSessionContext(candles);

  return {
    provider: providerName,
    activeKey,
    activeId,
    rawSize,
    autoActiveId,
    autoRawSize,
    candles,
    availableSeries,
    source,
    assetLabel: activeSymbol ?? (activeId !== null ? 'ATIVO NÃO IDENTIFICADO' : 'Não disponível'),
    timeframeLabel,
    bridgeOnline: Boolean(polariumStatus?.connected && polariumStatus.market_socket_ready),
    pipelineOnline,
    storeOnline,
    chartOnline,
    pipelineSuccessCount: polariumStatus?.processed ?? 0,
    activeIdsSeen,
    rawSizesSeen,
    lastEventName: polariumStatus?.received ? 'candles-generated' : null,
    lastEventAt: null,
    sessionContext: { ...sessionContext, candles },
    readiness,
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

export function resolveActiveSeries(status: PolariumRuntimeStatus, availableSeries: RealCandleSeriesSummary[]): SeriesContext | null {
  const visibleActiveId = status.sessionContext.visibleActiveId;
  const visibleRawSize = status.sessionContext.visibleRawSize;
  if (!status.connected || visibleActiveId === null) {
    return null;
  }
  if (typeof visibleRawSize === 'number') {
    return { activeId: visibleActiveId, rawSize: visibleRawSize };
  }
  const rawSizes = status.sessionContext.availableRawSizes.length ? status.sessionContext.availableRawSizes : status.latestRawSizes;
  for (const rawSize of rawSizes) {
    const context = { activeId: visibleActiveId, rawSize };
    if (hasAvailableSeries(availableSeries, context)) {
      return context;
    }
  }
  if (rawSizes.length > 0) {
    return { activeId: visibleActiveId, rawSize: rawSizes[0] };
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

async function loadPolariumProviderStatus(signal: AbortSignal): Promise<PolariumRuntimeStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/market/providers`, { signal });
    if (!response.ok) return offlinePolariumStatus();
    const payload = (await response.json()) as MarketProvidersResponse;
    const polarium = payload.providers.find((provider) => provider.provider === 'POLARIUM');
    return {
      connected: Boolean(polarium?.runtime?.connected && polarium?.live_source?.connected),
      market_socket_ready: Boolean(polarium?.runtime?.market_socket_ready),
      processed: Number(polarium?.runtime?.processed ?? 0),
      received: Number(polarium?.runtime?.received ?? polarium?.live_source?.received_events ?? 0),
      latestActiveId: typeof polarium?.runtime?.latest_active_id === 'number' ? polarium.runtime.latest_active_id : null,
      latestSymbol: typeof polarium?.runtime?.latest_symbol === 'string' ? polarium.runtime.latest_symbol : null,
      latestRawSizes: Array.isArray(polarium?.runtime?.latest_raw_sizes) ? polarium.runtime.latest_raw_sizes.filter((value): value is number => typeof value === 'number') : [],
      sessionContext: normalizePolariumSessionContext(polarium?.runtime?.session_context, [])
    };
  } catch (_error) {
    return offlinePolariumStatus();
  }
}

async function loadProviderV2Status(signal: AbortSignal): Promise<ProviderV2StatusResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/market/provider-v2/status`, { signal });
    if (!response.ok) return null;
    return (await response.json()) as ProviderV2StatusResponse;
  } catch (_error) {
    return null;
  }
}

function offlinePolariumStatus(): PolariumRuntimeStatus {
  return {
    connected: false,
    market_socket_ready: false,
    processed: 0,
    received: 0,
    latestActiveId: null,
    latestSymbol: null,
    latestRawSizes: [],
    sessionContext: disconnectedPolariumSessionContext()
  };
}

function uniqueNumbers(values: Array<number | null>): number[] {
  return Array.from(new Set(values.filter((value): value is number => typeof value === 'number'))).sort((left, right) => left - right);
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
