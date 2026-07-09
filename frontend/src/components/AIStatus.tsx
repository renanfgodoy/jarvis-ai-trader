import { Brain, CheckCircle2, Loader2 } from 'lucide-react';
import type { SignalAnalysis } from '../types/api';

export default function AIStatus({ signal }: { signal?: SignalAnalysis }) {
  const reasons = signal?.reasons?.length ? signal.reasons : [
    'Signal Engine conectado',
    'EMA e RSI calculados',
    'Volatilidade monitorada',
    'Risk Manager aguardando validação'
  ];

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-violet-300">AI Decision</p>
          <h3 className="mt-1 text-xl font-black text-white">Painel da IA</h3>
        </div>
        <Brain className="text-violet-300" />
      </div>

      <div className="mt-5 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5 text-center">
        <p className="text-sm text-slate-400">Sinal atual</p>
        <p className="mt-2 text-4xl font-black text-white">{signal?.trend ?? 'NEUTRAL'}</p>
        <p className="mt-2 text-sm text-violet-200">Força técnica: {Math.round(signal?.strength ?? 0)}%</p>
      </div>

      <div className="mt-5 space-y-3">
        {reasons.slice(0, 6).map((reason) => (
          <div key={reason} className="flex items-center gap-3 text-sm text-slate-300">
            <CheckCircle2 className="text-emerald-300" size={17} />
            {reason}
          </div>
        ))}
        <div className="flex items-center gap-3 text-sm text-cyan-300">
          <Loader2 className="animate-spin" size={17} />
          Monitorando novas oportunidades...
        </div>
      </div>
    </div>
  );
}
