import type { DiscoveryTimelineItem } from '../../../intelligence/types';
import Card from '../../Card';

export default function DiscoveryTimeline({ items }: { items: DiscoveryTimelineItem[] }) {
  return (
    <Card>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Discovery Timeline</p>
      <h3 className="mt-1 text-lg font-black text-white">Sequência de observação</h3>
      <div className="mt-5 space-y-4">
        {items.map((item) => (
          <div key={`${item.title}-${item.time}`} className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className={`h-3 w-3 rounded-full ${dotClass(item.status)}`} />
              <span className="mt-1 h-10 w-px bg-white/10" />
            </div>
            <div>
              <p className="text-sm font-black text-white">{item.title}</p>
              <p className="mt-1 text-xs text-slate-500">{item.time}</p>
              <p className="mt-1 text-sm text-slate-400">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function dotClass(status: DiscoveryTimelineItem['status']) {
  if (status === 'success') return 'bg-emerald-300 shadow-glow';
  if (status === 'warning') return 'bg-amber-300';
  if (status === 'blocked') return 'bg-red-300';
  return 'bg-slate-500';
}
