import { Activity } from 'lucide-react';
import { brand } from '../../branding/brand';

export default function BrandLogo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3" aria-label={brand.logo.ariaLabel}>
      <div
        className="relative flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-2xl border shadow-glow"
        style={{
          borderColor: `${brand.colors.primary}55`,
          background: `linear-gradient(145deg, ${brand.colors.surfaceElevated}, ${brand.colors.background})`,
          color: brand.colors.primary
        }}
      >
        <div className="absolute inset-0 opacity-70" style={{ background: `radial-gradient(circle at 30% 20%, ${brand.colors.primary}44, transparent 46%)` }} />
        <Activity className="relative" size={24} />
        <span className="absolute bottom-1 right-1 h-2 w-2 rounded-full bg-white shadow-[0_0_16px_rgba(255,255,255,0.85)]" />
      </div>
      {!compact && (
        <div>
          <h1 className="text-lg font-black tracking-[0.22em] text-white">{brand.logo.wordmark}</h1>
          <p className="text-xs font-bold uppercase text-cyan-300">{brand.logo.descriptor}</p>
        </div>
      )}
    </div>
  );
}
