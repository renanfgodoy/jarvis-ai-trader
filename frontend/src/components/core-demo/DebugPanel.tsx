import type { CoreDemoResponse, ExecutionResponse, TradingResponse } from '../../types/coreDemo';
import ProviderConfigurationPanel from './ProviderConfigurationPanel';
import ProviderHealthPanel from './ProviderHealthPanel';
import StatusBadge from './StatusBadge';

function isTradingResponse(response: CoreDemoResponse): response is TradingResponse {
  return 'execution' in response && 'decision' in response;
}

function unwrapExecution(response: CoreDemoResponse | null): ExecutionResponse | null {
  return response && isTradingResponse(response) ? response.execution.execution : response;
}

export default function DebugPanel({ response }: { response: CoreDemoResponse | null }) {
  const execution = unwrapExecution(response);
  const metadata = execution?.metadata;
  const providerMetadata = execution?.provider_response.metadata ?? {};
  const providerRegistry = Array.isArray(providerMetadata.provider_registry)
    ? providerMetadata.provider_registry.join(', ')
    : 'mock';
  const providerCapabilities = Array.isArray(providerMetadata.provider_capabilities)
    ? providerMetadata.provider_capabilities.join(', ')
    : 'chat';

  return (
    <div className="grid gap-4">
      <section className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs font-black uppercase tracking-[0.18em] text-cyan-200">Developer Console</p>
          <StatusBadge status={execution ? execution.status : 'READY'} />
        </div>
        <div className="mt-4 grid gap-2 text-sm">
          <Row label="Core Orchestrator" value="ONLINE" />
          <Row label="Module SDK" value={response && isTradingResponse(response) ? 'Trading Module' : 'READY'} />
          <Row label="Identity Engine" value={execution?.identity ?? 'READY'} />
          <Row label="Prompt Engine" value={execution ? 'PromptPackage built internally' : 'READY'} />
          <Row label="Provider Engine" value={execution?.provider ?? 'READY'} />
          <Row label="Mock Provider" value={execution?.provider_response.status ?? 'READY'} />
          <Row label="Provider Registry" value={providerRegistry} />
          <Row label="Provider Ativo" value={typeof providerMetadata.active_provider === 'string' ? providerMetadata.active_provider : execution?.provider ?? 'mock'} />
          <Row label="Provider Health" value={typeof providerMetadata.provider_health === 'string' ? providerMetadata.provider_health : 'UNKNOWN'} />
          <Row label="Model" value={typeof providerMetadata.provider_model === 'string' ? providerMetadata.provider_model : 'mock'} />
          <Row label="Capabilities" value={providerCapabilities} />
          <Row label="Pipeline Version" value={metadata?.pipeline_version ?? '1.0'} />
          <Row label="Execution Time" value={metadata?.duration !== null && metadata?.duration !== undefined ? `${metadata.duration.toFixed(4)}s` : 'Aguardando execução'} />
          <Row label="Execution ID" value={metadata?.execution_id ?? 'Não iniciado'} />
          <Row label="Request ID" value={execution?.request_id ?? 'Não iniciado'} />
          <Row label="Modo" value="Development" />
        </div>
      </section>
      <ProviderConfigurationPanel response={response} />
      <ProviderHealthPanel response={response} />
    </div>
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
