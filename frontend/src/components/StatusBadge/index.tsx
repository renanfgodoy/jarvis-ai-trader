export default function StatusBadge({ status, tone = 'neutral' }: { status: string; tone?: 'success' | 'warning' | 'danger' | 'neutral' }) {
  const color = tone === 'success'
    ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300'
    : tone === 'warning'
      ? 'border-amber-400/30 bg-amber-400/10 text-amber-300'
      : tone === 'danger'
        ? 'border-red-400/30 bg-red-400/10 text-red-300'
        : 'border-slate-500/30 bg-slate-500/10 text-slate-300';

  return <span className={`rounded-full border px-3 py-1 text-[10px] font-black uppercase tracking-widest ${color}`}>{status}</span>;
}
