import { Clock3, Menu, Radio, ShieldCheck, UserCircle, Wifi } from 'lucide-react';
import { brand } from '../../branding/brand';
import type { HealthResponse, MarketAssetsResponse, PolariumAccountState, ProviderStatus } from '../../types/api';
import StatusBadge from '../StatusBadge';

export default function Header({
  health,
  provider,
  marketAssets,
  account,
  onMenuClick
}: {
  health?: HealthResponse;
  provider?: ProviderStatus;
  marketAssets?: MarketAssetsResponse;
  account?: PolariumAccountState;
  onMenuClick?: () => void;
}) {
  const time = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  const connected = Boolean(account?.connected);

  return (
    <header className="sticky top-0 z-10 border-b border-cyan-400/10 bg-[#060725]/88 px-5 py-3 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button onClick={onMenuClick} className="rounded-xl border border-white/10 bg-white/[0.035] p-2 text-slate-300 lg:hidden">
            <Menu size={20} />
          </button>
          <div>
            <p className="text-[11px] uppercase tracking-[0.36em] text-cyan-300">{brand.name}</p>
            <h2 className="mt-1 text-2xl font-black tracking-wide text-white md:text-3xl">{provider?.provider ?? provider?.active_provider ?? brand.shortName}</h2>
          </div>
        </div>
        <div className="hidden flex-wrap items-center gap-3 xl:flex">
          <StatusPill icon={Wifi} label="API" value={health?.status ?? 'offline'} ok={health?.status === 'online'} />
          <StatusPill icon={Radio} label="Provider" value={provider?.provider ?? provider?.active_provider ?? 'Não disponível'} ok={Boolean(provider?.provider ?? provider?.active_provider)} />
          <StatusPill icon={Radio} label="Dados" value={marketAssets?.data_quality ?? 'Não disponível'} ok={marketAssets?.data_quality === 'REAL'} />
          <StatusPill icon={ShieldCheck} label="Conta" value={account?.account_mode ?? 'N/D'} ok={connected} />
          <StatusPill icon={ShieldCheck} label="Moeda" value={account?.currency ?? 'N/D'} ok={Boolean(account?.currency)} />
          <StatusBadge status={connected ? 'CONECTADO' : 'OFFLINE'} tone={connected ? 'success' : 'warning'} />
          <div className="rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-2.5">
            <div className="flex items-center gap-2 text-slate-400"><Clock3 size={14} /><span className="text-[10px] uppercase tracking-widest">Hora local</span></div>
            <p className="text-lg font-black text-white">{time}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-2.5">
            <div className="flex items-center gap-2 text-slate-400"><UserCircle size={14} /><span className="text-[10px] uppercase tracking-widest">Usuário</span></div>
            <p className="text-sm font-black text-white">{brand.operatorName}</p>
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
