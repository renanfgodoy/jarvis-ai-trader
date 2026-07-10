import { AlertTriangle, CheckCircle2, CircleDashed, Loader2, LockKeyhole } from 'lucide-react';
import type { ConnectionWizardStep } from '../../../hooks/useConnectionWizard';

const stateStyle = {
  success: 'border-emerald-400/30 bg-emerald-400/10 text-emerald-200',
  running: 'border-cyan-400/30 bg-cyan-400/10 text-cyan-200',
  error: 'border-red-400/30 bg-red-400/10 text-red-200',
  pending: 'border-white/10 bg-white/[0.025] text-slate-300',
  blocked: 'border-amber-400/25 bg-amber-400/10 text-amber-200'
};

const icons = {
  success: CheckCircle2,
  running: Loader2,
  error: AlertTriangle,
  pending: CircleDashed,
  blocked: LockKeyhole
};

export default function ConnectionStep({ step }: { step: ConnectionWizardStep }) {
  const Icon = icons[step.state];

  return (
    <div className={`rounded-2xl border p-4 ${stateStyle[step.state]}`}>
      <div className="flex items-center justify-between gap-3">
        <Icon className={step.state === 'running' ? 'animate-spin' : ''} size={20} />
        <span className="text-[10px] font-black uppercase tracking-widest">{step.statusLabel}</span>
      </div>
      <p className="mt-4 text-sm font-black text-white">{step.label}</p>
      <p className="mt-2 min-h-[36px] text-xs leading-relaxed text-slate-400">{step.description}</p>
    </div>
  );
}
