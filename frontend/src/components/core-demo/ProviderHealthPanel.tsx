import type { CoreDemoResponse, ExecutionResponse, TradingResponse } from '../../types/coreDemo';

function isTradingResponse(response: CoreDemoResponse): response is TradingResponse {
  return 'execution' in response && 'decision' in response;
}

function unwrapExecution(response: CoreDemoResponse | null): ExecutionResponse | null {
  return response && isTradingResponse(response) ? response.execution.execution : response;
}

export default function ProviderHealthPanel({ response }: { response: CoreDemoResponse | null }) {
  const execution = unwrapExecution(response);
  const providerMetadata = execution?.provider_response.metadata ?? {};
  const activeProvider = typeof providerMetadata.active_provider === 'string' ? providerMetadata.active_provider : 'mock';
  const healthSummary = readObject(providerMetadata.provider_health_summary);
  const activeHealth = readObject(healthSummary[activeProvider]);

  return (
    <section className="rounded-xl border border-emerald-400/15 bg-emerald-400/[0.04] p-4">
      <p className="text-xs font-black uppercase tracking-[0.18em] text-emerald-200">Provider Health</p>
      <div className="mt-4 grid gap-2 text-sm">
        <Row label="Active Provider" value={activeProvider} />
        <Row label="Status" value={readString(activeHealth.status, typeof providerMetadata.provider_health === 'string' ? providerMetadata.provider_health : 'UNKNOWN')} />
        <Row label="Requests" value={readNumber(activeHealth.request_count, 0).toString()} />
        <Row label="Latency Average" value={`${readNumber(activeHealth.latency_average, 0).toFixed(4)}s`} />
        <Row label="Last Execution" value={readString(activeHealth.last_execution, 'Aguardando execução')} />
        <Row label="Last Error" value={readString(activeHealth.last_error, 'Nenhum erro')} />
      </div>
    </section>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-lg border border-white/10 bg-black/20 px-3 py-2">
      <span className="text-xs font-black uppercase tracking-widest text-slate-500">{label}</span>
      <span className="break-words text-right font-semibold text-slate-100">{value}</span>
    </div>
  );
}

function readObject(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function readString(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.length > 0 ? value : fallback;
}

function readNumber(value: unknown, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}
