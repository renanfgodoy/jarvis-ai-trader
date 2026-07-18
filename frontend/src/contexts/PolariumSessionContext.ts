import type { RealChartCandle } from '../components/chart/RealCandleChart';

export const POLARIUM_SESSION_UPDATED = 'POLARIUM_SESSION_UPDATED';
export const UNKNOWN_POLARIUM_ASSET_LABEL = 'ATIVO NÃO IDENTIFICADO';

export type PolariumSessionContext = {
  provider: 'POLARIUM';
  websocketState: string;
  authenticated: boolean;
  connectionStatus: string;
  activeId: number | null;
  symbol: string | null;
  displayName: string;
  marketType: string;
  rawSize: number | null;
  timeframe: string | null;
  visibleActiveId: number | null;
  visibleSymbol: string | null;
  visibleDisplayName: string;
  visibleMarketType: string;
  visibleRawSize: number | null;
  visibleTimeframe: string | null;
  latestMarketEventActiveId: number | null;
  latestMarketEventRawSizes: number[];
  availableRawSizes: number[];
  backgroundMarketContexts: Array<{ active_id: number; raw_sizes: number[] }>;
  latestPrice: number | null;
  feedStatus: string;
  historyState: string;
  historyCount: number;
  historyRequired: number;
  historyProgress: number;
  bootstrapComplete: boolean;
  lastUpdate: number | null;
  analysisBlocked: boolean;
  analysisBlockReason: string | null;
  candles: RealChartCandle[];
};

export type RawPolariumSessionContext = {
  provider?: string;
  websocket_state?: string;
  authenticated?: boolean;
  connection_status?: string;
  active_id?: number | null;
  symbol?: string | null;
  display_name?: string | null;
  market_type?: string | null;
  raw_size?: number | null;
  timeframe?: string | null;
  visible_active_id?: number | null;
  visible_symbol?: string | null;
  visible_display_name?: string | null;
  visible_market_type?: string | null;
  visible_raw_size?: number | null;
  visible_timeframe?: string | null;
  latest_market_event_active_id?: number | null;
  latest_market_event_raw_sizes?: number[];
  available_raw_sizes?: number[];
  background_market_contexts?: Array<{ active_id?: number; raw_sizes?: number[] }>;
  latest_price?: number | null;
  feed_status?: string | null;
  history_state?: string | null;
  history_count?: number;
  history_required?: number;
  history_progress?: number;
  bootstrap_complete?: boolean;
  last_update?: number | null;
  analysis_blocked?: boolean;
  analysis_block_reason?: string | null;
};

export function disconnectedPolariumSessionContext(candles: RealChartCandle[] = []): PolariumSessionContext {
  return {
    provider: 'POLARIUM',
    websocketState: 'DISCONNECTED',
    authenticated: false,
    connectionStatus: 'OFFLINE',
    activeId: null,
    symbol: null,
    displayName: 'Não disponível',
    marketType: 'POLARIUM_AUTHORIZED_MARKET',
    rawSize: null,
    timeframe: null,
    visibleActiveId: null,
    visibleSymbol: null,
    visibleDisplayName: 'Não disponível',
    visibleMarketType: 'POLARIUM_AUTHORIZED_MARKET',
    visibleRawSize: null,
    visibleTimeframe: null,
    latestMarketEventActiveId: null,
    latestMarketEventRawSizes: [],
    availableRawSizes: [],
    backgroundMarketContexts: [],
    latestPrice: null,
    feedStatus: 'OFFLINE',
    historyState: 'NO_HISTORY',
    historyCount: 0,
    historyRequired: 0,
    historyProgress: 0,
    bootstrapComplete: false,
    lastUpdate: null,
    analysisBlocked: true,
    analysisBlockReason: 'POLARIUM_SESSION_OFFLINE',
    candles
  };
}

export function normalizePolariumSessionContext(raw: RawPolariumSessionContext | null | undefined, candles: RealChartCandle[]): PolariumSessionContext {
  if (!raw) return disconnectedPolariumSessionContext(candles);
  const activeId = typeof raw.active_id === 'number' ? raw.active_id : null;
  const symbol = typeof raw.symbol === 'string' && raw.symbol.trim() ? raw.symbol : null;
  const visibleActiveId = typeof raw.visible_active_id === 'number' ? raw.visible_active_id : activeId;
  const visibleSymbol = typeof raw.visible_symbol === 'string' && raw.visible_symbol.trim() ? raw.visible_symbol : symbol;
  const displayName =
    typeof raw.display_name === 'string' && raw.display_name.trim()
      ? raw.display_name
      : activeId !== null
        ? UNKNOWN_POLARIUM_ASSET_LABEL
        : 'Não disponível';
  return {
    provider: 'POLARIUM',
    websocketState: typeof raw.websocket_state === 'string' ? raw.websocket_state : 'DISCONNECTED',
    authenticated: Boolean(raw.authenticated),
    connectionStatus: typeof raw.connection_status === 'string' ? raw.connection_status : 'OFFLINE',
    activeId,
    symbol,
    displayName,
    marketType: typeof raw.market_type === 'string' && raw.market_type ? raw.market_type : 'POLARIUM_AUTHORIZED_MARKET',
    rawSize: typeof raw.raw_size === 'number' ? raw.raw_size : null,
    timeframe: typeof raw.timeframe === 'string' ? raw.timeframe : null,
    visibleActiveId,
    visibleSymbol,
    visibleDisplayName:
      typeof raw.visible_display_name === 'string' && raw.visible_display_name.trim()
        ? raw.visible_display_name
        : visibleActiveId !== null
          ? UNKNOWN_POLARIUM_ASSET_LABEL
          : 'Não disponível',
    visibleMarketType: typeof raw.visible_market_type === 'string' && raw.visible_market_type ? raw.visible_market_type : 'POLARIUM_AUTHORIZED_MARKET',
    visibleRawSize: typeof raw.visible_raw_size === 'number' ? raw.visible_raw_size : null,
    visibleTimeframe: typeof raw.visible_timeframe === 'string' ? raw.visible_timeframe : null,
    latestMarketEventActiveId: typeof raw.latest_market_event_active_id === 'number' ? raw.latest_market_event_active_id : null,
    latestMarketEventRawSizes: Array.isArray(raw.latest_market_event_raw_sizes) ? raw.latest_market_event_raw_sizes.filter((value): value is number => typeof value === 'number') : [],
    availableRawSizes: Array.isArray(raw.available_raw_sizes) ? raw.available_raw_sizes.filter((value): value is number => typeof value === 'number') : [],
    backgroundMarketContexts: Array.isArray(raw.background_market_contexts)
      ? raw.background_market_contexts
          .filter((item): item is { active_id: number; raw_sizes: number[] } => typeof item.active_id === 'number' && Array.isArray(item.raw_sizes))
          .map((item) => ({ active_id: item.active_id, raw_sizes: item.raw_sizes.filter((value): value is number => typeof value === 'number') }))
      : [],
    latestPrice: typeof raw.latest_price === 'number' ? raw.latest_price : null,
    feedStatus: typeof raw.feed_status === 'string' ? raw.feed_status : 'OFFLINE',
    historyState: typeof raw.history_state === 'string' ? raw.history_state : 'NO_HISTORY',
    historyCount: typeof raw.history_count === 'number' ? raw.history_count : 0,
    historyRequired: typeof raw.history_required === 'number' ? raw.history_required : 0,
    historyProgress: typeof raw.history_progress === 'number' ? raw.history_progress : 0,
    bootstrapComplete: Boolean(raw.bootstrap_complete),
    lastUpdate: typeof raw.last_update === 'number' ? raw.last_update : null,
    analysisBlocked: raw.analysis_blocked ?? symbol === null,
    analysisBlockReason: typeof raw.analysis_block_reason === 'string' ? raw.analysis_block_reason : null,
    candles
  };
}

export function publishPolariumSessionUpdate(context: PolariumSessionContext) {
  window.dispatchEvent(new CustomEvent(POLARIUM_SESSION_UPDATED, { detail: context }));
}
