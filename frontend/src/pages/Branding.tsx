import BrandLogo from '../components/BrandLogo';
import Card from '../components/Card';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import { brand } from '../branding/brand';

const colorLabels: Array<[keyof typeof brand.colors, string]> = [
  ['background', 'Background'],
  ['surface', 'Surface'],
  ['surfaceElevated', 'Surface Elevated'],
  ['primary', 'Electric Blue'],
  ['primaryStrong', 'Blue Strong'],
  ['text', 'Text'],
  ['success', 'Success/WIN'],
  ['danger', 'Error/LOSS']
];

export default function Branding() {
  return (
    <PageContainer>
      <PageTitle eyebrow="Desenvolvimento" title="Brand Center">
        <StatusBadge status="OFICIAL" tone="success" />
      </PageTitle>

      <div className="grid gap-4 xl:grid-cols-[1fr_1.25fr]">
        <Card>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <BrandLogo />
            <StatusBadge status={brand.tagline} tone="neutral" />
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <IdentityRow label="Nome" value={brand.name} />
            <IdentityRow label="Nome curto" value={brand.shortName} />
            <IdentityRow label="Slogan" value={brand.tagline} />
            <IdentityRow label="Descrição" value={brand.descriptor} />
            <IdentityRow label="Operador" value={brand.operatorName} />
            <IdentityRow label="Versão" value={`v${brand.version}`} />
          </div>
        </Card>

        <Card>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Assets oficiais</p>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <AssetPreview label="Logo principal" src={brand.assets.logo} wide />
            <AssetPreview label="Símbolo" src={brand.assets.symbol} />
            <AssetPreview label="Favicon" src={brand.assets.favicon} />
          </div>
        </Card>
      </div>

      <Card>
        <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Paleta oficial</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {colorLabels.map(([key, label]) => (
            <div key={key} className="rounded-xl border border-white/10 bg-white/[0.025] p-3">
              <div className="h-12 rounded-lg border border-white/10" style={{ backgroundColor: brand.colors[key] }} />
              <p className="mt-3 text-xs font-black text-white">{label}</p>
              <p className="mt-1 font-mono text-[11px] uppercase text-slate-500">{brand.colors[key]}</p>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid gap-4 xl:grid-cols-3">
        <Card>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Tipografia</p>
          <p className="mt-3 text-3xl font-black text-white">{brand.name}</p>
          <p className="mt-2 text-xl font-black text-cyan-300">{brand.tagline}</p>
          <p className="mt-3 text-sm leading-relaxed text-slate-400">{brand.descriptor}</p>
        </Card>
        <Card>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Card institucional</p>
          <div className="mt-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.035] p-4">
            <BrandLogo />
            <p className="mt-4 text-sm text-slate-300">Interface operacional para trading com IA, conectores e segurança em modo DEMO.</p>
          </div>
        </Card>
        <Card>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Aplicação compacta</p>
          <div className="mt-4 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.025] p-4">
            <BrandLogo compact />
            <div>
              <p className="text-sm font-black text-white">{brand.shortName}</p>
              <p className="text-xs text-slate-400">{brand.tagline}</p>
            </div>
          </div>
        </Card>
      </div>
    </PageContainer>
  );
}

function AssetPreview({ label, src, wide = false }: { label: string; src: string; wide?: boolean }) {
  return (
    <div className={`rounded-2xl border border-white/10 bg-white/[0.025] p-4 ${wide ? 'md:col-span-1' : ''}`}>
      <div className="flex h-24 items-center justify-center rounded-xl border border-white/10 bg-[#05070D] p-3">
        <img src={src} alt={`${brand.name} ${label}`} className={wide ? 'max-h-16 max-w-full' : 'h-16 w-16'} />
      </div>
      <p className="mt-3 text-xs font-black text-white">{label}</p>
    </div>
  );
}

function IdentityRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.025] px-4 py-3">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-black text-white">{value}</p>
    </div>
  );
}
