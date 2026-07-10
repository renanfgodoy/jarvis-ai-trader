import type { MarketSnapshot } from '../../../market-data/types';
import Card from '../../Card';

export default function MarketSnapshotCard({ snapshot }: { snapshot: MarketSnapshot }) {
  const rows = [
    ['Ativo', snapshot.context.asset],
    ['Timeframe', snapshot.context.timeframe],
    ['Broker', snapshot.context.broker],
    ['Conta', snapshot.context.account],
    ['Moeda', snapshot.context.currency],
    ['Ambiente', snapshot.context.environment],
    ['Última atualização', snapshot.status.lastUpdate],
    ['Origem', snapshot.source.origin]
  ];

  return (
    <Card>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Snapshot</p>
      <h3 className="mt-1 text-lg font-black text-white">Contexto atual de mercado</h3>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {rows.map(([label, value]) => (
          <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
            <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
