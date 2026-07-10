import type { MarketSource } from '../../../market-data/types';
import Card from '../../Card';

export default function MarketSourceCard({ source }: { source: MarketSource }) {
  const rows = [
    ['Provider', source.provider],
    ['Origem', source.origin],
    ['Qualidade', source.dataQuality],
    ['Connector', source.connectorStatus],
    ['Sincronização', source.syncStatus]
  ];

  return (
    <Card>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Fonte dos dados</p>
      <h3 className="mt-1 text-lg font-black text-white">Origem e conectividade</h3>
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
