import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import RealCandleChart from '../components/chart/RealCandleChart';
import { brand } from '../branding/brand';
import { useRealCandles } from '../hooks/useRealCandles';

export default function MarketChart() {
  const series = useRealCandles();

  return (
    <PageContainer>
      <PageTitle eyebrow={brand.name} title="Real Candle Chart">
        <StatusBadge status="PASSIVO" tone="neutral" />
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-3">
        <Metric label="Origem" value={series.source} />
        <Metric label="Active ID" value={String(series.activeId)} />
        <Metric label="Raw Size" value={String(series.rawSize)} />
      </div>

      <RealCandleChart activeId={series.activeId} rawSize={series.rawSize} candles={series.candles} />
    </PageContainer>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </div>
  );
}
