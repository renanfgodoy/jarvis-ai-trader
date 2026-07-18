import { AlertTriangle } from 'lucide-react';

export default function ExecutionError({ message, requestId }: { message: string | null; requestId?: string | null }) {
  if (!message) return null;

  return (
    <section className="rounded-xl border border-red-300/20 bg-red-500/10 p-4">
      <p className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-red-100">
        <AlertTriangle size={16} />
        Execution Error
      </p>
      <p className="mt-2 text-sm font-semibold text-red-50">{message}</p>
      <div className="mt-3 grid gap-2 text-xs font-semibold text-red-100/80">
        <span>Status: ERROR</span>
        <span>Pipeline interrompido</span>
        <span>Timestamp: {new Date().toLocaleString()}</span>
        <span>Request ID: {requestId ?? 'Não disponível'}</span>
      </div>
    </section>
  );
}
