import { Brain, CheckCircle2, Loader2 } from 'lucide-react';
import type { SignalAnalysis } from '../types/api';

export default function AIStatus({ signal, compact = false }: { signal?: SignalAnalysis; compact?: boolean }) {
  const reasons = signal?.reasons?.length ? signal.reasons : [
    'Signal Engine conectado',
    'EMA e RSI calculados',
    'Volatilidade monitorada',
    'Risk Manager aguardando validação'
  ];

  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] uppercase tracking-[0.25em] text-violet-300">AI Decision</p>
          <h3 className="mt-1 text-base font-black text-white">Painel da IA</h3>
        </div>
        <Brain className="text-violet-300" size={20} />
      </div>

      <div className="mt-4 rounded-2xl border border-violet-400/20 bg-violet-400/10 p-4 text-center">
        <p className="text-xs text-slate-400">Sinal atual</p>
        <p className="mt-1 text-3xl font-black text-white">{signal?.trend ?? 'NEUTRAL'}</p>
        <p className="mt-1 text-xs text-violet-200">Força técnica: {Math.round(signal?.strength ?? 0)}%</p>
      </div>

      <div className="mt-4 space-y-2">
        {reasons.slice(0, compact ? 4 : 6).map((reason) => (
          <div key={reason} className="flex items-center gap-2 text-xs text-slate-300">
            <CheckCircle2 className="text-emerald-300" size={15} />
            {reason}
          </div>
        ))}
        <div className="flex items-center gap-2 text-xs text-cyan-300">
          <Loader2 className="animate-spin" size={15} />
          Monitorando oportunidades...
        </div>
      </div>
    </div>
  );
}
