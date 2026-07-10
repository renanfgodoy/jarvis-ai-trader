import { DatabaseZap } from 'lucide-react';
import type { MarketSource } from '../../../intelligence/types';
import Card from '../../Card';

export default function MarketSourceCard({ source }: { source: MarketSource }) {
  const rows = [
    ['Provider', source.provider],
    ['Connector', source.connectorStatus],
    ['Qualidade', source.marketDataQuality],
    ['Sincronização', source.syncStatus],
    ['Última sync', source.lastSync],
    ['Disponibilidade', source.availability]
  ];

  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Fonte</p>
          <h3 className="mt-1 text-lg font-black text-white">Origem dos dados</h3>
        </div>
        <DatabaseZap className="text-cyan-300" size={22} />
      </div>
      <div className="mt-4 space-y-2">
        {rows.map(([label, value]) => (
          <div key={label} className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/[0.025] px-3 py-2">
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</span>
            <span className="text-right text-sm font-black text-white">{value}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
