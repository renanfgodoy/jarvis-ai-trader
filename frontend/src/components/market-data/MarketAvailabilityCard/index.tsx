import type { MarketAvailability } from '../../../market-data/types';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export default function MarketAvailabilityCard({ availability }: { availability: MarketAvailability }) {
  const rows = [
    ['Total de ativos', String(availability.totalAssets)],
    ['Ativos abertos', String(availability.openAssets)],
    ['Ativos fechados', String(availability.closedAssets)],
    ['Status do ativo', availability.selectedAssetStatus]
  ];

  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Disponibilidade</p>
          <h3 className="mt-1 text-lg font-black text-white">Estado observável</h3>
        </div>
        <StatusBadge status={availability.selectedAssetAvailable ? 'DISPONÍVEL' : 'NÃO DISPONÍVEL'} tone={availability.selectedAssetAvailable ? 'success' : 'warning'} />
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {rows.map(([label, value]) => (
          <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
            <p className="mt-2 text-sm font-black text-white">{value}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
