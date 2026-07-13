import { Menu } from 'lucide-react';
import { brand } from '../../branding/brand';

export default function Header({
  onMenuClick
}: {
  onMenuClick?: () => void;
}) {
  return (
    <header className="sticky top-0 z-10 border-b border-cyan-400/10 bg-[#060725]/88 px-4 py-3 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button onClick={onMenuClick} className="rounded-xl border border-white/10 bg-white/[0.035] p-2 text-slate-300 lg:hidden">
            <Menu size={20} />
          </button>
          <div>
            <p className="text-[11px] uppercase tracking-[0.36em] text-cyan-300">{brand.shortName}</p>
            <h2 className="mt-1 text-xl font-black tracking-wide text-white md:text-2xl">Simulação</h2>
          </div>
        </div>
      </div>
    </header>
  );
}
