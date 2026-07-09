import { Activity, BarChart3, Bot, Brain, Database, Gauge, History, LayoutDashboard, Radar, Settings, Shield } from 'lucide-react';

const items = [
  { label: 'Dashboard', icon: LayoutDashboard, active: true },
  { label: 'Scanner', icon: Radar },
  { label: 'Mercado', icon: BarChart3 },
  { label: 'IA', icon: Brain },
  { label: 'Execução', icon: Bot },
  { label: 'Risco', icon: Shield },
  { label: 'Histórico', icon: History },
  { label: 'Dados', icon: Database },
  { label: 'Status', icon: Activity },
  { label: 'Configurações', icon: Settings }
];

export default function Sidebar() {
  return (
    <aside className="hidden h-screen w-72 shrink-0 border-r border-white/10 bg-slate-950/80 p-6 lg:block">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-400/15 text-cyan-300 shadow-glow">
          <Gauge size={26} />
        </div>
        <div>
          <h1 className="text-lg font-black tracking-widest text-white">J.A.R.V.I.S</h1>
          <p className="text-xs text-cyan-300">AI TRADER</p>
        </div>
      </div>

      <nav className="mt-10 space-y-2">
        {items.map((item) => (
          <button
            key={item.label}
            className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm transition ${
              item.active
                ? 'border border-cyan-400/30 bg-cyan-400/15 text-cyan-200 shadow-glow'
                : 'text-slate-400 hover:bg-white/5 hover:text-white'
            }`}
          >
            <item.icon size={18} />
            {item.label}
          </button>
        ))}
      </nav>

      <div className="mt-10 rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-4">
        <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">Modo Seguro</p>
        <p className="mt-2 text-sm text-slate-300">Conta DEMO / DRY RUN</p>
        <p className="mt-3 text-xs text-slate-500">Primeiro proteger a banca. Depois crescer a banca.</p>
      </div>
    </aside>
  );
}
