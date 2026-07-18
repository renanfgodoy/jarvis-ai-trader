import type { CoreDemoResponse, ExecutionResponse, PipelineStep, TradingResponse } from '../../types/coreDemo';
import StatusBadge from './StatusBadge';

function isTradingResponse(response: CoreDemoResponse): response is TradingResponse {
  return 'execution' in response && 'decision' in response;
}

function unwrapExecution(response: CoreDemoResponse | null): ExecutionResponse | null {
  return response && isTradingResponse(response) ? response.execution.execution : response;
}

function pipelineStatus(steps: PipelineStep[]) {
  if (steps.some((step) => step.status === 'ERROR')) return 'ERROR';
  if (steps.every((step) => step.status === 'SUCCESS')) return 'SUCCESS';
  if (steps.some((step) => step.status === 'RUNNING')) return 'ONLINE';
  return 'READY';
}

export default function SystemStatusCards({
  loading,
  response,
  error,
  pipeline
}: {
  loading: boolean;
  response: CoreDemoResponse | null;
  error: string | null;
  pipeline: PipelineStep[];
}) {
  const execution = unwrapExecution(response);
  const status = error ? 'ERROR' : loading ? 'ONLINE' : execution ? 'SUCCESS' : 'READY';
  const cards = [
    ['Core', status],
    ['SDK', response && isTradingResponse(response) ? 'SUCCESS' : status],
    ['Trading Module', response && isTradingResponse(response) ? 'SUCCESS' : 'READY'],
    ['Identity Engine', execution?.identity ? 'SUCCESS' : status],
    ['Prompt Engine', execution ? 'SUCCESS' : status],
    ['Provider Engine', execution?.provider ? 'SUCCESS' : status],
    ['Pipeline', pipelineStatus(pipeline)]
  ] as const;

  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-7">
      {cards.map(([label, value]) => (
        <div key={label} className="rounded-xl border border-white/10 bg-white/[0.035] p-3 transition hover:border-cyan-300/25 hover:bg-cyan-300/5">
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
          <div className="mt-2">
            <StatusBadge status={value} />
          </div>
        </div>
      ))}
    </section>
  );
}
