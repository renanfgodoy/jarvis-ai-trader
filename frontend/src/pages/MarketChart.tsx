import type { ReactNode } from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { CheckCircle2, CircleDashed } from 'lucide-react';
import PageContainer from '../components/PageContainer';
import StatusBadge from '../components/StatusBadge';
import RealCandleChart, { type RealChartCandle } from '../components/chart/RealCandleChart';
import { mergeCandlesByTime } from '../components/chart/RealCandleChart/sync';

const MIN_ANALYSIS_CANDLES = 100;
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';
const IQ_TIMEFRAMES = [60, 300, 900];
const IQ_BOOTSTRAP_LIMIT = 1000;
const IQ_REFRESH_LIMIT = 5;
const IQ_POLL_INTERVAL_MS = 5000;
const IQ_REALTIME_POLL_INTERVAL_MS = 1000;
const IQ_PUSH_HEALTH_CHECK_INTERVAL_MS = 2000;
const IQ_PUSH_HEARTBEAT_TIMEOUT_MS = 15000;
const IQ_ASSET_RETRY_DELAYS_MS = [1000, 2000, 4000];
const IQ_STATUS_TIMEOUT_MS = 3000;
const IQ_CONNECT_TIMEOUT_MS = 8000;
const IQ_ASSETS_TIMEOUT_MS = 8000;
const IQ_CANDLES_TIMEOUT_MS = 10000;
const IQ_REALTIME_TIMEOUT_MS = 3000;
const IQ_MARKET_STORAGE_KEY = 'friday.iq.market';
const IQ_SYMBOL_STORAGE_KEY = 'friday.iq.symbol';
const IQ_TIMEFRAME_STORAGE_KEY = 'friday.iq.rawSize';
const FRIDAY_UI_MODE_STORAGE_KEY = 'friday.ui.mode';
const FRIDAY_STRATEGY_STORAGE_KEY = 'friday.strategy.selected';

type FridayUiMode = 'OPERATOR' | 'DEVELOPER';
type IQMarketType = 'OTC' | 'REGULAR';
type FridayStrategyStatus = 'IDLE' | 'LOADED' | 'DISABLED';
type FridayStrategyReadiness = 'INACTIVE' | 'READY' | 'BLOCKED';
type FridayStrategyConfluence = {
  id: string;
  name: string;
  status: 'PENDING' | 'MET' | 'NOT_MET';
};
type FridayStrategyDefinition = {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  supportedMarkets: IQMarketType[];
  supportedTimeframes: number[];
  status: FridayStrategyStatus;
  readiness: FridayStrategyReadiness;
  confluences: FridayStrategyConfluence[];
};
type IQAsset = { symbol: string; display_name: string; is_open: boolean };
type IQProviderStatus = { connected?: boolean };
type IQSourceMode = 'CHECKING' | 'NEAR_REALTIME' | 'SNAPSHOT' | 'STALE' | 'NO_DATA';
type IQDeliveryState = 'CONNECTING' | 'SSE' | 'POLLING_FALLBACK' | 'RECONNECTING' | 'DISCONNECTED';
type IQPushStats = {
  eventsReceived: number;
  chartUpdates: number;
  eventsCoalesced: number;
  lastEventAt: number | null;
  lastAppliedAt: number | null;
  sequence: number;
  reconnects: number;
  fallbacks: number;
  deliverySamplesMs: number[];
};
type IQRealtimeStreamEvent = {
  type: 'candle' | 'heartbeat';
  provider: string;
  market_type: IQMarketType;
  symbol: string;
  raw_size: number;
  source_mode: IQSourceMode | 'HEARTBEAT';
  sequence: number;
  worker_received_at?: number | null;
  backend_published_at?: number | null;
  candle?: RealChartCandle;
};

const FRIDAY_STRATEGIES: FridayStrategyDefinition[] = [];

export default function MarketChart() {
  const [iqAssets, setIqAssets] = useState<IQAsset[]>([]);
  const [iqMarketType, setIqMarketType] = useState<IQMarketType>(() => readStoredMarketType());
  const [iqSymbol, setIqSymbol] = useState(() => localStorage.getItem(IQ_SYMBOL_STORAGE_KEY) ?? fallbackIqSymbolAfterAssetsFailure('', readStoredMarketType()));
  const [iqRawSize, setIqRawSize] = useState(() => readStoredRawSize());
  const [iqCandles, setIqCandles] = useState<RealChartCandle[]>([]);
  const [iqError, setIqError] = useState<string | null>(null);
  const [iqAssetLoading, setIqAssetLoading] = useState(false);
  const [iqLoading, setIqLoading] = useState(false);
  const [iqLastUpdateAt, setIqLastUpdateAt] = useState<string | null>(null);
  const [iqSourceMode, setIqSourceMode] = useState<IQSourceMode>('CHECKING');
  const [iqLastMovementAt, setIqLastMovementAt] = useState<number | null>(null);
  const [iqRecentMovementIntervals, setIqRecentMovementIntervals] = useState<number[]>([]);
  const [iqDeliveryState, setIqDeliveryState] = useState<IQDeliveryState>('CONNECTING');
  const [iqPushStats, setIqPushStats] = useState<IQPushStats>(() => emptyIqPushStats());
  const [fridayUiMode, setFridayUiMode] = useState<FridayUiMode>(() => readStoredFridayUiMode());
  const [selectedStrategyId, setSelectedStrategyId] = useState(() => localStorage.getItem(FRIDAY_STRATEGY_STORAGE_KEY) ?? '');
  const [iqDiagnosticsExpanded, setIqDiagnosticsExpanded] = useState(false);
  const [nowTick, setNowTick] = useState(() => Date.now());
  const [iqAssetRetryKey, setIqAssetRetryKey] = useState(0);
  const iqConnectPromiseRef = useRef<Promise<void> | null>(null);
  const lastMovementKeyRef = useRef<string | null>(null);
  const lastMovementTimestampRef = useRef<number | null>(null);
  const selectedIqAsset = useMemo(() => iqAssets.find((asset) => asset.symbol === iqSymbol) ?? null, [iqAssets, iqSymbol]);
  const selectedStrategy = useMemo(
    () => FRIDAY_STRATEGIES.find((strategy) => strategy.id === selectedStrategyId) ?? null,
    [selectedStrategyId]
  );
  const displayedSymbol = selectedIqAsset?.display_name ?? formatIqSymbol(iqSymbol);
  const latest = iqCandles[iqCandles.length - 1];
  const feedState = getIqFeedState(latest?.time ?? null, iqRawSize, nowTick);
  const readiness = getReadiness({
    sourceOnline: Boolean(iqSymbol) && !iqError,
    rawSize: iqRawSize,
    candleCount: iqCandles.length,
    latestTime: latest?.time ?? null,
    feedState: feedState.status,
    sourceMode: iqSourceMode
  });
  const movementSummary = getMovementSummary(iqLastMovementAt, iqRecentMovementIntervals, nowTick);
  const deliverySummary = getDeliverySummary(iqPushStats, nowTick);
  const operatorMarketStatus = getOperatorMarketStatus(iqSourceMode, feedState, iqLoading, iqCandles.length);

  useEffect(() => {
    logIqFlow('page_mounted', { marketType: iqMarketType, symbolSelected: Boolean(iqSymbol), rawSize: iqRawSize });
  }, []);

  useEffect(() => {
    const intervalId = window.setInterval(() => setNowTick(Date.now()), 1000);
    return () => window.clearInterval(intervalId);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    setIqError(null);
    setIqAssetLoading(true);
    logIqFlow('assets_effect_started', { marketType: iqMarketType });

    async function loadIqAssets() {
      for (let attempt = 0; attempt <= IQ_ASSET_RETRY_DELAYS_MS.length; attempt += 1) {
        try {
          await ensureIqOptionConnected(iqConnectPromiseRef);
          logIqFlow('assets_request_started', { marketType: iqMarketType, attempt });
          const payload = await fetchJsonWithTimeout(`${API_BASE_URL}/market/providers/iq-option/assets?market_type=${iqMarketType}`, {
            signal: controller.signal,
            timeoutMs: IQ_ASSETS_TIMEOUT_MS,
            errorMessage: 'IQ Option assets'
          });
          if (cancelled) return;
          const assets = parseIqAssetsResponse(payload);
          logIqFlow('assets_request_finished', { marketType: iqMarketType, count: assets.length });
          setIqAssets(assets);
          setIqSymbol((current) => {
            const selected = chooseIqSymbol(current, assets, iqMarketType);
            logIqFlow('symbol_selected', { marketType: iqMarketType, selectedSymbol: selected || null, assetsCount: assets.length });
            return selected;
          });
          setIqError(null);
          return;
        } catch (error) {
          if (cancelled || controller.signal.aborted) return;
          logIqFlow('assets_request_failed', {
            marketType: iqMarketType,
            attempt,
            errorCode: sanitizeIqError(error)
          });
          if (attempt < IQ_ASSET_RETRY_DELAYS_MS.length && isRetryableIqAssetError(error)) {
            await abortableDelay(IQ_ASSET_RETRY_DELAYS_MS[attempt], controller.signal);
            continue;
          }
          setIqSymbol((current) => {
            const fallbackSymbol = fallbackIqSymbolAfterAssetsFailure(current, iqMarketType);
            if (fallbackSymbol) {
              setIqError(null);
            } else {
              setIqError('Não foi possível carregar os ativos IQ Option.');
            }
            return fallbackSymbol;
          });
          return;
        }
      }
    }

    void loadIqAssets().finally(() => {
      if (!cancelled) setIqAssetLoading(false);
    });

    return () => {
      cancelled = true;
      controller.abort();
      logIqFlow('assets_effect_cleanup', { marketType: iqMarketType });
    };
  }, [iqAssetRetryKey, iqMarketType]);

  useEffect(() => {
    if (!iqSymbol) return;
    let cancelled = false;
    let inFlight = false;
    let hasLoadedInitialCandles = false;
    let pushStreamStarted = false;
    let fallbackPollingEnabled = true;
    let fallbackReported = false;
    let lastPushHeartbeatAt = 0;
    let lastAppliedPushSequence = 0;
    let pendingPushEvent: IQRealtimeStreamEvent | null = null;
    let animationFrameId: number | null = null;
    let eventSource: EventSource | null = null;
    const expectedSymbol = iqSymbol;
    const expectedRawSize = iqRawSize;
    const controller = new AbortController();
    setIqCandles([]);
    setIqLastUpdateAt(null);
    setIqSourceMode('CHECKING');
    setIqLastMovementAt(null);
    setIqRecentMovementIntervals([]);
    setIqDeliveryState('CONNECTING');
    setIqPushStats(emptyIqPushStats());
    lastMovementKeyRef.current = null;
    lastMovementTimestampRef.current = null;
    setIqError(null);
    setIqLoading(true);
    logIqFlow('bootstrap_effect_started', { marketType: iqMarketType, symbol: expectedSymbol, rawSize: expectedRawSize });

    async function loadIqCandles(refresh: boolean) {
      if (inFlight) return;
      inFlight = true;
      const shouldRefresh = refresh && hasLoadedInitialCandles;
      const params = new URLSearchParams({
        symbol: expectedSymbol,
        raw_size: String(expectedRawSize),
        limit: String(shouldRefresh ? IQ_REFRESH_LIMIT : IQ_BOOTSTRAP_LIMIT),
        market_type: iqMarketType
      });
      if (shouldRefresh) {
        params.set('refresh_limit', String(IQ_REFRESH_LIMIT));
      }
      try {
        logIqFlow(shouldRefresh ? 'poll_request_started' : 'bootstrap_request_started', { marketType: iqMarketType, symbol: expectedSymbol, rawSize: expectedRawSize });
        const payload = await fetchJsonWithTimeout(`${API_BASE_URL}/market/providers/iq-option/candles?${params.toString()}`, {
          signal: controller.signal,
          timeoutMs: IQ_CANDLES_TIMEOUT_MS,
          errorMessage: 'IQ Option candles'
        });
        if (cancelled) return;
        if (payload.provider !== 'IQ_OPTION' || payload.symbol !== expectedSymbol || Number(payload.raw_size) !== expectedRawSize) {
          logIqFlow('candles_response_ignored', { expectedSymbol, expectedRawSize });
          return;
        }
        const parsed = parseIqCandlesResponse(payload);
        const nextCandles = parsed.candles;
        logIqFlow(shouldRefresh ? 'poll_request_finished' : 'bootstrap_request_finished', {
          marketType: iqMarketType,
          symbol: expectedSymbol,
          rawSize: expectedRawSize,
          count: parsed.count,
          candlesCount: nextCandles.length
        });
        if (nextCandles.length > 0) {
          hasLoadedInitialCandles = true;
          setIqCandles((previousCandles) => mergeIqOptionCandles(previousCandles, nextCandles));
          setIqLastUpdateAt(new Date().toISOString());
          startPushStream();
        }
        setIqError(null);
      } catch (error) {
        if (!cancelled && !(error instanceof DOMException && error.name === 'AbortError')) {
          logIqFlow(shouldRefresh ? 'poll_request_failed' : 'bootstrap_request_failed', {
            marketType: iqMarketType,
            symbol: expectedSymbol,
            rawSize: expectedRawSize,
            errorCode: sanitizeIqError(error)
          });
          setIqError(error instanceof Error ? error.message : 'Falha ao carregar candles IQ Option');
        }
      } finally {
        inFlight = false;
        if (!cancelled) setIqLoading(false);
      }
    }

    async function loadIqRealtime() {
      if (!hasLoadedInitialCandles) return;
      const params = new URLSearchParams({
        symbol: expectedSymbol,
        raw_size: String(expectedRawSize),
        limit: String(IQ_BOOTSTRAP_LIMIT),
        market_type: iqMarketType
      });
      try {
        const payload = await fetchJsonWithTimeout(`${API_BASE_URL}/market/providers/iq-option/realtime-candles?${params.toString()}`, {
          signal: controller.signal,
          timeoutMs: IQ_REALTIME_TIMEOUT_MS,
          errorMessage: 'IQ Option realtime candles'
        });
        if (cancelled) return;
        if (payload.provider !== 'IQ_OPTION' || payload.symbol !== expectedSymbol || Number(payload.raw_size) !== expectedRawSize) {
          logIqFlow('realtime_response_ignored', { expectedSymbol, expectedRawSize });
          return;
        }
        const parsed = parseIqCandlesResponse(payload);
        const nextCandles = parsed.candles;
        const sourceMode = parseIqSourceMode(payload);
        logIqFlow('realtime_request_finished', {
          marketType: iqMarketType,
          symbol: expectedSymbol,
          rawSize: expectedRawSize,
          sourceMode,
          count: parsed.count,
          candlesCount: nextCandles.length
        });
        setIqSourceMode(sourceMode);
        if (nextCandles.length > 0) {
          setIqCandles((previousCandles) => mergeIqOptionCandles(previousCandles, nextCandles));
          setIqLastUpdateAt(new Date().toISOString());
        }
      } catch (error) {
        if (!cancelled && !(error instanceof DOMException && error.name === 'AbortError')) {
          logIqFlow('realtime_request_failed', {
            marketType: iqMarketType,
            symbol: expectedSymbol,
            rawSize: expectedRawSize,
            errorCode: sanitizeIqError(error)
          });
          setIqSourceMode('SNAPSHOT');
        }
      }
    }

    function startPushStream() {
      if (pushStreamStarted || !hasLoadedInitialCandles) return;
      pushStreamStarted = true;
      if (!('EventSource' in window)) {
        fallbackPollingEnabled = true;
        setIqDeliveryState('POLLING_FALLBACK');
        registerFallback();
        logIqFlow('sse_unavailable_fallback_enabled', { marketType: iqMarketType, symbol: expectedSymbol, rawSize: expectedRawSize });
        return;
      }
      const params = new URLSearchParams({
        symbol: expectedSymbol,
        raw_size: String(expectedRawSize),
        market_type: iqMarketType
      });
      eventSource = new EventSource(`${API_BASE_URL}/market/providers/iq-option/realtime-candles/stream?${params.toString()}`);
      fallbackPollingEnabled = false;
      setIqDeliveryState('CONNECTING');
      logIqFlow('sse_stream_started', { marketType: iqMarketType, symbol: expectedSymbol, rawSize: expectedRawSize });

      eventSource.onopen = () => {
        if (cancelled) return;
        fallbackPollingEnabled = false;
        fallbackReported = false;
        lastPushHeartbeatAt = Date.now();
        setIqDeliveryState('SSE');
        setIqPushStats((current) => ({ ...current, reconnects: current.eventsReceived > 0 ? current.reconnects + 1 : current.reconnects }));
        logIqFlow('sse_stream_open', { marketType: iqMarketType, symbol: expectedSymbol, rawSize: expectedRawSize });
      };

      eventSource.onerror = () => {
        if (cancelled) return;
        fallbackPollingEnabled = true;
        setIqDeliveryState('POLLING_FALLBACK');
        registerFallback();
        logIqFlow('sse_stream_error_fallback_enabled', { marketType: iqMarketType, symbol: expectedSymbol, rawSize: expectedRawSize });
      };

      eventSource.addEventListener('heartbeat', (message) => {
        const event = parseIqRealtimeStreamEvent(message);
        if (!event || !matchesIqRealtimeContext(event, expectedSymbol, expectedRawSize, iqMarketType)) return;
        lastPushHeartbeatAt = Date.now();
        fallbackPollingEnabled = false;
        fallbackReported = false;
        setIqDeliveryState('SSE');
        setIqPushStats((current) => ({
          ...current,
          lastEventAt: Date.now(),
          sequence: Math.max(current.sequence, event.sequence)
        }));
      });

      eventSource.addEventListener('candle', (message) => {
        const event = parseIqRealtimeStreamEvent(message);
        if (!event || !event.candle || !matchesIqRealtimeContext(event, expectedSymbol, expectedRawSize, iqMarketType)) return;
        if (event.sequence <= lastAppliedPushSequence) return;
        lastPushHeartbeatAt = Date.now();
        fallbackPollingEnabled = false;
        fallbackReported = false;
        setIqDeliveryState('SSE');
        if (event.source_mode !== 'HEARTBEAT') {
          setIqSourceMode(event.source_mode);
        }
        if (pendingPushEvent !== null) {
          setIqPushStats((current) => ({ ...current, eventsCoalesced: current.eventsCoalesced + 1 }));
        }
        pendingPushEvent = event;
        setIqPushStats((current) => ({
          ...current,
          eventsReceived: current.eventsReceived + 1,
          lastEventAt: Date.now(),
          sequence: Math.max(current.sequence, event.sequence)
        }));
        if (animationFrameId !== null) return;
        animationFrameId = window.requestAnimationFrame(() => {
          animationFrameId = null;
          const latestPushEvent = pendingPushEvent;
          pendingPushEvent = null;
          if (!latestPushEvent?.candle || latestPushEvent.sequence <= lastAppliedPushSequence) return;
          lastAppliedPushSequence = latestPushEvent.sequence;
          const appliedAt = Date.now();
          setIqCandles((previousCandles) => mergeIqOptionCandles(previousCandles, [latestPushEvent.candle as RealChartCandle]));
          setIqLastUpdateAt(new Date(appliedAt).toISOString());
          setIqPushStats((current) => ({
            ...current,
            chartUpdates: current.chartUpdates + 1,
            lastAppliedAt: appliedAt,
            deliverySamplesMs: appendDeliverySample(current.deliverySamplesMs, deliveryMsForEvent(latestPushEvent, appliedAt))
          }));
        });
      });
    }

    function registerFallback() {
      if (fallbackReported) return;
      fallbackReported = true;
      setIqPushStats((current) => ({ ...current, fallbacks: current.fallbacks + 1 }));
    }

    void loadIqCandles(false);
    const intervalId = window.setInterval(() => {
      void loadIqCandles(true);
    }, IQ_POLL_INTERVAL_MS);
    const realtimeIntervalId = window.setInterval(() => {
      if (fallbackPollingEnabled) {
        void loadIqRealtime();
      }
    }, IQ_REALTIME_POLL_INTERVAL_MS);
    const pushHealthIntervalId = window.setInterval(() => {
      if (!pushStreamStarted || cancelled) return;
      if (lastPushHeartbeatAt > 0 && Date.now() - lastPushHeartbeatAt > IQ_PUSH_HEARTBEAT_TIMEOUT_MS) {
        fallbackPollingEnabled = true;
        setIqDeliveryState('POLLING_FALLBACK');
        registerFallback();
        logIqFlow('sse_heartbeat_timeout_fallback_enabled', { marketType: iqMarketType, symbol: expectedSymbol, rawSize: expectedRawSize });
      }
    }, IQ_PUSH_HEALTH_CHECK_INTERVAL_MS);

    return () => {
      cancelled = true;
      controller.abort();
      eventSource?.close();
      setIqDeliveryState('DISCONNECTED');
      if (animationFrameId !== null) {
        window.cancelAnimationFrame(animationFrameId);
      }
      window.clearInterval(intervalId);
      window.clearInterval(realtimeIntervalId);
      window.clearInterval(pushHealthIntervalId);
      logIqFlow('bootstrap_effect_cleanup', { marketType: iqMarketType, symbol: expectedSymbol, rawSize: expectedRawSize });
    };
  }, [iqMarketType, iqRawSize, iqSymbol]);

  useEffect(() => {
    logIqFlow('chart_props', { symbol: iqSymbol || null, rawSize: iqRawSize, candlesCount: iqCandles.length });
  }, [iqCandles.length, iqRawSize, iqSymbol]);

  useEffect(() => {
    if (!latest) return;
    const nextKey = `${latest.time}:${latest.open}:${latest.high}:${latest.low}:${latest.close}`;
    if (lastMovementKeyRef.current === null) {
      lastMovementKeyRef.current = nextKey;
      lastMovementTimestampRef.current = Date.now();
      setIqLastMovementAt(Date.now());
      return;
    }
    if (lastMovementKeyRef.current === nextKey) {
      return;
    }
    const now = Date.now();
    const previousMovementAt = lastMovementTimestampRef.current;
    lastMovementKeyRef.current = nextKey;
    lastMovementTimestampRef.current = now;
    setIqLastMovementAt(now);
    if (previousMovementAt !== null) {
      setIqRecentMovementIntervals((current) => [...current.slice(-14), now - previousMovementAt]);
    }
  }, [latest]);

  useEffect(() => {
    localStorage.setItem(IQ_MARKET_STORAGE_KEY, iqMarketType);
  }, [iqMarketType]);

  useEffect(() => {
    if (iqSymbol) localStorage.setItem(IQ_SYMBOL_STORAGE_KEY, iqSymbol);
  }, [iqSymbol]);

  useEffect(() => {
    localStorage.setItem(IQ_TIMEFRAME_STORAGE_KEY, String(iqRawSize));
  }, [iqRawSize]);

  useEffect(() => {
    localStorage.setItem(FRIDAY_UI_MODE_STORAGE_KEY, fridayUiMode);
  }, [fridayUiMode]);

  useEffect(() => {
    if (selectedStrategyId) {
      localStorage.setItem(FRIDAY_STRATEGY_STORAGE_KEY, selectedStrategyId);
    } else {
      localStorage.removeItem(FRIDAY_STRATEGY_STORAGE_KEY);
    }
  }, [selectedStrategyId]);

  return (
    <PageContainer className="space-y-2 p-2 2xl:p-3">
      <section className="rounded-2xl border border-white/10 bg-white/[0.025] px-3 py-3">
        <div className="mb-3 flex flex-col gap-2 min-[760px]:flex-row min-[760px]:items-end min-[760px]:justify-between">
          <div className="min-w-0">
            <p className="text-lg font-black uppercase leading-tight tracking-normal text-white">FRIDAY TRADE</p>
            <p className="text-sm font-bold text-slate-400">Análise de mercado</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <MarketHealthBadge status={operatorMarketStatus} />
            <button
              type="button"
              onClick={() => setFridayUiMode((current) => (current === 'OPERATOR' ? 'DEVELOPER' : 'OPERATOR'))}
              className="h-9 rounded-xl border border-white/10 px-3 text-[10px] font-black uppercase tracking-widest text-slate-300 hover:border-cyan-300/40 hover:text-cyan-100"
            >
              {fridayUiMode === 'DEVELOPER' ? 'OPERADOR' : 'DEV'}
            </button>
          </div>
        </div>

        <div className="grid gap-2 lg:grid-cols-[minmax(150px,0.7fr)_minmax(240px,1.3fr)_minmax(150px,0.65fr)_minmax(150px,0.65fr)] lg:items-end">
          <Control label="Mercado">
            <select
              value={iqMarketType}
              onChange={(event) => {
                const nextMarketType = event.target.value as IQMarketType;
                setIqMarketType(nextMarketType);
                setIqAssets([]);
                setIqSymbol(fallbackIqSymbolAfterAssetsFailure('', nextMarketType));
              }}
              className="h-9 w-full rounded-xl border border-white/10 bg-[#080a2a] px-3 text-sm font-black text-white outline-none focus:border-cyan-300/60"
            >
              <option value="OTC">OTC</option>
              <option value="REGULAR">Aberto</option>
            </select>
          </Control>

          <Control label="Ativo">
            <select
              value={iqSymbol}
              onChange={(event) => setIqSymbol(event.target.value)}
              className="h-9 w-full rounded-xl border border-white/10 bg-[#080a2a] px-3 text-sm font-black text-white outline-none focus:border-cyan-300/60"
            >
              {iqAssetLoading && <option value="">Carregando ativos...</option>}
              {iqSymbol && !iqAssets.some((asset) => asset.symbol === iqSymbol) && (
                <option value={iqSymbol}>{formatIqSymbol(iqSymbol)}</option>
              )}
              {!iqAssetLoading && !iqAssets.length && <option value="">{iqMarketType === 'REGULAR' ? 'Mercado regular fechado' : 'Nenhum ativo OTC disponível'}</option>}
              {iqAssets.map((asset) => (
                <option key={asset.symbol} value={asset.symbol}>
                  {asset.display_name}
                </option>
              ))}
            </select>
          </Control>

          <Control label="Timeframe">
            <select
              value={iqRawSize}
              onChange={(event) => setIqRawSize(Number(event.target.value))}
              className="h-9 w-full rounded-xl border border-white/10 bg-[#080a2a] px-3 text-sm font-black text-white outline-none focus:border-cyan-300/60"
            >
              {IQ_TIMEFRAMES.map((rawSize) => (
                <option key={rawSize} value={rawSize}>
                  {formatRawSize(rawSize)}
                </option>
              ))}
            </select>
          </Control>

          <div className="rounded-2xl border border-white/10 bg-[#080a2a] px-3 py-2">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Próxima vela</p>
            <p className="mt-0.5 text-sm font-black text-cyan-100">{formatFeedCountdown(feedState)}</p>
          </div>
        </div>
      </section>

      {operatorMarketStatus.notice && <MarketNotice status={operatorMarketStatus} />}

      <section className="grid min-h-0 gap-2 xl:grid-cols-[minmax(0,3fr)_minmax(320px,1fr)]">
        <div className="min-w-0">
          {iqSymbol && iqRawSize ? (
            <RealCandleChart
              activeId={null}
              symbol={displayedSymbol !== 'Não disponível' ? displayedSymbol : null}
              rawSize={iqRawSize}
              candles={iqCandles}
              compact
              chartClassName="h-[calc(100dvh-218px)] min-h-[420px] max-h-[700px]"
            />
          ) : (
            <IqEmptyChart
              loading={iqAssetLoading || iqLoading}
              error={iqError}
              marketType={iqMarketType}
              onRetry={() => setIqAssetRetryKey((current) => current + 1)}
            />
          )}
        </div>

        <aside className="grid content-start gap-2">
          <FridayStrategyEnginePanel
            strategies={FRIDAY_STRATEGIES}
            selectedStrategy={selectedStrategy}
            selectedStrategyId={selectedStrategyId}
            onSelectStrategy={setSelectedStrategyId}
          />

          {fridayUiMode === 'DEVELOPER' && (
            <>
              <DiagnosticsPanel
                deliveryState={iqDeliveryState}
                sourceMode={iqSourceMode}
                stats={iqPushStats}
                summary={deliverySummary}
                feedState={feedState}
                lastUpdateAt={iqLastUpdateAt}
                nowTick={nowTick}
                expanded={iqDiagnosticsExpanded}
                onToggle={() => setIqDiagnosticsExpanded((current) => !current)}
              />

              <CompactPanel title="Contexto DEV">
                <InfoLine label="Mercado" value={iqMarketType === 'OTC' ? 'OTC' : 'Aberto'} />
                <InfoLine label="Ativo" value={displayedSymbol} />
                <InfoLine label="Timeframe" value={formatRawSize(iqRawSize)} />
                <InfoLine label="Próxima vela" value={formatFeedCountdown(feedState)} />
                <InfoLine label="Modo" value="IQ Option Read Only" />
                <InfoLine label="Provider" value="IQ Option" />
                <InfoLine label="CandleStore" value={`${iqCandles.length} candles`} />
                <InfoLine label="raw_size" value={String(iqRawSize)} />
                <InfoLine label="Candles" value={`${iqCandles.length} candles`} />
                <InfoLine label="Modo da fonte" value={formatSourceMode(iqSourceMode)} />
                <InfoLine label="Entrega" value={`${formatDeliveryTitle(iqDeliveryState)} - ${formatDeliveryDetail(iqDeliveryState, deliverySummary.averageLabel)}`} />
                <InfoLine label="Última resposta" value={formatLastResponse(iqLastUpdateAt)} />
                <InfoLine label="Último movimento" value={movementSummary.lastMovementLabel} />
                <InfoLine label="Movimentos" value={movementSummary.rateLabel} />
                <InfoLine label="Feed" value={formatFeedStatus(feedState, iqLastUpdateAt, iqLoading)} />
              </CompactPanel>

              <CompactPanel title="Readiness DEV">
                <div className="flex items-center justify-between gap-3">
                  <StatusBadge status={readiness.status} tone={readiness.status === 'READY' ? 'success' : readiness.status === 'PARTIAL' ? 'warning' : 'danger'} />
                  <span className="text-xs font-bold text-slate-400">{readiness.reason}</span>
                </div>
                <div className="mt-2 grid gap-1.5">
                  <CheckItem label="Fonte read-only conectada" ok={Boolean(iqSymbol) && !iqError} />
                  <CheckItem label="Ativo selecionado" ok={Boolean(iqSymbol)} />
                  <CheckItem label="Timeframe selecionado" ok={Boolean(iqRawSize)} />
                  <CheckItem label="Candles disponíveis" ok={iqCandles.length > 0} />
                  <CheckItem label="Quantidade mínima" ok={iqCandles.length >= MIN_ANALYSIS_CANDLES} />
                  <CheckItem label="Última atualização" ok={Boolean(latest)} />
                </div>
              </CompactPanel>
            </>
          )}

          {iqError && (
            <CompactPanel title="Erro">
              <p className="text-xs text-red-200">{iqError}</p>
              <button
                type="button"
                onClick={() => setIqAssetRetryKey((current) => current + 1)}
                className="mt-2 h-8 rounded-lg border border-cyan-300/30 px-3 text-xs font-black text-cyan-100 hover:border-cyan-200"
              >
                Tentar novamente
              </button>
            </CompactPanel>
          )}
        </aside>
      </section>
    </PageContainer>
  );
}

function Control({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</span>
      {children}
    </label>
  );
}

function FridayStrategyEnginePanel({
  strategies,
  selectedStrategy,
  selectedStrategyId,
  onSelectStrategy
}: {
  strategies: FridayStrategyDefinition[];
  selectedStrategy: FridayStrategyDefinition | null;
  selectedStrategyId: string;
  onSelectStrategy: (strategyId: string) => void;
}) {
  const confluenceCount = selectedStrategy?.confluences.length ?? 0;
  const confluenceLabel = selectedStrategy ? `${confluenceCount} avaliadas` : '0 avaliadas';
  return (
    <section className="rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.035] p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-cyan-200/70">FRIDAY STRATEGY</p>
          <h2 className="mt-1 text-lg font-black text-white">{selectedStrategy?.name ?? 'Nenhuma estratégia carregada'}</h2>
          <p className="mt-1 text-xs font-bold leading-relaxed text-slate-400">
            Selecione uma estratégia para iniciar a leitura do mercado.
          </p>
        </div>
        <span className="rounded-full border border-amber-300/30 px-3 py-1 text-[10px] font-black uppercase tracking-widest text-amber-200">
          Neutro
        </span>
      </div>

      <label className="mt-3 block">
        <span className="mb-1 block text-[10px] font-black uppercase tracking-widest text-slate-500">Estratégia</span>
        <select
          value={selectedStrategyId}
          onChange={(event) => onSelectStrategy(event.target.value)}
          className="h-9 w-full rounded-xl border border-white/10 bg-[#080a2a] px-3 text-sm font-black text-white outline-none focus:border-cyan-300/60"
          disabled={!strategies.length}
        >
          <option value="">Nenhuma selecionada</option>
          {strategies.map((strategy) => (
            <option key={strategy.id} value={strategy.id}>
              {strategy.name}
            </option>
          ))}
        </select>
      </label>

      <div className="mt-3 grid gap-2">
        <InfoLine label="Estratégia ativa" value={selectedStrategy?.name ?? 'Nenhuma selecionada'} />
        <InfoLine label="Status" value={selectedStrategy ? formatStrategyStatus(selectedStrategy.status) : 'Aguardando configuração'} />
        <InfoLine label="Confluências" value={confluenceLabel} />
        <InfoLine label="Decisão" value="Nenhuma análise ativa" />
        {selectedStrategy && (
          <>
            <InfoLine label="Readiness" value={formatStrategyReadiness(selectedStrategy.readiness)} />
            <InfoLine label="Mercados suportados" value={selectedStrategy.supportedMarkets.join(', ')} />
            <InfoLine label="Timeframes suportados" value={selectedStrategy.supportedTimeframes.map(formatRawSize).join(', ')} />
          </>
        )}
      </div>

      <p className="mt-3 rounded-xl border border-white/10 bg-white/[0.025] px-3 py-2 text-xs font-bold text-slate-400">
        Nenhuma análise ativa. Nenhum cálculo operacional, estatística ou decisão é gerado nesta fundação.
      </p>
    </section>
  );
}

function MarketHealthBadge({ status }: { status: OperatorMarketStatus }) {
  const toneClass = status.tone === 'success' ? 'border-emerald-300/25 text-emerald-200' : status.tone === 'warning' ? 'border-amber-300/25 text-amber-200' : 'border-red-300/25 text-red-200';
  return (
    <div className={`rounded-xl border px-3 py-2 text-xs font-black uppercase tracking-wide ${toneClass}`}>
      {status.label}
    </div>
  );
}

function MarketNotice({ status }: { status: OperatorMarketStatus }) {
  if (!status.notice) return null;
  return (
    <section className="rounded-2xl border border-amber-300/20 bg-amber-300/[0.04] px-3 py-2">
      <p className="text-sm font-black text-amber-100">{status.notice.title}</p>
      <p className="mt-0.5 text-xs font-bold text-amber-100/75">{status.notice.description}</p>
    </section>
  );
}

function CompactPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <p className="mb-2 text-[10px] font-black uppercase tracking-widest text-slate-500">{title}</p>
      {children}
    </section>
  );
}

function DiagnosticsPanel({
  deliveryState,
  sourceMode,
  stats,
  summary,
  feedState,
  lastUpdateAt,
  nowTick,
  expanded,
  onToggle
}: {
  deliveryState: IQDeliveryState;
  sourceMode: IQSourceMode;
  stats: IQPushStats;
  summary: ReturnType<typeof getDeliverySummary>;
  feedState: IqFeedState;
  lastUpdateAt: string | null;
  nowTick: number;
  expanded: boolean;
  onToggle: () => void;
}) {
  const deliveryTitle = formatDeliveryTitle(deliveryState);
  const qualityTitle = formatSourceShort(sourceMode);
  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-3 text-left [hyphens:none] [overflow-wrap:normal] [word-break:normal]"
      >
        <span>
          <span className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Diagnóstico DEV</span>
          <span className="mt-1 block whitespace-normal text-xs font-black leading-snug text-white">
            {deliveryTitle} • {qualityTitle} • {stats.fallbacks} fallbacks
          </span>
        </span>
        <span className="shrink-0 rounded-lg border border-white/10 px-2 py-1 text-[10px] font-black uppercase tracking-widest text-cyan-100">
          {expanded ? 'Recolher' : 'Expandir'}
        </span>
      </button>

      {expanded && (
        <div className="mt-3 grid grid-cols-1 gap-2 min-[420px]:grid-cols-2">
          <InfoLine label="Fonte IQ" value="Candle Stream" />
          <InfoLine label="Entrega" value={formatDeliveryTitle(deliveryState)} />
          <InfoLine label="Status" value={formatDeliveryDetail(deliveryState, summary.averageLabel)} />
          <InfoLine label="Qualidade" value={formatSourceMode(sourceMode)} />
          <InfoLine label="Eventos de candle" value={String(stats.eventsReceived)} />
          <InfoLine label="Atualizações do gráfico" value={String(stats.chartUpdates)} />
          <InfoLine label="Eventos coalescidos" value={String(stats.eventsCoalesced)} />
          <InfoLine label="Último evento" value={formatElapsed(stats.lastEventAt, nowTick)} />
          <InfoLine label="Última aplicação" value={formatElapsed(stats.lastAppliedAt, nowTick)} />
          <InfoLine label="Última resposta" value={formatLastResponse(lastUpdateAt)} />
          <InfoLine label="Próxima vela" value={formatFeedCountdown(feedState)} />
          <InfoLine label="Latência local média" value={summary.averageLabel} />
          <InfoLine label="Latência local p95" value={summary.p95Label} />
          <InfoLine label="Sequência" value={String(stats.sequence)} />
          <InfoLine label="Reconexões" value={String(stats.reconnects)} />
          <InfoLine label="Fallbacks" value={String(stats.fallbacks)} />
          <InfoLine label="Heartbeat" value={summary.lastEventLabel} />
        </div>
      )}
    </section>
  );
}

function InfoLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-0.5 whitespace-normal text-xs font-black leading-snug text-white [hyphens:none] [overflow-wrap:normal] [word-break:normal]">{value}</p>
    </div>
  );
}

function CheckItem({ label, ok }: { label: string; ok: boolean }) {
  const Icon = ok ? CheckCircle2 : CircleDashed;
  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-white/[0.025] px-2.5 py-1.5">
      <span className="text-xs font-bold text-slate-300">{label}</span>
      <Icon size={15} className={ok ? 'text-emerald-300' : 'text-amber-300'} />
    </div>
  );
}

function IqEmptyChart({ loading, error, marketType, onRetry }: { loading: boolean; error: string | null; marketType: IQMarketType; onRetry: () => void }) {
  const idleMessage = marketType === 'REGULAR' ? 'Mercado regular fechado no momento.' : 'Carregando ativos OTC...';
  return (
    <div className="flex h-[calc(100dvh-218px)] min-h-[420px] max-h-[700px] items-center justify-center rounded-2xl border border-cyan-400/15 bg-[#070920] px-6 text-center">
      <div>
        <p className="text-sm font-black text-white">
          {loading ? 'Conectando à fonte IQ Option...' : error ? 'Não foi possível carregar os ativos IQ Option.' : idleMessage}
        </p>
        <p className="mt-2 max-w-xl text-xs leading-relaxed text-slate-400">
          {marketType === 'REGULAR' && !loading && !error
            ? 'Os ativos OTC continuam disponíveis no seletor de mercado.'
            : 'O gráfico principal usa somente IQ Option em modo read-only.'}
        </p>
        {error && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 h-9 rounded-lg border border-cyan-300/30 px-4 text-xs font-black text-cyan-100 hover:border-cyan-200"
          >
            Tentar novamente
          </button>
        )}
      </div>
    </div>
  );
}

async function ensureIqOptionConnected(promiseRef: { current: Promise<void> | null }) {
  if (promiseRef.current) {
    return promiseRef.current;
  }
  promiseRef.current = (async () => {
    logIqFlow('status_request_started');
    const status = (await fetchJsonWithTimeout(`${API_BASE_URL}/market/providers/iq-option/status`, {
      timeoutMs: IQ_STATUS_TIMEOUT_MS,
      errorMessage: 'IQ Option status'
    })) as IQProviderStatus;
    logIqFlow('status_request_finished', { connected: Boolean(status.connected) });
    logIqFlow('connect_started', { alreadyConnected: Boolean(status.connected) });
    await fetchJsonWithTimeout(`${API_BASE_URL}/market/providers/iq-option/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
      timeoutMs: IQ_CONNECT_TIMEOUT_MS,
      errorMessage: 'IQ Option connect'
    });
    logIqFlow('connect_finished');
  })();
  try {
    await promiseRef.current;
  } finally {
    promiseRef.current = null;
  }
}

export function parseIqAssetsResponse(payload: unknown): IQAsset[] {
  const record = asRecord(payload);
  const nestedData = asRecord(record?.data);
  const rawAssets = Array.isArray(record?.assets) ? record.assets : Array.isArray(nestedData?.assets) ? nestedData.assets : [];
  return rawAssets
    .filter((asset): asset is Record<string, unknown> => Boolean(asRecord(asset)))
    .map((asset) => ({
      symbol: String(asset.symbol ?? ''),
      display_name: typeof asset.display_name === 'string' ? asset.display_name : formatIqSymbol(String(asset.symbol ?? '')),
      is_open: Boolean(asset.is_open)
    }))
    .filter((asset) => asset.symbol && asset.is_open);
}

export function parseIqCandlesResponse(payload: unknown): { count: number; candles: RealChartCandle[] } {
  const record = asRecord(payload);
  const chart = asRecord(record?.chart);
  const rawCandles = Array.isArray(chart?.candles) ? chart.candles : Array.isArray(record?.candles) ? record.candles : [];
  const countValue = Number(chart?.count ?? rawCandles.length);
  const candles = rawCandles
    .filter((candle): candle is Record<string, unknown> => Boolean(asRecord(candle)))
    .map((candle) => ({
      time: Number(candle.time),
      open: Number(candle.open),
      high: Number(candle.high),
      low: Number(candle.low),
      close: Number(candle.close)
    }))
    .filter((candle) => [candle.time, candle.open, candle.high, candle.low, candle.close].every(Number.isFinite));
  return { count: Number.isFinite(countValue) ? countValue : candles.length, candles };
}

export function parseIqSourceMode(payload: unknown): IQSourceMode {
  const record = asRecord(payload);
  const sourceMode = record?.source_mode;
  if (sourceMode === 'NEAR_REALTIME' || sourceMode === 'SNAPSHOT' || sourceMode === 'STALE' || sourceMode === 'NO_DATA') {
    return sourceMode;
  }
  return 'CHECKING';
}

export function parseIqRealtimeStreamEvent(message: MessageEvent): IQRealtimeStreamEvent | null {
  try {
    const payload = asRecord(JSON.parse(String(message.data)));
    if (!payload) return null;
    const candleRecord = asRecord(payload.candle);
    const sourceMode = payload.source_mode === 'HEARTBEAT' ? 'HEARTBEAT' : parseIqSourceMode(payload);
    const eventType = payload.type === 'heartbeat' ? 'heartbeat' : 'candle';
    const event: IQRealtimeStreamEvent = {
      type: eventType,
      provider: String(payload.provider ?? ''),
      market_type: payload.market_type === 'REGULAR' ? 'REGULAR' : 'OTC',
      symbol: String(payload.symbol ?? ''),
      raw_size: Number(payload.raw_size),
      source_mode: sourceMode,
      sequence: Number(payload.sequence),
      worker_received_at: typeof payload.worker_received_at === 'number' ? payload.worker_received_at : null,
      backend_published_at: typeof payload.backend_published_at === 'number' ? payload.backend_published_at : null
    };
    if (candleRecord) {
      event.candle = {
        time: Number(candleRecord.time ?? candleRecord.timestamp),
        open: Number(candleRecord.open),
        high: Number(candleRecord.high),
        low: Number(candleRecord.low),
        close: Number(candleRecord.close)
      };
      if (![event.candle.time, event.candle.open, event.candle.high, event.candle.low, event.candle.close].every(Number.isFinite)) {
        return null;
      }
    }
    if (!event.provider || !event.symbol || !Number.isFinite(event.raw_size) || !Number.isFinite(event.sequence)) {
      return null;
    }
    return event;
  } catch {
    return null;
  }
}

function matchesIqRealtimeContext(event: IQRealtimeStreamEvent, symbol: string, rawSize: number, marketType: IQMarketType) {
  return event.provider === 'IQ_OPTION' && event.symbol === symbol && event.raw_size === rawSize && event.market_type === marketType;
}

export function chooseIqSymbol(currentSymbol: string, assets: IQAsset[], marketType: IQMarketType) {
  if (currentSymbol && assets.some((asset) => asset.symbol === currentSymbol && asset.is_open)) {
    return currentSymbol;
  }
  const preferredSymbol = marketType === 'OTC' ? 'EURUSD-OTC' : 'EURUSD';
  const preferred = assets.find((asset) => asset.symbol === preferredSymbol && asset.is_open);
  return preferred?.symbol ?? assets.find((asset) => asset.is_open)?.symbol ?? '';
}

function fallbackIqSymbolAfterAssetsFailure(currentSymbol: string, marketType: IQMarketType) {
  if (currentSymbol) return currentSymbol;
  return marketType === 'OTC' ? 'EURUSD-OTC' : 'EURUSD';
}

function isRetryableIqAssetError(error: unknown) {
  if (error instanceof IqHttpError) {
    return [502, 503, 504].includes(error.status);
  }
  const message = error instanceof Error ? error.message : String(error);
  return ['PROVIDER_CONNECTION_FAILED', 'WORKER_TIMEOUT', 'IQ_OPTION_WORKER_TIMEOUT'].some((code) => message.includes(code));
}

function abortableDelay(delayMs: number, signal: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    const timeoutId = window.setTimeout(resolve, delayMs);
    signal.addEventListener(
      'abort',
      () => {
        window.clearTimeout(timeoutId);
        reject(new DOMException('Aborted', 'AbortError'));
      },
      { once: true }
    );
  });
}

async function fetchJsonWithTimeout(
  url: string,
  options: RequestInit & { timeoutMs: number; errorMessage: string }
): Promise<Record<string, unknown>> {
  const { timeoutMs, errorMessage, signal, ...fetchOptions } = options;
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
  const abortFromParent = () => controller.abort();
  signal?.addEventListener('abort', abortFromParent, { once: true });
  try {
    const response = await fetch(url, { ...fetchOptions, signal: controller.signal });
    if (!response.ok) {
      throw new IqHttpError(response.status, `${errorMessage} returned ${response.status}`);
    }
    const payload = await response.json();
    return asRecord(payload) ?? {};
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError' && !signal?.aborted) {
      throw new IqHttpError(408, `${errorMessage} timeout`);
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
    signal?.removeEventListener('abort', abortFromParent);
  }
}

class IqHttpError extends Error {
  constructor(
    readonly status: number,
    message: string
  ) {
    super(message);
  }
}

function mergeIqOptionCandles(previousCandles: RealChartCandle[], nextCandles: RealChartCandle[]) {
  const sortedNext = [...nextCandles].sort((left, right) => left.time - right.time);
  const windowStart = previousCandles[0]?.time ?? null;
  const contextCandles = windowStart === null ? sortedNext : sortedNext.filter((candle) => candle.time >= windowStart);
  if (!contextCandles.length) {
    return previousCandles;
  }
  if (!isCompatibleIqOptionPriceContext(previousCandles, contextCandles)) {
    return previousCandles;
  }
  return mergeCandlesByTime(previousCandles, contextCandles, IQ_BOOTSTRAP_LIMIT);
}

function emptyIqPushStats(): IQPushStats {
  return {
    eventsReceived: 0,
    chartUpdates: 0,
    eventsCoalesced: 0,
    lastEventAt: null,
    lastAppliedAt: null,
    sequence: 0,
    reconnects: 0,
    fallbacks: 0,
    deliverySamplesMs: []
  };
}

function appendDeliverySample(samples: number[], value: number | null) {
  if (value === null || !Number.isFinite(value) || value < 0) {
    return samples;
  }
  return [...samples.slice(-99), value];
}

function deliveryMsForEvent(event: IQRealtimeStreamEvent, appliedAt: number) {
  if (typeof event.backend_published_at !== 'number') {
    return null;
  }
  return appliedAt - event.backend_published_at;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function sanitizeIqError(error: unknown) {
  if (error instanceof IqHttpError) return `HTTP_${error.status}`;
  if (error instanceof DOMException) return error.name;
  return error instanceof Error ? error.name : 'UNKNOWN_ERROR';
}

function logIqFlow(event: string, metadata: Record<string, unknown> = {}) {
  if (!import.meta.env.DEV) return;
  const target = window as unknown as { __IQ_FLOW_EVENTS__?: Array<{ event: string; metadata: Record<string, unknown> }> };
  target.__IQ_FLOW_EVENTS__ = [...(target.__IQ_FLOW_EVENTS__ ?? []), { event, metadata }].slice(-100);
  console.info('[IQ_FLOW]', event, metadata);
}

function isCompatibleIqOptionPriceContext(previousCandles: RealChartCandle[], nextCandles: RealChartCandle[]) {
  if (previousCandles.length < 12 || !nextCandles.length) {
    return true;
  }
  const recentCandles = previousCandles.slice(-60);
  const recentCloses = recentCandles.map((candle) => candle.close).filter(Number.isFinite);
  const recentRanges = recentCandles.map((candle) => Math.abs(candle.high - candle.low)).filter(Number.isFinite);
  const baselineClose = medianNumber(recentCloses);
  if (!baselineClose || baselineClose <= 0) {
    return true;
  }
  const baselineRange = medianNumber(recentRanges) ?? 0;
  const maxAllowedGap = Math.max(baselineClose * 0.05, baselineRange * 40);
  return nextCandles.every((candle) => Math.abs(candle.close - baselineClose) <= maxAllowedGap);
}

function medianNumber(values: number[]) {
  if (!values.length) return null;
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) return sorted[middle];
  return (sorted[middle - 1] + sorted[middle]) / 2;
}

function formatIqSymbol(symbol: string) {
  if (!symbol) return 'Ativo não identificado';
  const isOtc = symbol.endsWith('-OTC') || symbol.includes('-OTC-');
  const base = symbol.replace('-OTC', '').replace('-op', '');
  if (isCurrencyPairSymbol(base)) {
    return `${base.slice(0, 3)}/${base.slice(3)}${symbol.endsWith('-OTC') ? ' OTC' : ''}`;
  }
  return `${base.replace('-', ' ')}${isOtc && !base.endsWith('OTC') ? ' OTC' : ''}`;
}

function isCurrencyPairSymbol(symbol: string) {
  if (symbol.length !== 6) return false;
  const currencyCodes = new Set(['AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'JPY', 'NZD', 'USD']);
  return currencyCodes.has(symbol.slice(0, 3)) && currencyCodes.has(symbol.slice(3));
}

function getReadiness({
  sourceOnline,
  rawSize,
  candleCount,
  latestTime,
  feedState,
  sourceMode
}: {
  sourceOnline: boolean;
  rawSize: number | null;
  candleCount: number;
  latestTime: number | null;
  feedState: IqFeedStatus;
  sourceMode: IQSourceMode;
}) {
  if (!sourceOnline || !rawSize) {
    return { status: 'BLOCKED' as const, reason: 'Fonte ou série ausente' };
  }
  if (feedState === 'STALE' || sourceMode === 'STALE') {
    return { status: 'BLOCKED' as const, reason: 'Dados atrasados' };
  }
  if (sourceMode === 'NO_DATA' || sourceMode === 'CHECKING') {
    return { status: 'BLOCKED' as const, reason: 'Feed em verificação' };
  }
  if (sourceMode === 'SNAPSHOT') {
    return { status: 'PARTIAL' as const, reason: 'Feed limitado por snapshot' };
  }
  if (candleCount >= MIN_ANALYSIS_CANDLES && latestTime) {
    return { status: 'READY' as const, reason: 'Base mínima atingida' };
  }
  return { status: 'PARTIAL' as const, reason: 'Aguardando candles suficientes' };
}

type IqFeedStatus = 'LIVE' | 'QUIET' | 'STALE' | 'NO_DATA';
type OperatorMarketStatus = {
  label: 'MERCADO ATIVO' | 'MERCADO LENTO' | 'DADOS LIMITADOS' | 'DADOS ATRASADOS' | 'SEM DADOS' | 'VERIFICANDO MERCADO';
  tone: 'success' | 'warning' | 'danger';
  notice: { title: string; description: string } | null;
};

type IqFeedState = {
  status: IqFeedStatus;
  ageSeconds: number | null;
  secondsRemaining: number | null;
};

function getIqFeedState(latestTime: number | null, rawSize: number | null, nowMs: number): IqFeedState {
  if (!latestTime || !rawSize) {
    return { status: 'NO_DATA', ageSeconds: null, secondsRemaining: null };
  }
  const nowSeconds = Math.floor(nowMs / 1000);
  const ageSeconds = Math.max(0, nowSeconds - latestTime);
  const staleAfterSeconds = rawSize * 3;
  if (ageSeconds > staleAfterSeconds) {
    return { status: 'STALE', ageSeconds, secondsRemaining: null };
  }
  const secondsRemaining = rawSize - (nowSeconds % rawSize);
  return { status: ageSeconds <= rawSize ? 'LIVE' : 'QUIET', ageSeconds, secondsRemaining };
}

function getOperatorMarketStatus(sourceMode: IQSourceMode, feedState: IqFeedState, loading: boolean, candleCount: number): OperatorMarketStatus {
  if (loading || sourceMode === 'CHECKING') {
    return { label: 'VERIFICANDO MERCADO', tone: 'warning', notice: null };
  }
  if (candleCount <= 0 || sourceMode === 'NO_DATA' || feedState.status === 'NO_DATA') {
    return {
      label: 'SEM DADOS',
      tone: 'danger',
      notice: { title: 'Análise indisponível', description: 'Não há candles disponíveis.' }
    };
  }
  if (sourceMode === 'STALE' || feedState.status === 'STALE') {
    return {
      label: 'DADOS ATRASADOS',
      tone: 'danger',
      notice: { title: 'Análise indisponível', description: 'Os dados deste ativo estão atrasados.' }
    };
  }
  if (sourceMode === 'SNAPSHOT') {
    return {
      label: 'DADOS LIMITADOS',
      tone: 'warning',
      notice: { title: 'Dados limitados', description: 'Evite decisões que dependem de resposta instantânea.' }
    };
  }
  if (feedState.status === 'QUIET') {
    return { label: 'MERCADO LENTO', tone: 'warning', notice: null };
  }
  return { label: 'MERCADO ATIVO', tone: 'success', notice: null };
}

function formatFeedStatus(feedState: IqFeedState, lastUpdateAt: string | null, loading: boolean) {
  if (feedState.status === 'NO_DATA') {
    return loading ? 'Carregando' : 'Sem dados';
  }
  if (feedState.status === 'STALE') {
    return `Dados atrasados ${formatDuration(feedState.ageSeconds ?? 0)}`;
  }
  const countdown = feedState.secondsRemaining !== null ? `proxima vela ${formatCountdown(feedState.secondsRemaining)}` : 'aguardando vela';
  if (!lastUpdateAt) {
    return countdown;
  }
  return `${countdown} · resp. ${formatDateTime(lastUpdateAt)}`;
}

function formatStrategyStatus(status: FridayStrategyStatus) {
  if (status === 'LOADED') return 'Estratégia carregada';
  if (status === 'DISABLED') return 'Estratégia desativada';
  return 'Aguardando configuração';
}

function formatStrategyReadiness(readiness: FridayStrategyReadiness) {
  if (readiness === 'READY') return 'Pronto';
  if (readiness === 'BLOCKED') return 'Bloqueado';
  return 'Inativo';
}

function formatFeedCountdown(feedState: IqFeedState) {
  if (feedState.status === 'STALE') return `Atraso: ${formatDuration(feedState.ageSeconds ?? 0)}`;
  if (feedState.secondsRemaining === null) return 'Aguardando vela';
  return formatCountdown(feedState.secondsRemaining);
}

function formatLastResponse(lastUpdateAt: string | null) {
  return lastUpdateAt ? formatDateTime(lastUpdateAt) : 'Pendente';
}

function formatSourceMode(sourceMode: IQSourceMode) {
  if (sourceMode === 'NEAR_REALTIME') return 'PRÓXIMO DO TEMPO REAL';
  if (sourceMode === 'SNAPSHOT') return 'SNAPSHOT';
  if (sourceMode === 'STALE') return 'DADOS ATRASADOS';
  if (sourceMode === 'NO_DATA') return 'SEM DADOS';
  return 'VERIFICANDO';
}

function formatSourceShort(sourceMode: IQSourceMode) {
  if (sourceMode === 'NEAR_REALTIME') return 'GOOD';
  if (sourceMode === 'SNAPSHOT') return 'SNAPSHOT';
  if (sourceMode === 'STALE') return 'STALE';
  if (sourceMode === 'NO_DATA') return 'NO DATA';
  return 'CHECKING';
}

function formatSourceDetail(sourceMode: IQSourceMode) {
  if (sourceMode === 'NEAR_REALTIME') return 'Fluxo saudável';
  if (sourceMode === 'SNAPSHOT') return 'Atualização limitada';
  if (sourceMode === 'STALE') return 'Dados atrasados';
  if (sourceMode === 'NO_DATA') return 'Sem leitura';
  return 'Aguardando leitura';
}

function formatDeliveryTitle(deliveryState: IQDeliveryState) {
  if (deliveryState === 'SSE') return 'SSE';
  if (deliveryState === 'POLLING_FALLBACK') return 'POLLING 1s';
  if (deliveryState === 'RECONNECTING') return 'RECONECTANDO';
  if (deliveryState === 'DISCONNECTED') return 'DESCONECTADO';
  return 'CONECTANDO';
}

function formatDeliveryDetail(deliveryState: IQDeliveryState, averageLabel: string) {
  if (deliveryState === 'SSE') return averageLabel === 'Não disponível' ? 'Push em tempo real' : `Latência local ${averageLabel}`;
  if (deliveryState === 'POLLING_FALLBACK') return 'Polling de segurança';
  if (deliveryState === 'RECONNECTING') return 'Aguardando heartbeat';
  if (deliveryState === 'DISCONNECTED') return 'Canal fechado';
  return 'Abrindo EventSource';
}

function getDeliverySummary(stats: IQPushStats, nowMs: number) {
  const samples = stats.deliverySamplesMs.filter((value) => Number.isFinite(value) && value >= 0);
  if (!samples.length) {
    return {
      averageLabel: 'Não disponível',
      p50Label: 'Não disponível',
      p95Label: 'Não disponível',
      maxLabel: 'Não disponível',
      above250: 0,
      above500: 0,
      above1000: 0,
      lastEventLabel: formatElapsed(stats.lastEventAt, nowMs),
      lastAppliedLabel: formatElapsed(stats.lastAppliedAt, nowMs)
    };
  }
  const sorted = [...samples].sort((left, right) => left - right);
  const average = samples.reduce((total, value) => total + value, 0) / samples.length;
  return {
    averageLabel: formatMilliseconds(average),
    p50Label: formatMilliseconds(percentile(sorted, 0.5)),
    p95Label: formatMilliseconds(percentile(sorted, 0.95)),
    maxLabel: formatMilliseconds(sorted[sorted.length - 1]),
    above250: samples.filter((value) => value > 250).length,
    above500: samples.filter((value) => value > 500).length,
    above1000: samples.filter((value) => value > 1000).length,
    lastEventLabel: formatElapsed(stats.lastEventAt, nowMs),
    lastAppliedLabel: formatElapsed(stats.lastAppliedAt, nowMs)
  };
}

function getMovementSummary(lastMovementAt: number | null, intervals: number[], nowMs: number) {
  if (lastMovementAt === null) {
    return { lastMovementLabel: 'Aguardando movimento', rateLabel: 'Sem movimentos' };
  }
  const ageSeconds = Math.max(0, (nowMs - lastMovementAt) / 1000);
  if (!intervals.length) {
    return { lastMovementLabel: `há ${formatDecimalSeconds(ageSeconds)}`, rateLabel: 'Calculando' };
  }
  const averageInterval = intervals.reduce((total, value) => total + value, 0) / intervals.length;
  const rate = averageInterval > 0 ? 1000 / averageInterval : 0;
  return {
    lastMovementLabel: `há ${formatDecimalSeconds(ageSeconds)}`,
    rateLabel: `${formatMovementRate(rate)}/s`
  };
}

function formatElapsed(timestampMs: number | null, nowMs: number) {
  if (timestampMs === null) return 'Não disponível';
  const elapsedSeconds = Math.max(0, (nowMs - timestampMs) / 1000);
  return `há ${formatDecimalSeconds(elapsedSeconds)}`;
}

function formatMilliseconds(value: number) {
  if (!Number.isFinite(value)) return 'Não disponível';
  if (value < 1000) return `${Math.round(value)}ms`;
  return `${(value / 1000).toFixed(1).replace('.', ',')}s`;
}

function percentile(sortedValues: number[], ratio: number) {
  if (!sortedValues.length) return 0;
  const index = Math.min(sortedValues.length - 1, Math.ceil(sortedValues.length * ratio) - 1);
  return sortedValues[index];
}

function formatDecimalSeconds(value: number) {
  if (value < 10) return `${value.toFixed(1).replace('.', ',')}s`;
  return `${Math.round(value)}s`;
}

function formatMovementRate(value: number) {
  if (!Number.isFinite(value) || value <= 0) return '0';
  if (value < 10) return value.toFixed(1).replace('.', ',');
  return String(Math.round(value));
}

function formatCountdown(seconds: number) {
  const safeSeconds = Math.max(0, seconds);
  const minutes = Math.floor(safeSeconds / 60);
  const rest = safeSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`;
}

function formatDuration(seconds: number) {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}min`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h`;
}

function formatPrice(value: number) {
  return value.toFixed(value > 10 ? 2 : 5);
}

function formatCandleTime(value: number) {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'medium' }).format(new Date(value * 1000));
}

function formatDateTime(value: string) {
  try {
    return new Intl.DateTimeFormat('pt-BR', { timeStyle: 'medium' }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatRawSize(rawSize: number): string {
  if (rawSize === 60) return 'M1';
  if (rawSize === 300) return 'M5';
  if (rawSize === 900) return 'M15';
  return `${rawSize}s`;
}

function readStoredMarketType(): IQMarketType {
  return localStorage.getItem(IQ_MARKET_STORAGE_KEY) === 'REGULAR' ? 'REGULAR' : 'OTC';
}

function readStoredFridayUiMode(): FridayUiMode {
  return localStorage.getItem(FRIDAY_UI_MODE_STORAGE_KEY) === 'DEVELOPER' ? 'DEVELOPER' : 'OPERATOR';
}

function readStoredRawSize(): number {
  const value = Number(localStorage.getItem(IQ_TIMEFRAME_STORAGE_KEY));
  return IQ_TIMEFRAMES.includes(value) ? value : 60;
}
