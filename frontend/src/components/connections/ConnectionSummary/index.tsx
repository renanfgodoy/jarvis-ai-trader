import Card from '../../Card';
import ConnectionReadinessBadge from '../ConnectionReadinessBadge';
import type { ConnectionReadiness } from '../../../hooks/usePolariumConnection';

export type ConnectionSummaryItem = {
  label: string;
  value: string;
  tone?: 'success' | 'warning' | 'danger' | 'neutral';
};

export default function ConnectionSummary({
  items,
  readiness
}: {
  items: ConnectionSummaryItem[];
  readiness: ConnectionReadiness;
}) {
  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Resumo operacional</p>
          <h3 className="mt-1 text-lg font-black text-white">Estado atual da conexão</h3>
        </div>
        <ConnectionReadinessBadge readiness={readiness} />
      </div>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {items.map((item) => (
          <div key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{item.label}</p>
            <p className={`mt-2 break-words text-sm font-black ${toneClass(item.tone)}`}>{item.value}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

function toneClass(tone: ConnectionSummaryItem['tone']) {
  if (tone === 'success') return 'text-emerald-300';
  if (tone === 'warning') return 'text-amber-300';
  if (tone === 'danger') return 'text-red-300';
  return 'text-white';
}
