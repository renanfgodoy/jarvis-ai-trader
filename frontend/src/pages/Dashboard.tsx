import type { ElementType } from 'react';
import { Activity, BarChart3, BrainCircuit, RadioTower, TimerReset } from 'lucide-react';
import Card from '../components/Card';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import RealCandleChart from '../components/chart/RealCandleChart';
import { useRealCandles } from '../hooks/useRealCandles';

export default function Dashboard() {
  const series = useRealCandles();
  const latest = series.candles[series.candles.length - 1];
  const sourceOnline = series.bridgeOnline && series.source === 'POLARIUM AUTHORIZED BROWSER LIVE';

  return (
    <PageContainer>
      <PageTitle eyebrow="Friday Trade V4" title="Real-Time Trading Dashboard">
        <StatusBadge status={sourceOnline ? 'ONLINE' : 'AGUARDANDO DADOS'} tone={sourceOnline ? 'success' : 'warning'} />
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <InfoCard icon={RadioTower} label="Live Source" value={series.source} status={sourceOnline ? 'ONLINE' : 'DISCONNECTED'} tone={sourceOnline ? 'success' : 'warning'} />
        <InfoCard icon={BarChart3} label="Ativo" value={series.assetLabel} detail={series.activeIdsSeen.length ? `Observados: ${series.activeIdsSeen.join(', ')}` : 'Aguardando Browser Bridge'} />
        <InfoCard icon={TimerReset} label="Timeframe" value={series.timeframeLabel} detail={series.rawSize ? `raw_size ${series.rawSize}` : 'Não disponível'} />
        <InfoCard icon={Activity} label="Pipeline" value={series.pipelineOnline ? 'ONLINE' : 'AGUARDANDO'} detail={`Sucessos: ${series.pipelineSuccessCount}`} tone={series.pipelineOnline ? 'success' : 'warning'} />
      </div>

      <div className="grid gap-3 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,0.7fr)]">
        <Card className="p-0">
          {series.activeId && series.rawSize ? (
            <RealCandleChart activeId={series.activeId} rawSize={series.rawSize} candles={series.candles} />
          ) : (
            <div className="flex min-h-[620px] items-center justify-center px-6 text-center">
              <div>
                <p className="text-lg font-black text-white">Aguardando candles reais da Polarium.</p>
                <p className="mt-2 max-w-xl text-sm leading-relaxed text-slate-400">
                  Abra a Polarium com a extensão ativa. O Dashboard detectará automaticamente active_id e raw_size pelo fluxo oficial do Browser Bridge ao CandleStore.
                </p>
              </div>
            </div>
          )}
        </Card>

        <div className="space-y-3">
          <Card>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Último Candle</p>
            {latest ? (
              <div className="mt-4 grid grid-cols-2 gap-3">
                <Value label="Open" value={formatPrice(latest.open)} />
                <Value label="High" value={formatPrice(latest.high)} />
                <Value label="Low" value={formatPrice(latest.low)} />
                <Value label="Close" value={formatPrice(latest.close)} />
                <div className="col-span-2">
                  <Value label="Timestamp" value={formatTimestamp(latest.time)} />
                </div>
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-400">Nenhum candle salvo no CandleStore para a série ativa.</p>
            )}
          </Card>

          <Card>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Pipeline</p>
            <div className="mt-4 grid gap-2">
              <Stage label="Bridge" online={series.bridgeOnline} />
              <Stage label="Pipeline" online={series.pipelineOnline} />
              <Stage label="Store" online={series.storeOnline} />
              <Stage label="Chart" online={series.chartOnline} />
            </div>
            <p className="mt-4 text-xs leading-relaxed text-slate-400">
              Último evento: <b className="text-slate-200">{series.lastEventName ?? 'Não disponível'}</b>
              {series.lastEventAt ? ` · ${formatDateTime(series.lastEventAt)}` : ''}
            </p>
          </Card>

          <Card>
            <div className="flex items-center gap-2">
              <BrainCircuit size={18} className="text-cyan-300" />
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">AI Readiness</p>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2">
              <Placeholder label="Trend" />
              <Placeholder label="Momentum" />
              <Placeholder label="Volatility" />
              <Placeholder label="Signal" />
            </div>
          </Card>

          {series.error && (
            <Card className="border-red-400/20 bg-red-500/5">
              <p className="text-sm font-black text-red-200">Falha de leitura</p>
              <p className="mt-2 text-xs text-red-100/80">{series.error}</p>
            </Card>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

function InfoCard({
  icon: Icon,
  label,
  value,
  detail,
  status,
  tone = 'neutral'
}: {
  icon: ElementType;
  label: string;
  value: string;
  detail?: string;
  status?: string;
  tone?: 'success' | 'warning' | 'neutral';
}) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <Icon className="shrink-0 text-cyan-300" size={22} />
        {status && <StatusBadge status={status} tone={tone} />}
      </div>
      <p className="mt-3 text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
      {detail && <p className="mt-2 text-xs leading-relaxed text-slate-400">{detail}</p>}
    </Card>
  );
}

function Value({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.035] p-3">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-1 break-words text-sm font-black text-white">{value}</p>
    </div>
  );
}

function Stage({ label, online }: { label: string; online: boolean }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2">
      <span className="text-sm font-bold text-slate-200">{label}</span>
      <StatusBadge status={online ? 'ONLINE' : 'WAITING'} tone={online ? 'success' : 'warning'} />
    </div>
  );
}

function Placeholder({ label }: { label: string }) {
  return (
    <div className="rounded-xl border border-dashed border-cyan-400/20 bg-cyan-400/[0.035] p-3">
      <p className="text-[10px] font-black uppercase tracking-widest text-cyan-200">{label}</p>
      <p className="mt-1 text-xs text-slate-400">Placeholder</p>
    </div>
  );
}

function formatPrice(value: number) {
  return value.toFixed(value > 10 ? 2 : 5);
}

function formatTimestamp(value: number) {
  return String(value);
}

function formatDateTime(value: string) {
  try {
    return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'medium' }).format(new Date(value));
  } catch {
    return value;
  }
}
