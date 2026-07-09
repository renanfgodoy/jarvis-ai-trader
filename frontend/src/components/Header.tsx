import { Clock3, Cpu, Menu, Radio, ShieldCheck, Wifi } from 'lucide-react';
import type { HealthResponse, MarketAssetsResponse, ProviderStatus } from '../types/api';

export default function Header({ health, provider, marketAssets }: { health?: HealthResponse; provider?: ProviderStatus; marketAssets?: MarketAssetsResponse }) {
  const time = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

  return (
    <header className="sticky top-0 z-10 border-b border-cyan-400/10 bg-[#060725]/88 px-5 py-3 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button className="rounded-xl border border-white/10 bg-white/[0.035] p-2 text-slate-300 lg:hidden">
            <Menu size={20} />
          </button>
          <div>
            <p className="text-[11px] uppercase tracking-[0.42em] text-cyan-300">Premium Dashboard V2</p>
            <h2 className="mt-1 text-2xl font-black tracking-wide text-white md:text-3xl">J.A.R.V.I.S AI TRADER</h2>
          </div>
        </div>
        <div className="hidden flex-wrap items-center gap-3 xl:flex">
          <StatusPill icon={Wifi} label="API" value={health?.status ?? 'offline'} ok={health?.status === 'online'} />
          <StatusPill icon={Cpu} label="IA" value="online" ok />
          <StatusPill icon={Radio} label="Provider" value={provider?.provider ?? provider?.active_provider ?? 'simulated'} ok />
          <StatusPill icon={Radio} label="Dados" value={marketAssets?.data_quality ?? 'SIMULATED'} ok={marketAssets?.data_quality === 'REAL'} />
          <StatusPill icon={ShieldCheck} label="Execução" value="DEMO" ok />
          <div className="rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-2.5">
            <div className="flex items-center gap-2 text-slate-400"><Clock3 size={14} /><span className="text-[10px] uppercase tracking-widest">Hora local</span></div>
            <p className="text-lg font-black text-white">{time}</p>
          </div>
        </div>
      </div>
    </header>
  );
}

function StatusPill({ icon: Icon, label, value, ok }: { icon: React.ElementType; label: string; value: string; ok?: boolean }) {
  return (
    <div className="min-w-[132px] rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-2.5">
      <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-slate-500">
        <Icon className={ok ? 'text-emerald-300' : 'text-red-300'} size={14} />
        {label}
      </div>
      <p className={`mt-1 text-sm font-black uppercase ${ok ? 'text-emerald-300' : 'text-red-300'}`}>{value}</p>
    </div>
  );
}
