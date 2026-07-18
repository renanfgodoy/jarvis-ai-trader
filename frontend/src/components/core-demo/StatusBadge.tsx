import type { ExecutionStatus, PipelineStepStatus, ProviderStatus } from '../../types/coreDemo';

type Status = ExecutionStatus | PipelineStepStatus | ProviderStatus | 'READY' | 'ONLINE' | 'ERROR';

const styles: Record<string, string> = {
  READY: 'border-cyan-300/25 bg-cyan-300/10 text-cyan-100',
  ONLINE: 'border-blue-300/25 bg-blue-300/10 text-blue-100',
  ERROR: 'border-red-300/25 bg-red-300/10 text-red-100',
  WAITING: 'border-slate-400/20 bg-slate-400/10 text-slate-300',
  RUNNING: 'border-blue-300/25 bg-blue-300/10 text-blue-100',
  SUCCESS: 'border-emerald-300/25 bg-emerald-300/10 text-emerald-100',
  FAILED: 'border-red-300/25 bg-red-300/10 text-red-100',
  Excelente: 'border-emerald-300/25 bg-emerald-300/10 text-emerald-100',
  Boa: 'border-cyan-300/25 bg-cyan-300/10 text-cyan-100',
  Moderada: 'border-amber-300/25 bg-amber-300/10 text-amber-100',
  Lenta: 'border-red-300/25 bg-red-300/10 text-red-100',
  placeholder: 'border-amber-300/25 bg-amber-300/10 text-amber-100',
  success: 'border-emerald-300/25 bg-emerald-300/10 text-emerald-100',
  not_configured: 'border-slate-300/20 bg-slate-300/10 text-slate-200',
  error: 'border-red-300/25 bg-red-300/10 text-red-100'
};

export default function StatusBadge({ status }: { status: Status | string }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-black uppercase tracking-wider ${styles[status] ?? styles.READY}`}>
      {status}
    </span>
  );
}
