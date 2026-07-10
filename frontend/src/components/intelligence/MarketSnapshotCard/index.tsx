import { Clock3, Landmark, WalletCards } from 'lucide-react';
import type { MarketSnapshot } from '../../../intelligence/types';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export default function MarketSnapshotCard({ snapshot }: { snapshot: MarketSnapshot }) {
  const items = [
    { label: 'Ativo', value: snapshot.asset },
    { label: 'Timeframe', value: snapshot.timeframe },
    { label: 'Broker', value: snapshot.broker },
    { label: 'Conta', value: snapshot.account },
    { label: 'Moeda', value: snapshot.currency },
    { label: 'Ambiente', value: snapshot.environment },
    { label: 'Atualização', value: snapshot.updatedAt },
    { label: 'Fonte', value: snapshot.dataSource }
  ];

  return (
    <Card>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Market Snapshot</p>
          <h2 className="mt-1 text-xl font-black text-white">Observação atual do mercado</h2>
        </div>
        <StatusBadge status={snapshot.marketReady ? 'MARKET READY' : 'INCOMPLETO'} tone={snapshot.marketReady ? 'success' : 'warning'} />
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {items.map((item, index) => {
          const Icon = index === 2 ? Landmark : index === 4 ? WalletCards : Clock3;
          return (
            <div key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
              <Icon className="text-cyan-300" size={17} />
              <p className="mt-3 text-[10px] font-black uppercase tracking-widest text-slate-500">{item.label}</p>
              <p className="mt-1 break-words text-sm font-black text-white">{item.value}</p>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
