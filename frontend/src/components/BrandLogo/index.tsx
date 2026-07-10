import { brand } from '../../branding/brand';

export default function BrandLogo({
  compact = false,
  className = ''
}: {
  compact?: boolean;
  className?: string;
}) {
  return (
    <div className={`flex items-center gap-3 ${className}`} aria-label={brand.logo.ariaLabel}>
      <img
        src={brand.assets.symbol}
        alt={brand.icon.ariaLabel}
        className="h-12 w-12 shrink-0 rounded-2xl"
        width={48}
        height={48}
      />
      {!compact && (
        <div className="min-w-0">
          <h1 className="truncate text-lg font-black tracking-[0.12em] text-white">{brand.name}</h1>
          <p className="truncate text-xs font-bold text-cyan-300">{brand.tagline}</p>
        </div>
      )}
    </div>
  );
}
