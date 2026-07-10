import type { LucideIcon } from 'lucide-react';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export type ReadinessCheckStatus = 'ok' | 'warning' | 'blocked';

export type ReadinessCheck = {
  label: string;
  value: string;
  detail: string;
  status: ReadinessCheckStatus;
  icon: LucideIcon;
};

const toneByStatus = {
  ok: 'success',
  warning: 'warning',
  blocked: 'danger'
} as const;

const labelByStatus = {
  ok: 'OK',
  warning: 'Parcial',
  blocked: 'Bloqueado'
};

export default function ReadinessCheckCard({ check }: { check: ReadinessCheck }) {
  const Icon = check.icon;

  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <Icon className={check.status === 'ok' ? 'text-emerald-300' : check.status === 'warning' ? 'text-amber-300' : 'text-red-300'} size={21} />
        <StatusBadge status={labelByStatus[check.status]} tone={toneByStatus[check.status]} />
      </div>
      <p className="mt-4 text-[10px] font-black uppercase tracking-widest text-slate-500">{check.label}</p>
      <p className="mt-2 break-words text-base font-black text-white">{check.value}</p>
      <p className="mt-2 text-xs leading-relaxed text-slate-500">{check.detail}</p>
    </Card>
  );
}
