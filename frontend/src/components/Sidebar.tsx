import {
  BarChart3,
  Bot,
  Brain,
  History,
  LayoutDashboard,
  LifeBuoy,
  LineChart,
  Radar,
  Settings,
  Shield,
  Wallet
} from 'lucide-react';
import { brand } from '../branding/brand';
import BrandLogo from './BrandLogo';

const items = [
  { label: 'Dashboard', icon: LayoutDashboard, active: true },
  { label: 'Scanner', icon: Radar },
  { label: 'Mercado', icon: BarChart3 },
  { label: 'Gráfico', icon: LineChart },
  { label: 'IA Decision', icon: Brain },
  { label: 'Execução', icon: Bot },
  { label: 'Risco', icon: Shield },
  { label: 'Histórico', icon: History },
  { label: 'Configurações', icon: Settings }
];

export default function Sidebar() {
  return (
    <aside className="hidden h-screen w-[260px] shrink-0 border-r border-cyan-400/10 bg-[#07082a]/95 p-4 lg:flex lg:flex-col">
      <div className="flex items-center gap-3 border-b border-white/10 pb-4">
        <BrandLogo />
      </div>

      <div className="mt-6 rounded-2xl border border-white/10 bg-white/[0.035] p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-cyan-400 text-slate-950 shadow-[0_0_30px_rgba(34,211,238,0.5)]">
            <Wallet size={22} />
          </div>
          <div>
            <p className="text-base font-black text-white">{brand.operatorName}</p>
            <p className="text-xs uppercase tracking-widest text-slate-400">Conta Polarium</p>
          </div>
        </div>
        <div className="mt-4 rounded-xl border border-white/10 bg-[#0b0b3a]/80 p-3">
          <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">Saldo demo</p>
          <p className="mt-1 text-2xl font-black text-white">R$ 200,00</p>
          <div className="mt-3 rounded-lg border border-cyan-400/30 py-2 text-center text-xs font-black text-cyan-300">Conta DEMO</div>
        </div>
      </div>

      <nav className="mt-5 space-y-1.5">
        {items.map((item) => (
          <button
            key={item.label}
            className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-semibold transition ${
              item.active
                ? 'border border-cyan-400/40 bg-cyan-400/15 text-cyan-200 shadow-glow'
                : 'text-slate-300 hover:bg-white/5 hover:text-white'
            }`}
          >
            <item.icon size={17} />
            {item.label}
          </button>
        ))}
      </nav>

      <div className="mt-auto rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4">
        <div className="flex items-center gap-3 text-cyan-200">
          <LifeBuoy size={22} />
          <div>
            <p className="text-sm font-black">Suporte 24/7</p>
            <p className="text-xs text-slate-400">Precisa de ajuda?</p>
          </div>
        </div>
      </div>
      <p className="mt-4 text-xs tracking-widest text-slate-500">v{brand.version}</p>
    </aside>
  );
}
