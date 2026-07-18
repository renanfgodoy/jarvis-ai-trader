import type { RealChartCandle } from '../components/chart/RealCandleChart';

export type ChartBindingTraceEvent =
  | 'SESSION_CONTEXT_RECEIVED'
  | 'ACTIVE_KEY_RESOLVED'
  | 'CHART_FETCH_START'
  | 'CHART_FETCH_SUCCESS'
  | 'CHART_FETCH_EMPTY'
  | 'CHART_FETCH_ERROR'
  | 'STALE_RESPONSE_IGNORED'
  | 'STALE_ACTIVE_KEY_RESPONSE_IGNORED'
  | 'CANDLES_NORMALIZED'
  | 'CANDLE_STATE_UPDATED'
  | 'SOURCE_SELECTED'
  | 'GRAPH_PROPS_UPDATED'
  | 'GRAPH_RENDERED'
  | 'GRAPH_EMPTY'
  | 'GRAPH_LOADING'
  | 'GRAPH_ERROR';

export type ChartBindingSelectedSource =
  | 'PROVIDER_V2'
  | 'POLARIUM_CHART_API'
  | 'POLARIUM_LIVE'
  | 'EMPTY'
  | 'LEGACY_IQ_BLOCKED'
  | 'UNKNOWN';

export type ChartBindingTraceRecord = {
  timestamp: string;
  event: ChartBindingTraceEvent;
  active_id?: number | null;
  raw_size?: number | null;
  symbol?: string | null;
  endpoint?: string | null;
  http_status?: number | null;
  response_count?: number | null;
  normalized_count?: number | null;
  state_count?: number | null;
  selected_source?: ChartBindingSelectedSource | null;
  provider?: string | null;
  active_key?: string | null;
  graph_prop_count?: number | null;
  first_candle_time?: number | null;
  last_candle_time?: number | null;
  request_sequence?: number | null;
  requested_active_id?: number | null;
  requested_raw_size?: number | null;
  response_active_id?: number | null;
  response_raw_size?: number | null;
  current_context_active_id?: number | null;
  current_context_raw_size?: number | null;
  response_applied?: boolean | null;
  response_ignored?: boolean | null;
  reason?: string | null;
};

export type ChartBindingTraceInput = Partial<Omit<ChartBindingTraceRecord, 'timestamp' | 'event'>>;

const TRACE_STORAGE_KEY = 'friday_chart_binding_trace';
const MAX_TRACE_RECORDS = 500;

declare global {
  interface Window {
    __FRIDAY_CHART_BINDING_TRACE__?: ChartBindingTraceRecord[];
    __FRIDAY_EXPORT_CHART_BINDING_TRACE__?: () => string;
  }
}

export function recordChartBindingTrace(event: ChartBindingTraceEvent, details: ChartBindingTraceInput = {}): void {
  if (!isDevelopmentBrowser()) return;
  installChartBindingTraceGlobals();

  const records = window.__FRIDAY_CHART_BINDING_TRACE__ ?? [];
  const nextRecord: ChartBindingTraceRecord = {
    timestamp: new Date().toISOString(),
    event,
    ...sanitizeTraceInput(details)
  };
  const nextRecords = [...records, nextRecord].slice(-MAX_TRACE_RECORDS);
  window.__FRIDAY_CHART_BINDING_TRACE__ = nextRecords;
  writeTraceStorage(nextRecords);
}

export function summarizeChartBindingCandles(candles: RealChartCandle[]): Pick<
  ChartBindingTraceRecord,
  'first_candle_time' | 'last_candle_time'
> {
  return {
    first_candle_time: candles[0]?.time ?? null,
    last_candle_time: candles[candles.length - 1]?.time ?? null
  };
}

function installChartBindingTraceGlobals(): void {
  if (!isDevelopmentBrowser()) return;
  if (!Array.isArray(window.__FRIDAY_CHART_BINDING_TRACE__)) {
    window.__FRIDAY_CHART_BINDING_TRACE__ = readTraceStorage();
  }
  window.__FRIDAY_EXPORT_CHART_BINDING_TRACE__ = exportChartBindingTrace;
}

function exportChartBindingTrace(): string {
  const records = window.__FRIDAY_CHART_BINDING_TRACE__ ?? [];
  const latest = records[records.length - 1] ?? null;
  const latestSuccess = [...records].reverse().find((record) => !isFailureEvent(record.event)) ?? null;
  const latestFailure = [...records].reverse().find((record) => isFailureEvent(record.event)) ?? null;

  const summary = [
    'Friday Trade - Chart Binding Trace',
    `active_id=${formatTraceValue(latest?.active_id)}`,
    `raw_size=${formatTraceValue(latest?.raw_size)}`,
    `endpoint=${formatTraceValue(latest?.endpoint)}`,
    `response_count=${formatTraceValue(latest?.response_count)}`,
    `normalized_count=${formatTraceValue(latest?.normalized_count)}`,
    `state_count=${formatTraceValue(latest?.state_count)}`,
    `selected_source=${formatTraceValue(latest?.selected_source)}`,
    `graph_prop_count=${formatTraceValue(latest?.graph_prop_count)}`,
    `request_sequence=${formatTraceValue(latest?.request_sequence)}`,
    `requested=${formatTraceValue(latest?.requested_active_id)}/${formatTraceValue(latest?.requested_raw_size)}`,
    `response=${formatTraceValue(latest?.response_active_id)}/${formatTraceValue(latest?.response_raw_size)}`,
    `current_context=${formatTraceValue(latest?.current_context_active_id)}/${formatTraceValue(latest?.current_context_raw_size)}`,
    `response_applied=${formatTraceValue(latest?.response_applied)}`,
    `response_ignored=${formatTraceValue(latest?.response_ignored)}`,
    `last_successful_stage=${formatTraceValue(latestSuccess?.event)}`,
    `failure_stage=${formatTraceValue(latestFailure?.event)}`,
    `failure_reason=${formatTraceValue(latestFailure?.reason)}`
  ];

  const rows = records.map((record) => JSON.stringify(record));
  return [...summary, '', ...rows].join('\n');
}

function isDevelopmentBrowser(): boolean {
  return Boolean(import.meta.env.DEV && typeof window !== 'undefined');
}

function readTraceStorage(): ChartBindingTraceRecord[] {
  try {
    const rawValue = window.localStorage.getItem(TRACE_STORAGE_KEY);
    if (!rawValue) return [];
    const parsed = JSON.parse(rawValue);
    if (!Array.isArray(parsed)) return [];
    return parsed.slice(-MAX_TRACE_RECORDS).filter(isTraceRecord);
  } catch (_error) {
    return [];
  }
}

function writeTraceStorage(records: ChartBindingTraceRecord[]): void {
  try {
    window.localStorage.setItem(TRACE_STORAGE_KEY, JSON.stringify(records.slice(-MAX_TRACE_RECORDS)));
  } catch (_error) {
    // Storage can be unavailable in private or restricted browser contexts.
  }
}

function sanitizeTraceInput(details: ChartBindingTraceInput): ChartBindingTraceInput {
  return {
    active_id: sanitizeNullableNumber(details.active_id),
    raw_size: sanitizeNullableNumber(details.raw_size),
    symbol: sanitizeNullableString(details.symbol),
    endpoint: sanitizeEndpoint(details.endpoint),
    http_status: sanitizeNullableNumber(details.http_status),
    response_count: sanitizeNullableNumber(details.response_count),
    normalized_count: sanitizeNullableNumber(details.normalized_count),
    state_count: sanitizeNullableNumber(details.state_count),
    selected_source: sanitizeSelectedSource(details.selected_source),
    graph_prop_count: sanitizeNullableNumber(details.graph_prop_count),
    first_candle_time: sanitizeNullableNumber(details.first_candle_time),
    last_candle_time: sanitizeNullableNumber(details.last_candle_time),
    request_sequence: sanitizeNullableNumber(details.request_sequence),
    requested_active_id: sanitizeNullableNumber(details.requested_active_id),
    requested_raw_size: sanitizeNullableNumber(details.requested_raw_size),
    response_active_id: sanitizeNullableNumber(details.response_active_id),
    response_raw_size: sanitizeNullableNumber(details.response_raw_size),
    current_context_active_id: sanitizeNullableNumber(details.current_context_active_id),
    current_context_raw_size: sanitizeNullableNumber(details.current_context_raw_size),
    response_applied: sanitizeNullableBoolean(details.response_applied),
    response_ignored: sanitizeNullableBoolean(details.response_ignored),
    reason: sanitizeNullableString(details.reason)
  };
}

function sanitizeNullableNumber(value: unknown): number | null | undefined {
  if (value === undefined) return undefined;
  if (value === null) return null;
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function sanitizeNullableString(value: unknown): string | null | undefined {
  if (value === undefined) return undefined;
  if (value === null) return null;
  if (typeof value !== 'string') return null;
  return value.replace(/[\r\n\t]/g, ' ').slice(0, 180);
}

function sanitizeNullableBoolean(value: unknown): boolean | null | undefined {
  if (value === undefined) return undefined;
  if (value === null) return null;
  return typeof value === 'boolean' ? value : null;
}

function sanitizeEndpoint(value: unknown): string | null | undefined {
  const endpoint = sanitizeNullableString(value);
  if (!endpoint) return endpoint;
  try {
    const parsed = new URL(endpoint, window.location.origin);
    return `${parsed.origin}${parsed.pathname}${parsed.search}`;
  } catch (_error) {
    return endpoint;
  }
}

function sanitizeSelectedSource(value: unknown): ChartBindingSelectedSource | null | undefined {
  if (value === undefined) return undefined;
  if (
    value === 'POLARIUM_CHART_API' ||
    value === 'POLARIUM_LIVE' ||
    value === 'EMPTY' ||
    value === 'LEGACY_IQ_BLOCKED' ||
    value === 'UNKNOWN'
  ) {
    return value;
  }
  return 'UNKNOWN';
}

function isTraceRecord(value: unknown): value is ChartBindingTraceRecord {
  return Boolean(value && typeof value === 'object' && 'timestamp' in value && 'event' in value);
}

function isFailureEvent(event: ChartBindingTraceEvent): boolean {
  return (
    event === 'CHART_FETCH_EMPTY' ||
    event === 'CHART_FETCH_ERROR' ||
    event === 'STALE_RESPONSE_IGNORED' ||
    event === 'STALE_ACTIVE_KEY_RESPONSE_IGNORED' ||
    event === 'GRAPH_EMPTY' ||
    event === 'GRAPH_ERROR'
  );
}

function formatTraceValue(value: unknown): string {
  if (value === undefined || value === null || value === '') return 'null';
  return String(value);
}
