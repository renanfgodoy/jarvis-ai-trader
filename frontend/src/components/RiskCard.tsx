import { ShieldCheck } from 'lucide-react';
import type { RiskCheck } from '../types/api';

export default function RiskCard({ risk }: { risk?: RiskCheck }) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">Risk Manager</p>
          <h3 className="mt-1 text-xl font-black text-white">Proteção da Banca</h3>
        </div>
        <ShieldCheck className="text-emerald-300" />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
        <Info label="Banca" value={`R$ ${(risk?.bankroll ?? 200).toFixed(2)}`} />
        <Info label="Entrada" value={`R$ ${(risk?.recommended_entry ?? 10).toFixed(2)}`} />
        <Info label="Score risco" value={`${risk?.risk_score ?? 0}/100`} />
        <Info label="Status" value={risk?.decision ?? (risk?.allowed ? 'APPROVED' : 'WAIT')} />
      </div>

      <div className="mt-5 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4 text-sm text-emerald-100">
        {risk?.official_rule ?? 'Primeiro proteger a banca. Depois crescer a banca.'}
      </div>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 font-black text-white">{value}</p>
    </div>
  );
}
