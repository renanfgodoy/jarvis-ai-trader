import { Trash2 } from 'lucide-react';
import type { ConnectionAttempt } from '../../../hooks/useConnectionHistory';
import EmptyState from '../../EmptyState';

export default function ConnectionAttemptHistory({
  attempts,
  onClear
}: {
  attempts: ConnectionAttempt[];
  onClear: () => void;
}) {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Histórico de Tentativas</p>
          <h3 className="mt-1 text-lg font-black text-white">Sessão atual da interface</h3>
        </div>
        <button type="button" onClick={onClear} className="toolbar-btn text-slate-200" disabled={!attempts.length}>
          <Trash2 size={14} /> Limpar
        </button>
      </div>

      <div className="mt-4 space-y-2">
        {attempts.length === 0 ? (
          <EmptyState title="Nenhuma tentativa registrada" message="As ações feitas nesta tela aparecerão aqui sem tokens, cookies, headers ou payloads brutos." />
        ) : attempts.map((attempt) => (
          <div key={attempt.id} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-black text-white">{attempt.action}</p>
              <span className={`text-[10px] font-black uppercase tracking-widest ${resultClass(attempt.result)}`}>{attempt.result}</span>
            </div>
            <p className="mt-1 text-xs text-slate-500">{attempt.time} · {attempt.step}</p>
            <p className="mt-2 text-sm text-slate-300">{attempt.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function resultClass(result: ConnectionAttempt['result']) {
  if (result === 'success') return 'text-emerald-300';
  if (result === 'error') return 'text-red-300';
  return 'text-cyan-300';
}
