import type { MarketDataTimeframe, MarketContext } from '../../../market-data/types';
import Card from '../../Card';

const timeframes: MarketDataTimeframe[] = ['M1', 'M5', 'M15'];

export default function MarketContextCard({
  context,
  setAsset,
  setTimeframe
}: {
  context: MarketContext;
  setAsset: (asset: string) => void;
  setTimeframe: (timeframe: MarketDataTimeframe) => void;
}) {
  return (
    <Card>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Contexto compartilhado</p>
      <h3 className="mt-1 text-lg font-black text-white">Ativo e timeframe globais</h3>
      <div className="mt-4 space-y-3">
        <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Ativo</label>
        <input className="login-input" value={context.asset} onChange={(event) => setAsset(event.target.value)} />
        <div className="flex flex-wrap gap-2">
          {timeframes.map((timeframe) => (
            <button
              key={timeframe}
              type="button"
              onClick={() => setTimeframe(timeframe)}
              className={`rounded-xl border px-4 py-2 text-xs font-black transition ${
                context.timeframe === timeframe
                  ? 'border-cyan-400/50 bg-cyan-400/20 text-cyan-200'
                  : 'border-white/10 bg-white/[0.035] text-slate-400 hover:bg-white/[0.06]'
              }`}
            >
              {timeframe}
            </button>
          ))}
        </div>
      </div>
    </Card>
  );
}
