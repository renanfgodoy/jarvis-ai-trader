import { Cpu, Radio, ShieldCheck, Wifi } from 'lucide-react';
import type { HealthResponse, ProviderStatus } from '../types/api';

export default function Header({ health, provider }: { health?: HealthResponse; provider?: ProviderStatus }) {
  return (
    <header className="sticky top-0 z-10 border-b border-white/10 bg-slate-950/70 px-6 py-4 backdrop-blur-xl">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-cyan-300">Premium Dashboard V1</p>
          <h2 className="mt-1 text-2xl font-black text-white md:text-3xl">J.A.R.V.I.S AI TRADER</h2>
        </div>
        <div className="flex flex-wrap gap-3">
          <StatusPill icon={Wifi} label="API" value={health?.status ?? 'offline'} ok={health?.status === 'online'} />
          <StatusPill icon={Cpu} label="IA" value="online" ok />
          <StatusPill icon={Radio} label="Provider" value={provider?.provider ?? provider?.active_provider ?? 'simulated'} ok />
          <StatusPill icon={ShieldCheck} label="Execução" value="DEMO" ok />
        </div>
      </div>
    </header>
  );
}

function StatusPill({ icon: Icon, label, value, ok }: { icon: React.ElementType; label: string; value: string; ok?: boolean }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
      <Icon className={ok ? 'text-emerald-300' : 'text-red-300'} size={18} />
      <div>
        <p className="text-[10px] uppercase tracking-widest text-slate-500">{label}</p>
        <p className="text-sm font-bold text-white">{value}</p>
      </div>
    </div>
  );
}
