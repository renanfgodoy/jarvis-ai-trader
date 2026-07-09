import { Clock3, LockKeyhole, Play } from 'lucide-react';
import type { Timeframe } from '../types/api';

const timeframes: Timeframe[] = ['M1', 'M5', 'M15'];

type Props = {
  selected: Timeframe | null;
  onSelect: (timeframe: Timeframe) => void;
  autoTradeEnabled: boolean;
  onToggleAutoTrade: () => void;
  gateStatus?: string;
};

export default function TimeframeControl({ selected, onSelect, autoTradeEnabled, onToggleAutoTrade, gateStatus }: Props) {
  return (
    <div className="panel flex flex-wrap items-center justify-between gap-3 p-3">
      <div>
        <p className="eyebrow">Operação</p>
        <h3 className="mt-1 text-sm font-black text-white">Timeframe + AutoTrade Gate</h3>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {timeframes.map((tf) => (
          <button
            key={tf}
            onClick={() => onSelect(tf)}
            className={`inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-xs font-black transition ${selected === tf ? 'border-cyan-400/50 bg-cyan-400/20 text-cyan-200' : 'border-white/10 bg-white/[0.035] text-slate-400 hover:bg-white/[0.06]'}`}
          >
            <Clock3 size={14} /> {tf}
          </button>
        ))}
        <button
          onClick={onToggleAutoTrade}
          className={`inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-xs font-black transition ${autoTradeEnabled ? 'border-emerald-400/50 bg-emerald-400/20 text-emerald-200' : 'border-amber-400/30 bg-amber-400/10 text-amber-200'}`}
        >
          {autoTradeEnabled ? <Play size={14} /> : <LockKeyhole size={14} />}
          {autoTradeEnabled ? 'AutoTrade ON' : 'Ativar AutoTrade'}
        </button>
        <span className="rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2 text-[10px] font-black uppercase tracking-widest text-slate-400">
          Gate: {gateStatus ?? 'WAITING'}
        </span>
      </div>
    </div>
  );
}
