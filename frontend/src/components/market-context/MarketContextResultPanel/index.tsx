import { AlertTriangle, CheckCircle2, PauseCircle } from 'lucide-react';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export type MarketContextReadiness = 'READY' | 'PARTIAL' | 'BLOCKED';

const toneByReadiness = {
  READY: 'success',
  PARTIAL: 'warning',
  BLOCKED: 'danger'
} as const;

export default function MarketContextResultPanel({
  readiness,
  reasons
}: {
  readiness: MarketContextReadiness;
  reasons: string[];
}) {
  const Icon = readiness === 'READY' ? CheckCircle2 : readiness === 'PARTIAL' ? PauseCircle : AlertTriangle;

  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <Icon className={readiness === 'READY' ? 'text-emerald-300' : readiness === 'PARTIAL' ? 'text-amber-300' : 'text-red-300'} size={27} />
            <StatusBadge status={readiness} tone={toneByReadiness[readiness]} />
          </div>
          <h2 className="mt-4 text-2xl font-black text-white">
            {readiness === 'READY' ? 'Mercado pronto para análise futura.' : 'Contexto de mercado incompleto.'}
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-400">
            O Market Context Engine consolida contexto, disponibilidade e qualidade sem criar indicadores, sinais, pontuações ou candles artificiais.
          </p>
        </div>
      </div>

      {reasons.length > 0 && (
        <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/40 p-4">
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Motivos do bloqueio</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            {reasons.map((reason) => (
              <li key={reason}>• {reason}</li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}
