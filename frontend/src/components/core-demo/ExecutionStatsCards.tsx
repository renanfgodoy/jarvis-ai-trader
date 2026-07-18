import type { ExecutionStats } from '../../types/coreDemo';

function formatLatency(value: number | null) {
  if (value === null) return 'Aguardando';
  return `${(value * 1000).toFixed(0)} ms`;
}

function formatLastExecution(value: string | null) {
  if (!value) return 'Nenhuma';
  return new Date(value).toLocaleTimeString();
}

export default function ExecutionStatsCards({ stats }: { stats: ExecutionStats }) {
  return (
    <section className="grid gap-3 sm:grid-cols-3">
      <StatCard label="Execucoes" value={String(stats.count)} detail="desde abertura" />
      <StatCard label="Tempo Medio" value={formatLatency(stats.averageLatency)} detail={stats.latencyClassification} />
      <StatCard label="Ultima Execucao" value={formatLastExecution(stats.lastExecutionAt)} detail="sessao atual" />
    </section>
  );
}

function StatCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.035] p-4 transition hover:border-cyan-300/25 hover:bg-cyan-300/5">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-black text-white">{value}</p>
      <p className="mt-1 text-xs font-bold uppercase tracking-widest text-cyan-200">{detail}</p>
    </div>
  );
}
