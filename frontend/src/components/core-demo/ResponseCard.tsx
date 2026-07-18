import { Cpu, FileText } from 'lucide-react';
import type { CoreDemoResponse, ExecutionResponse, TradingResponse } from '../../types/coreDemo';
import StatusBadge from './StatusBadge';

function isTradingResponse(response: CoreDemoResponse): response is TradingResponse {
  return 'execution' in response && 'decision' in response;
}

function unwrapExecution(response: CoreDemoResponse): ExecutionResponse {
  return isTradingResponse(response) ? response.execution.execution : response;
}

function parseScenario(response: TradingResponse | null) {
  const scenario = typeof response?.metadata?.scenario === 'string' ? response.metadata.scenario : '';
  const match = scenario.match(/^(\S+)\s+(\S+)\s+(\S+)\s+using\s+(.+)$/);

  return {
    market: match?.[1] ?? 'Nao informado',
    symbol: match?.[2] ?? 'Nao informado',
    timeframe: match?.[3] ?? 'Nao informado',
    strategy: match?.[4] ?? 'Nao informado'
  };
}

function classifyLatency(latency: number) {
  if (latency < 0.05) return 'Excelente';
  if (latency < 0.15) return 'Boa';
  if (latency < 0.5) return 'Moderada';
  return 'Lenta';
}

export default function ResponseCard({ response }: { response: CoreDemoResponse | null }) {
  if (!response) {
    return (
      <section className="rounded-xl border border-dashed border-white/10 bg-white/[0.025] p-5">
        <p className="text-sm font-semibold text-slate-400">Execute uma mensagem para visualizar o Execution Report da Friday.</p>
      </section>
    );
  }

  const execution = unwrapExecution(response);
  const trading = isTradingResponse(response) ? response : null;
  const scenario = parseScenario(trading);

  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.035] p-5 shadow-2xl shadow-cyan-950/20">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="flex items-center gap-2 text-xs font-black uppercase tracking-[0.18em] text-cyan-200">
            <FileText size={15} />
            J.A.R.V.I.S Trading Report
          </p>
          <h2 className="mt-2 text-xl font-black leading-tight text-white">
            {trading ? trading.decision : execution.status}
          </h2>
          <p className="mt-2 max-w-4xl text-sm font-semibold leading-6 text-slate-300">
            {trading ? trading.analysis : execution.provider_response.response}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={execution.status} />
          <StatusBadge status={classifyLatency(execution.latency)} />
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Mercado" value={scenario.market} />
        <Metric label="Ativo" value={scenario.symbol} />
        <Metric label="Timeframe" value={scenario.timeframe} />
        <Metric label="Estrategia" value={scenario.strategy} />
        <Metric label="Trend" value={trading?.trend ?? 'Nao aplicado'} />
        <Metric label="Risk" value={trading?.risk ?? 'Nao aplicado'} />
        <Metric label="Confidence" value={trading ? `${trading.confidence}%` : 'Nao aplicado'} />
        <Metric label="Decision" value={trading?.decision ?? execution.status} />
        <Metric label="Support" value={trading?.support ?? 'Nao aplicado'} />
        <Metric label="Resistance" value={trading?.resistance ?? 'Nao aplicado'} />
        <Metric label="Identity" value={execution.identity} />
        <Metric label="Provider" value={execution.provider} />
        <Metric label="Latency" value={`${(execution.latency * 1000).toFixed(0)} ms · ${classifyLatency(execution.latency)}`} />
        <Metric label="Timestamp" value={new Date(execution.timestamp).toLocaleString()} />
        <Metric label="Execution ID" value={execution.metadata.execution_id} />
        <Metric label="Request ID" value={execution.request_id} />
        <Metric label="Fingerprint" value={execution.fingerprint.slice(0, 16)} />
      </div>

      <div className="mt-4 flex items-center gap-2 rounded-lg border border-cyan-300/10 bg-cyan-300/5 px-3 py-2 text-xs font-bold text-cyan-100">
        <Cpu size={14} />
        ExecutionResponse publico validado. Objetos internos do pipeline permanecem fora da UI.
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-3">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-1 break-words text-sm font-bold text-slate-100">{value}</p>
    </div>
  );
}
