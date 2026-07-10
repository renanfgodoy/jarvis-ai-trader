import { DatabaseZap } from 'lucide-react';
import type { MarketSnapshot } from '../../../market-data/types';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export default function MarketDataSummaryCard({ snapshot }: { snapshot: MarketSnapshot }) {
  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Resumo</p>
          <h2 className="mt-1 text-xl font-black text-white">Market Data Engine</h2>
        </div>
        <DatabaseZap className="text-cyan-300" size={24} />
      </div>
      <p className="mt-4 text-sm leading-relaxed text-slate-400">
        Camada única para fornecer contexto de mercado ao Friday Trade. Não cria indicadores, IA ou execução.
      </p>
      <div className="mt-5 flex flex-wrap items-center gap-2">
        <StatusBadge status={snapshot.marketReady ? 'MARKET READY' : 'NÃO DISPONÍVEL'} tone={snapshot.marketReady ? 'success' : 'warning'} />
        <StatusBadge status={snapshot.source.dataQuality} tone={snapshot.source.dataQuality === 'REAL' ? 'success' : 'neutral'} />
      </div>
    </Card>
  );
}
