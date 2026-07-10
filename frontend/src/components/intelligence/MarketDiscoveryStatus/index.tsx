import type { MarketDiscoveryItem } from '../../../intelligence/types';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export default function MarketDiscoveryStatus({ items }: { items: MarketDiscoveryItem[] }) {
  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Market Discovery</p>
          <h3 className="mt-1 text-lg font-black text-white">Dados descobertos</h3>
        </div>
        <StatusBadge status="OBSERVANDO" tone="neutral" />
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <div key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{item.label}</p>
              <span className={`h-2.5 w-2.5 rounded-full ${statusDot(item.status)}`} />
            </div>
            <p className="mt-2 break-words text-sm font-black text-white">{item.value}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

function statusDot(status: MarketDiscoveryItem['status']) {
  if (status === 'success') return 'bg-emerald-300';
  if (status === 'warning') return 'bg-amber-300';
  if (status === 'blocked') return 'bg-red-300';
  return 'bg-slate-500';
}
