import { Activity, Clock3, Radio, Server, Wifi } from 'lucide-react';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export type MarketStatusItem = {
  label: string;
  value: string;
  tone?: 'success' | 'warning' | 'danger' | 'neutral';
};

export default function MarketStatusWidget({ items }: { items: MarketStatusItem[] }) {
  const icons = [Server, Activity, Radio, Wifi, Clock3, Activity];

  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Market Status</p>
          <h3 className="mt-1 text-lg font-black text-white">Condição do mercado</h3>
        </div>
        <StatusBadge status="LEITURA" tone="neutral" />
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {items.map((item, index) => {
          const Icon = icons[index] ?? Activity;
          return (
            <div key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
              <Icon className="text-cyan-300" size={18} />
              <p className="mt-3 text-[10px] font-black uppercase tracking-widest text-slate-500">{item.label}</p>
              <p className={`mt-1 text-sm font-black ${toneClass(item.tone)}`}>{item.value}</p>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

function toneClass(tone: MarketStatusItem['tone']) {
  if (tone === 'success') return 'text-emerald-300';
  if (tone === 'warning') return 'text-amber-300';
  if (tone === 'danger') return 'text-red-300';
  return 'text-white';
}
