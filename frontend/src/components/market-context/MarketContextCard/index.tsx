import type { LucideIcon } from 'lucide-react';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export type MarketContextTone = 'success' | 'warning' | 'danger' | 'neutral';

export type MarketContextItem = {
  label: string;
  value: string;
  detail: string;
  tone: MarketContextTone;
  icon: LucideIcon;
};

export default function MarketContextCard({ item }: { item: MarketContextItem }) {
  const Icon = item.icon;

  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <Icon className={iconColor(item.tone)} size={21} />
        <StatusBadge status={item.value} tone={item.tone} />
      </div>
      <p className="mt-4 text-[10px] font-black uppercase tracking-widest text-slate-500">{item.label}</p>
      <p className="mt-2 break-words text-base font-black text-white">{item.value}</p>
      <p className="mt-2 text-xs leading-relaxed text-slate-500">{item.detail}</p>
    </Card>
  );
}

function iconColor(tone: MarketContextTone) {
  if (tone === 'success') return 'text-emerald-300';
  if (tone === 'warning') return 'text-amber-300';
  if (tone === 'danger') return 'text-red-300';
  return 'text-cyan-300';
}
