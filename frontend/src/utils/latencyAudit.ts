export type FridayLatencyAuditDetail = Record<string, string | number | boolean | null>;

export type FridayLatencyAuditRecord = {
  stage: string;
  at_ms: number;
  detail: FridayLatencyAuditDetail;
};

type FridayLatencyAuditState = {
  version: 'v4.9';
  records: FridayLatencyAuditRecord[];
  counters: Record<string, number>;
};

declare global {
  interface Window {
    __FRIDAY_LATENCY_AUDIT__?: FridayLatencyAuditState;
  }
}

const MAX_LATENCY_AUDIT_RECORDS = 500;

export function recordFridayLatencyAudit(stage: string, detail: FridayLatencyAuditDetail = {}): void {
  if (typeof window === 'undefined' || typeof performance === 'undefined') return;

  const state = (window.__FRIDAY_LATENCY_AUDIT__ ??= {
    version: 'v4.9',
    records: [],
    counters: {}
  });
  const record = {
    stage,
    at_ms: roundAuditMs(performance.now()),
    detail
  };
  state.records = [...state.records.slice(-(MAX_LATENCY_AUDIT_RECORDS - 1)), record];
  state.counters[stage] = (state.counters[stage] ?? 0) + 1;
  window.dispatchEvent(new CustomEvent('friday-latency-audit', { detail: record }));
}

export function measureFridayLatencyAudit<TValue>(
  stage: string,
  measure: () => TValue,
  detail: FridayLatencyAuditDetail = {}
): TValue {
  if (typeof performance === 'undefined') {
    return measure();
  }
  const startedAt = performance.now();
  const value = measure();
  recordFridayLatencyAudit(stage, {
    ...detail,
    duration_ms: roundAuditMs(performance.now() - startedAt)
  });
  return value;
}

function roundAuditMs(value: number): number {
  return Math.round(value * 1000) / 1000;
}
