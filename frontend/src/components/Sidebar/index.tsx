import { BrainCircuit, History, Home, Settings, ShieldCheck, TerminalSquare } from 'lucide-react';
import type { AppRoute } from '../../hooks/useAppNavigation';
import BrandLogo from '../BrandLogo';

const navigation: Array<{ route: AppRoute; label: string; icon: React.ElementType; group?: string }> = [
  { route: '/dashboard', label: 'Dashboard', icon: Home },
  { route: '/vision', label: 'Friday Vision', icon: BrainCircuit },
  { route: '/history', label: 'Histórico', icon: History },
  { route: '/risk', label: 'Gestão de Risco', icon: ShieldCheck },
  { route: '/developer/core-demo', label: 'Developer Console', icon: TerminalSquare },
  { route: '/settings', label: 'Settings', icon: Settings }
];

export default function Sidebar({
  activeRoute,
  onNavigate,
  mobileOpen = false,
  onClose
}: {
  activeRoute: AppRoute;
  onNavigate: (route: AppRoute) => void;
  mobileOpen?: boolean;
  onClose?: () => void;
}) {
  return (
    <aside className={`${mobileOpen ? 'fixed inset-y-0 left-0 z-30 flex' : 'hidden'} h-screen w-[272px] shrink-0 flex-col border-r border-cyan-400/10 bg-[#07082a]/95 p-4 lg:static lg:z-auto lg:flex`}>
      <div className="flex items-center gap-3 border-b border-white/10 pb-4">
        <BrandLogo />
      </div>

      <nav className="mt-5 space-y-1.5">
        {navigation.map((item, index) => (
          <div key={item.route}>
            {item.group && (index === 0 || navigation[index - 1].group !== item.group) && (
              <p className="mb-2 mt-5 px-3 text-[10px] font-black uppercase tracking-[0.24em] text-slate-500">{item.group}</p>
            )}
            <button
              type="button"
              onClick={() => {
                onNavigate(item.route);
                onClose?.();
              }}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-semibold transition ${
                activeRoute === item.route
                  ? 'border border-cyan-400/40 bg-cyan-400/15 text-cyan-200 shadow-glow'
                  : 'text-slate-300 hover:bg-white/5 hover:text-white'
              }`}
            >
              <item.icon size={17} />
              {item.label}
            </button>
          </div>
        ))}
      </nav>
      <div className="mt-auto" />
    </aside>
  );
}
