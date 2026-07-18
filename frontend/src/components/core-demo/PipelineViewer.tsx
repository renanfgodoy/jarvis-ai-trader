import { Check, Circle, Loader2, X } from 'lucide-react';
import type { PipelineStep } from '../../types/coreDemo';

function StepIcon({ status }: { status: PipelineStep['status'] }) {
  if (status === 'SUCCESS') return <Check size={16} />;
  if (status === 'ERROR') return <X size={16} />;
  if (status === 'RUNNING') return <Loader2 size={16} className="animate-spin" />;
  return <Circle size={16} />;
}

export default function PipelineViewer({ steps }: { steps: PipelineStep[] }) {
  const finalStatus = steps.every((step) => step.status === 'SUCCESS')
    ? 'SUCCESS'
    : steps.some((step) => step.status === 'ERROR')
      ? 'ERROR'
      : steps.some((step) => step.status === 'RUNNING')
        ? 'RUNNING'
        : 'READY';

  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-black uppercase tracking-[0.18em] text-cyan-200">Execution Pipeline</p>
        <span className="rounded-full border border-white/10 bg-black/25 px-2 py-1 text-[10px] font-black uppercase tracking-widest text-slate-300">
          Final {finalStatus}
        </span>
      </div>
      <div className="mt-4 grid gap-2">
        {steps.map((step, index) => (
          <div key={step.id} className={`flex items-center gap-3 rounded-lg border border-white/10 bg-black/20 p-2 transition ${
            step.status === 'RUNNING' ? 'animate-pulse border-cyan-300/25 bg-cyan-300/5' : ''
          }`}>
            <div className={`flex h-8 w-8 items-center justify-center rounded-full border ${
              step.status === 'SUCCESS' ? 'border-emerald-300/35 bg-emerald-300/10 text-emerald-100' :
              step.status === 'ERROR' ? 'border-red-300/35 bg-red-300/10 text-red-100' :
              step.status === 'RUNNING' ? 'border-cyan-300/35 bg-cyan-300/10 text-cyan-100' :
              'border-white/10 bg-white/5 text-slate-500'
            }`}>
              <StepIcon status={step.status} />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-black text-white">{step.label}</p>
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">{step.status}</p>
            </div>
            {index < steps.length - 1 && <span className="text-slate-600">↓</span>}
          </div>
        ))}
      </div>
    </section>
  );
}
