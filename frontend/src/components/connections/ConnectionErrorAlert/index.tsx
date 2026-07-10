import { AlertTriangle } from 'lucide-react';

export default function ConnectionErrorAlert({ message }: { message?: string | null }) {
  if (!message) return null;

  return (
    <div className="rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4">
      <div className="flex items-center gap-2 text-amber-200">
        <AlertTriangle size={18} />
        <p className="text-[10px] font-black uppercase tracking-widest">Erro sanitizado</p>
      </div>
      <p className="mt-2 text-sm font-semibold text-amber-100/90">{message}</p>
    </div>
  );
}
