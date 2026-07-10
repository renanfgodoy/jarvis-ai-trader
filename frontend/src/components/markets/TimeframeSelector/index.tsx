import { Clock3 } from 'lucide-react';
import type { MarketWorkspaceTimeframe } from '../../../hooks/useMarketStatus';

const timeframes: MarketWorkspaceTimeframe[] = ['M1', 'M5', 'M15', 'H1'];

export default function TimeframeSelector({
  selected,
  onSelect
}: {
  selected: MarketWorkspaceTimeframe;
  onSelect: (timeframe: MarketWorkspaceTimeframe) => void;
}) {
  return (
    <div className="panel flex flex-wrap items-center justify-between gap-3 p-4">
      <div>
        <p className="eyebrow">Timeframe</p>
        <h3 className="mt-1 text-sm font-black text-white">Leitura de mercado</h3>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {timeframes.map((timeframe) => (
          <button
            key={timeframe}
            type="button"
            onClick={() => onSelect(timeframe)}
            className={`inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-xs font-black transition ${
              selected === timeframe
                ? 'border-cyan-400/50 bg-cyan-400/20 text-cyan-200'
                : 'border-white/10 bg-white/[0.035] text-slate-400 hover:bg-white/[0.06]'
            }`}
          >
            <Clock3 size={14} /> {timeframe}
          </button>
        ))}
      </div>
    </div>
  );
}
