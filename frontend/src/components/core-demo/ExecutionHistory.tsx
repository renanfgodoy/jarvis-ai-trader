import type { ExecutionHistoryItem } from '../../types/coreDemo';

export default function ExecutionHistory({ history }: { history: ExecutionHistoryItem[] }) {
  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-black uppercase tracking-[0.18em] text-cyan-200">Ultimas Execucoes</p>
        <span className="rounded-full border border-white/10 bg-black/25 px-2 py-1 text-[10px] font-black uppercase tracking-widest text-slate-300">
          {history.length}/5
        </span>
      </div>

      <div className="mt-4 space-y-2">
        {history.length === 0 && (
          <div className="rounded-lg border border-dashed border-white/10 bg-black/20 p-3 text-sm font-semibold text-slate-400">
            Nenhuma execucao nesta sessao.
          </div>
        )}

        {history.map((item) => (
          <div key={item.id} className="rounded-lg border border-white/10 bg-black/20 p-3 transition hover:border-cyan-300/25 hover:bg-cyan-300/5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-xs font-black uppercase tracking-widest text-white">{item.symbol}</p>
              <span className="text-[11px] font-bold text-slate-400">{new Date(item.time).toLocaleTimeString()}</span>
            </div>
            <div className="mt-2 grid gap-2 text-xs font-semibold text-slate-300 sm:grid-cols-3">
              <span>{item.market}</span>
              <span>{item.strategy}</span>
              <span>{item.decision}{item.confidence !== null ? ` · ${item.confidence}%` : ''}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
