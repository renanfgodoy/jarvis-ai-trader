import { ShieldCheck } from 'lucide-react';
import type { RiskCheck } from '../types/api';

export default function RiskCard({ risk, compact = false }: { risk?: RiskCheck; compact?: boolean }) {
  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] uppercase tracking-[0.25em] text-emerald-300">Risk Manager</p>
          <h3 className="mt-1 text-base font-black text-white">Proteção da Banca</h3>
        </div>
        <ShieldCheck className="text-emerald-300" size={20} />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
        <Info label="Banca" value={`R$ ${(risk?.bankroll ?? 200).toFixed(2)}`} />
        <Info label="Entrada" value={`R$ ${(risk?.recommended_entry ?? 10).toFixed(2)}`} />
        <Info label="Risco" value={`${risk?.risk_score ?? 0}/100`} />
        <Info label="Status" value={risk?.decision ?? (risk?.allowed ? 'APPROVED' : 'WAIT')} />
      </div>

      {!compact && (
        <div className="mt-5 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4 text-sm text-emerald-100">
          {risk?.official_rule ?? 'Primeiro proteger a banca. Depois crescer a banca.'}
        </div>
      )}
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-[10px] uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-black text-white">{value}</p>
    </div>
  );
}
