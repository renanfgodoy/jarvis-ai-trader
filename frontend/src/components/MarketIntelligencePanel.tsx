import { Brain, ShieldCheck } from 'lucide-react';
import { brand } from '../branding/brand';
import type { MarketIntelligence } from '../types/api';

type Props = {
  intelligence?: MarketIntelligence;
  enabled: boolean;
};

export default function MarketIntelligencePanel({ intelligence, enabled }: Props) {
  if (!enabled || !intelligence) {
    return (
      <div className="panel p-4">
        <div className="flex items-center gap-2">
          <Brain className="text-cyan-300" size={18} />
          <p className="eyebrow">Market Intelligence</p>
        </div>
        <p className="mt-3 text-sm text-slate-400">Selecione M1/M5/M15 para o {brand.shortName} analisar imediatamente. AutoTrade é somente para execução quando o gate aprovar.</p>
      </div>
    );
  }

  const tone = intelligence.status === 'APPROVED' ? 'text-emerald-300' : intelligence.status === 'WATCHLIST' ? 'text-amber-300' : 'text-red-300';
  const factors = intelligence.factors.slice(0, 6);

  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="eyebrow">Market Intelligence</p>
          <h3 className="mt-1 text-lg font-black text-white">{intelligence.symbol} · {intelligence.timeframe}</h3>
        </div>
        <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-right">
          <p className="text-[10px] uppercase tracking-widest text-slate-400">Score</p>
          <p className={`text-3xl font-black ${tone}`}>{intelligence.score}</p>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-4 gap-2 text-center">
        <Mini label="IA" value={intelligence.signal} tone={tone} />
        <Mini label="Status" value={intelligence.status} tone={tone} />
        <Mini label="Payout" value={`${intelligence.payout.toFixed(0)}%`} />
        <Mini label="Risco" value={intelligence.risk_bias} />
      </div>

      <div className="mt-4 space-y-2">
        {factors.map((factor) => (
          <div key={factor.name} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2 text-xs">
            <div className="min-w-0">
              <p className="font-black text-slate-200">{factor.passed ? '✓' : '•'} {factor.name}</p>
              <p className="truncate text-slate-500">{factor.explanation}</p>
            </div>
            <span className="ml-3 font-black text-cyan-300">{factor.points}/{factor.max_points}</span>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-xl border border-emerald-400/15 bg-emerald-400/5 p-3">
        <div className="flex items-center gap-2 text-emerald-300"><ShieldCheck size={16} /><span className="text-xs font-black uppercase tracking-widest">Ação</span></div>
        <p className="mt-2 text-sm font-bold text-slate-200">{intelligence.action}</p>
      </div>
    </div>
  );
}

function Mini({ label, value, tone = 'text-white' }: { label: string; value: string; tone?: string }) {
  return <div className="rounded-xl border border-white/10 bg-white/[0.035] p-2"><p className="text-[9px] uppercase tracking-widest text-slate-500">{label}</p><p className={`mt-1 text-sm font-black ${tone}`}>{value}</p></div>;
}
