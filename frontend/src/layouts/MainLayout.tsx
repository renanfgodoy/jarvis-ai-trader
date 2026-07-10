import type { ReactNode } from 'react';
import { useState } from 'react';
import Header from '../components/Header/index';
import Sidebar from '../components/Sidebar/index';
import type { AppRoute } from '../hooks/useAppNavigation';
import { usePolariumAccount } from '../hooks/usePolariumAccount';
import { useSystemStatus } from '../hooks/useSystemStatus';

export default function MainLayout({ activeRoute, onNavigate, children }: { activeRoute: AppRoute; onNavigate: (route: AppRoute) => void; children: ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const { health, provider } = useSystemStatus();
  const { polarium } = usePolariumAccount();

  return (
    <div className="min-h-screen bg-[#05051f] text-slate-200">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.12),transparent_28%),radial-gradient(circle_at_top_right,rgba(99,102,241,0.12),transparent_36%),linear-gradient(180deg,#060626,#05051f)]" />
      <div className="flex min-h-screen">
        {mobileNavOpen && <button aria-label="Fechar navegação" className="fixed inset-0 z-20 bg-slate-950/70 lg:hidden" onClick={() => setMobileNavOpen(false)} />}
        <Sidebar activeRoute={activeRoute} onNavigate={onNavigate} mobileOpen={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
        <main className="min-w-0 flex-1">
          <Header health={health.data} provider={provider.data} account={polarium.data} onMenuClick={() => setMobileNavOpen(true)} />
          {children}
        </main>
      </div>
    </div>
  );
}
