import BrandLogo from '../components/BrandLogo';
import Card from '../components/Card';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import { brand } from '../branding/brand';

const colorLabels: Array<[keyof typeof brand.colors, string]> = [
  ['background', 'Background'],
  ['surface', 'Surface'],
  ['primary', 'Primary'],
  ['primaryStrong', 'Primary Strong'],
  ['text', 'Text'],
  ['success', 'Success'],
  ['warning', 'Warning'],
  ['danger', 'Danger']
];

export default function Branding() {
  return (
    <PageContainer>
      <PageTitle eyebrow="Desenvolvimento" title="Branding Foundation" />

      <div className="grid gap-4 xl:grid-cols-[1fr_1.4fr]">
        <Card>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <BrandLogo />
            <StatusBadge status="TEMPORÁRIO" tone="warning" />
          </div>
          <div className="mt-6 space-y-3">
            <IdentityRow label="Nome" value={brand.name} />
            <IdentityRow label="Subtítulo" value={brand.subtitle} />
            <IdentityRow label="Versão" value={`v${brand.version}`} />
            <IdentityRow label="Ambiente" value={brand.environment} />
          </div>
        </Card>

        <Card>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Cores principais</p>
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
      </div>

      <section>
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-cyan-300">Naming Lab</p>
            <h2 className="mt-1 text-xl font-black text-white">Sugestões para a marca futura</h2>
          </div>
          <StatusBadge status="NÃO OFICIAL" tone="neutral" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {brand.nameSuggestions.map((suggestion) => (
            <Card key={suggestion.name}>
              <p className="text-lg font-black text-white">{suggestion.name}</p>
              <p className="mt-3 text-sm leading-relaxed text-slate-400">{suggestion.concept}</p>
            </Card>
          ))}
        </div>
      </section>
    </PageContainer>
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
