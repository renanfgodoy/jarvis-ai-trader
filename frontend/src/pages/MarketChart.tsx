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
        <Metric label="Active ID" value={series.activeId ? String(series.activeId) : 'Não disponível'} />
        <Metric label="Raw Size" value={series.rawSize ? String(series.rawSize) : 'Não disponível'} />
      </div>

      {series.activeId && series.rawSize ? (
        <RealCandleChart activeId={series.activeId} rawSize={series.rawSize} candles={series.candles} />
      ) : (
        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-8 text-center">
          <p className="text-sm font-black text-white">Aguardando série ativa do Browser Bridge.</p>
          <p className="mt-2 text-xs text-slate-400">
            O gráfico será carregado quando active_id e raw_size existirem no fluxo oficial.
          </p>
        </div>
      )}
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
