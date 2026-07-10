import type { MarketSnapshot } from '../../../market-data/types';
import Card from '../../Card';

export default function MarketDataTimeline({ snapshot }: { snapshot: MarketSnapshot }) {
  const items = [
    ['Contexto atualizado', `${snapshot.context.asset} · ${snapshot.context.timeframe}`],
    ['Fonte verificada', snapshot.source.provider],
    ['Disponibilidade lida', snapshot.status.availability],
    ['Snapshot publicado', snapshot.marketReady ? 'Dados mínimos disponíveis.' : 'Dados insuficientes.']
  ];

  return (
    <Card>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Timeline</p>
      <h3 className="mt-1 text-lg font-black text-white">Atualização do Market Data</h3>
      <div className="mt-5 space-y-4">
        {items.map(([title, description]) => (
          <div key={title} className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className="h-3 w-3 rounded-full bg-cyan-300 shadow-glow" />
              <span className="mt-1 h-8 w-px bg-white/10" />
            </div>
            <div>
              <p className="text-sm font-black text-white">{title}</p>
              <p className="mt-1 text-xs text-slate-500">{snapshot.status.lastUpdate}</p>
              <p className="mt-1 text-sm text-slate-400">{description}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
