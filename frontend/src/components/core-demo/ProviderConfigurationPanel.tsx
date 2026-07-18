import type { CoreDemoResponse, ExecutionResponse, TradingResponse } from '../../types/coreDemo';

function isTradingResponse(response: CoreDemoResponse): response is TradingResponse {
  return 'execution' in response && 'decision' in response;
}

function unwrapExecution(response: CoreDemoResponse | null): ExecutionResponse | null {
  return response && isTradingResponse(response) ? response.execution.execution : response;
}

export default function ProviderConfigurationPanel({ response }: { response: CoreDemoResponse | null }) {
  const execution = unwrapExecution(response);
  const providerMetadata = execution?.provider_response.metadata ?? {};
  const configuration = readObject(providerMetadata.provider_configuration);
  const environment = readObject(providerMetadata.provider_environment);
  const featureFlags = readObject(providerMetadata.provider_feature_flags);

  return (
    <section className="rounded-xl border border-cyan-400/15 bg-cyan-400/[0.04] p-4">
      <p className="text-xs font-black uppercase tracking-[0.18em] text-cyan-200">Provider Configuration</p>
      <div className="mt-4 grid gap-2 text-sm">
        <Row label="Environment" value={readString(environment.name, 'development')} />
        <Row label="Default Provider" value={readString(configuration.default_provider, 'mock')} />
        <Row label="Enabled Providers" value={readList(configuration.enabled_providers, 'mock')} />
        <Row label="Provider Priority" value={readList(configuration.provider_priority, 'mock')} />
        <Row label="Fallback" value={readBool(configuration.fallback_enabled, true) ? 'ENABLED' : 'DISABLED'} />
        <Row label="Feature Flags" value={formatFeatureFlags(featureFlags)} />
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

function readBool(value: unknown, fallback: boolean): boolean {
  return typeof value === 'boolean' ? value : fallback;
}

function readList(value: unknown, fallback: string): string {
  return Array.isArray(value) && value.length > 0 ? value.join(', ') : fallback;
}

function formatFeatureFlags(flags: Record<string, unknown>): string {
  const enabled = Object.entries(flags)
    .filter(([, value]) => value === true)
    .map(([key]) => key);
  return enabled.length > 0 ? enabled.join(', ') : 'mock';
}
