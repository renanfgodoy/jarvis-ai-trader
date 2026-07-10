import { AlertTriangle, CheckCircle2, PauseCircle } from 'lucide-react';
import ActionButton from '../../ActionButton';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export type AnalysisReadinessState = 'READY' | 'PARTIAL' | 'NOT READY';

const stateTone = {
  READY: 'success',
  PARTIAL: 'warning',
  'NOT READY': 'danger'
} as const;

export default function ReadinessResultPanel({
  state,
  reasons
}: {
  state: AnalysisReadinessState;
  reasons: string[];
}) {
  const Icon = state === 'READY' ? CheckCircle2 : state === 'PARTIAL' ? PauseCircle : AlertTriangle;

  return (
    <Card>
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <Icon className={state === 'READY' ? 'text-emerald-300' : state === 'PARTIAL' ? 'text-amber-300' : 'text-red-300'} size={26} />
            <StatusBadge status={state} tone={stateTone[state]} />
          </div>
          <h2 className="mt-4 text-2xl font-black text-white">
            {state === 'READY' ? 'Sistema pronto para análise.' : 'Análise indisponível.'}
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-slate-400">
            {state === 'READY'
              ? 'Engine de IA será implementada em Sprint futura.'
              : 'O Friday Trade só libera análise quando os pré-requisitos mínimos estiverem confirmados por dados reais.'}
          </p>
        </div>

        <ActionButton type="button" disabled={state !== 'READY'} className="justify-center border-cyan-400/30 text-cyan-100 disabled:opacity-50">
          Iniciar Análise
        </ActionButton>
      </div>

      {reasons.length > 0 && (
        <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/40 p-4">
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Motivos</p>
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
