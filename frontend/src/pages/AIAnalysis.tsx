import { BarChart3, CalendarClock, DatabaseZap, LineChart, Link2, PlugZap, Radio, Timer, WalletCards } from 'lucide-react';
import ReadinessCheckCard, { type ReadinessCheck } from '../components/analysis/ReadinessCheckCard';
import ReadinessResultPanel, { type AnalysisReadinessState } from '../components/analysis/ReadinessResultPanel';
import Card from '../components/Card';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import { useRuntimeMarketContext } from '../hooks/useRuntimeMarketContext';

const minimumCandles = 100;
const unavailable = 'Não disponível';

export default function AIAnalysis() {
  const marketData = useRuntimeMarketContext();
  const hasAsset = Boolean(marketData.context.asset);
  const hasTimeframe = Boolean(marketData.context.timeframe);
  const hasBroker = marketData.context.broker !== unavailable;
  const hasSource = marketData.source.origin !== unavailable;
  const connected = marketData.status.connection === 'Conectado';
  const candlesAvailable = false;
  const candlesCount: number | null = null;
  const hasKnownUpdate = marketData.status.lastUpdate !== 'Não verificada' && marketData.status.lastUpdate !== unavailable;

  const hardBlockers = [
    !hasAsset ? 'Ativo não selecionado.' : null,
    !hasTimeframe ? 'Timeframe não definido.' : null,
    !hasBroker ? 'Broker indisponível.' : null,
    !hasSource ? 'Fonte de dados indisponível.' : null
  ].filter(Boolean) as string[];

  const partialBlockers = [
    !connected ? 'Conexão desconectada.' : null,
    !candlesAvailable ? 'Candles não disponíveis.' : null,
    candlesCount === null ? 'Quantidade atual de candles indisponível.' : null,
    !hasKnownUpdate ? 'Última atualização não verificada.' : null
  ].filter(Boolean) as string[];

  const readiness: AnalysisReadinessState = hardBlockers.length
    ? 'NOT READY'
    : partialBlockers.length
      ? 'PARTIAL'
      : 'READY';

  const checks: ReadinessCheck[] = [
    {
      label: 'Ativo selecionado',
      value: hasAsset ? marketData.context.asset : 'Não selecionado',
      detail: hasAsset ? 'Ativo recebido do contexto compartilhado de Markets.' : 'Selecione um ativo válido em Markets.',
      status: hasAsset ? 'ok' : 'blocked',
      icon: BarChart3
    },
    {
      label: 'Timeframe',
      value: hasTimeframe ? marketData.context.timeframe : 'Não definido',
      detail: hasTimeframe ? 'Timeframe permitido para a Sprint atual.' : 'Escolha M1, M5 ou M15 em Markets.',
      status: hasTimeframe ? 'ok' : 'blocked',
      icon: Timer
    },
    {
      label: 'Broker',
      value: hasBroker ? 'Disponível' : 'Indisponível',
      detail: marketData.context.broker,
      status: hasBroker ? 'ok' : 'blocked',
      icon: PlugZap
    },
    {
      label: 'Fonte dos dados',
      value: hasSource ? marketData.source.origin : 'Indisponível',
      detail: 'Nenhuma fonte alternativa é inferida nesta Sprint.',
      status: hasSource ? 'ok' : 'blocked',
      icon: DatabaseZap
    },
    {
      label: 'Conexão',
      value: connected ? 'Conectado' : 'Desconectado',
      detail: marketData.source.connectorStatus,
      status: connected ? 'ok' : 'warning',
      icon: Link2
    },
    {
      label: 'Candles disponíveis',
      value: candlesAvailable ? 'Disponível' : unavailable,
      detail: 'Nenhum endpoint de candles reais foi consumido por esta tela.',
      status: candlesAvailable ? 'ok' : 'warning',
      icon: LineChart
    },
    {
      label: 'Quantidade mínima',
      value: candlesCount === null ? `Necessário ${minimumCandles} candles · Atual indisponível` : `Necessário ${minimumCandles} candles · Atual ${candlesCount}`,
      detail: 'A quantidade atual não é inventada quando o dado não existe.',
      status: candlesCount !== null && candlesCount >= minimumCandles ? 'ok' : 'warning',
      icon: Radio
    },
    {
      label: 'Última atualização',
      value: marketData.status.lastUpdate,
      detail: hasKnownUpdate ? 'Timestamp conhecido recebido do estado de conexão.' : 'Nenhum timestamp real disponível.',
      status: hasKnownUpdate ? 'ok' : 'warning',
      icon: CalendarClock
    }
  ];

  const reasons = readiness === 'READY' ? [] : [...hardBlockers, ...partialBlockers];

  return (
    <PageContainer>
      <PageTitle eyebrow="Friday Trade V2" title="AI Analysis">
        <StatusBadge status={readiness} tone={readiness === 'READY' ? 'success' : readiness === 'PARTIAL' ? 'warning' : 'danger'} />
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <Summary label="Ativo" value={marketData.context.asset || 'Não selecionado'} />
        <Summary label="Timeframe" value={marketData.context.timeframe || 'Não definido'} />
        <Summary label="Broker" value={marketData.context.broker} />
        <Summary label="Conta" value={marketData.context.account} />
        <Summary label="Ambiente" value={marketData.context.environment} />
      </div>

      <Card>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Checklist</p>
            <h2 className="mt-1 text-xl font-black text-white">Podemos analisar este ativo?</h2>
          </div>
          <WalletCards className="text-cyan-300" size={22} />
        </div>
      </Card>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {checks.map((check) => (
          <ReadinessCheckCard key={check.label} check={check} />
        ))}
      </div>

      <ReadinessResultPanel state={readiness} reasons={reasons} />
    </PageContainer>
  );
}

function Summary({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </div>
  );
}
