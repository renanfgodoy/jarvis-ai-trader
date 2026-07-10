import { BarChart3, Bot, CalendarClock, DatabaseZap, LineChart, PlugZap, Radar, Radio, ShieldAlert, Wifi } from 'lucide-react';
import MarketContextCard, { type MarketContextItem } from '../components/market-context/MarketContextCard';
import MarketContextResultPanel, { type MarketContextReadiness } from '../components/market-context/MarketContextResultPanel';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import { useRuntimeMarketContext } from '../hooks/useRuntimeMarketContext';

const unavailable = 'Não disponível';

export default function AIAnalysis() {
  const marketData = useRuntimeMarketContext();
  const hasAsset = Boolean(marketData.context.asset);
  const hasBroker = marketData.context.broker !== unavailable;
  const hasSource = marketData.source.origin !== unavailable;
  const connected = marketData.status.connection === 'Conectado';
  const candlesAvailable = false;
  const scannerAvailable = hasAsset && hasBroker && hasSource && connected;
  const hasKnownUpdate = marketData.status.lastUpdate !== 'Não verificada' && marketData.status.lastUpdate !== unavailable;
  const marketStatus = unavailable;

  const blockingReasons = [
    !hasAsset ? 'sem ativo' : null,
    !hasBroker ? 'sem broker' : null,
    !hasSource ? 'sem fonte' : null,
    !connected ? 'sem conexão' : null,
    !candlesAvailable ? 'sem candles' : null
  ].filter(Boolean) as string[];

  const hardBlocked = !hasAsset || !hasBroker || !hasSource;
  const readiness: MarketContextReadiness = hardBlocked
    ? 'BLOCKED'
    : blockingReasons.length
      ? 'PARTIAL'
      : 'READY';

  const dataQuality = getDataQuality({
    hasAsset,
    hasBroker,
    hasSource,
    connected,
    candlesAvailable
  });

  const aiEngineStatus = readiness === 'READY' ? 'Preparado' : readiness === 'PARTIAL' ? 'Aguardando' : 'Bloqueado';

  const items: MarketContextItem[] = [
    {
      label: 'Status do mercado',
      value: marketStatus,
      detail: 'Abertura/fechamento não está disponível no contexto desta tela.',
      tone: 'neutral',
      icon: BarChart3
    },
    {
      label: 'Fonte dos dados',
      value: hasSource ? marketData.source.origin : 'Desconhecida',
      detail: 'Fonte recebida do contexto atual, sem fallback inventado.',
      tone: hasSource ? 'success' : 'danger',
      icon: DatabaseZap
    },
    {
      label: 'Qualidade dos dados',
      value: dataQuality,
      detail: 'Qualidade calculada apenas pela presença dos dados reais exigidos.',
      tone: dataQuality === 'Excelente' ? 'success' : dataQuality === 'Parcial' ? 'warning' : 'danger',
      icon: ShieldAlert
    },
    {
      label: 'Conexão',
      value: connected ? 'Conectado' : 'Desconectado',
      detail: marketData.source.connectorStatus,
      tone: connected ? 'success' : 'danger',
      icon: Wifi
    },
    {
      label: 'Candles',
      value: candlesAvailable ? 'Disponível' : unavailable,
      detail: 'Nenhuma quantidade de candles é inferida sem dado real.',
      tone: candlesAvailable ? 'success' : 'warning',
      icon: LineChart
    },
    {
      label: 'Scanner',
      value: scannerAvailable ? 'Disponível' : 'Bloqueado',
      detail: scannerAvailable ? 'Contexto mínimo presente para futura leitura.' : 'Scanner não é liberado sem ativo, broker, fonte e conexão.',
      tone: scannerAvailable ? 'success' : 'warning',
      icon: Radar
    },
    {
      label: 'AI Engine',
      value: aiEngineStatus,
      detail: 'A engine de IA ainda não é executada nesta Sprint.',
      tone: readiness === 'READY' ? 'success' : readiness === 'PARTIAL' ? 'warning' : 'danger',
      icon: Bot
    },
    {
      label: 'Última atualização',
      value: marketData.status.lastUpdate,
      detail: hasKnownUpdate ? 'Timestamp conhecido recebido do estado atual.' : 'Nenhum timestamp real disponível.',
      tone: hasKnownUpdate ? 'success' : 'warning',
      icon: CalendarClock
    }
  ];

  return (
    <PageContainer>
      <PageTitle eyebrow="Friday Trade V2" title="Market Context Engine">
        <StatusBadge status={readiness} tone={readiness === 'READY' ? 'success' : readiness === 'PARTIAL' ? 'warning' : 'danger'} />
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-6">
        <Summary label="Ativo" value={marketData.context.asset || 'Não selecionado'} />
        <Summary label="Broker" value={marketData.context.broker} />
        <Summary label="Conta" value={marketData.context.account} />
        <Summary label="Ambiente" value={marketData.context.environment} />
        <Summary label="Timeframe" value={marketData.context.timeframe || 'Não definido'} />
        <Summary label="Última atualização" value={marketData.status.lastUpdate} />
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {items.map((item) => (
          <MarketContextCard key={item.label} item={item} />
        ))}
      </div>

      <MarketContextResultPanel readiness={readiness} reasons={blockingReasons} />
    </PageContainer>
  );
}

function getDataQuality({
  hasAsset,
  hasBroker,
  hasSource,
  connected,
  candlesAvailable
}: {
  hasAsset: boolean;
  hasBroker: boolean;
  hasSource: boolean;
  connected: boolean;
  candlesAvailable: boolean;
}) {
  if (hasAsset && hasBroker && hasSource && connected && candlesAvailable) return 'Excelente';
  if (hasAsset && hasBroker && hasSource && connected) return 'Parcial';
  if (hasAsset && hasBroker && hasSource) return 'Parcial';
  return 'Insuficiente';
}

function Summary({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
      <div className="flex items-center gap-2 text-slate-500">
        <PlugZap size={14} />
        <p className="text-[10px] font-black uppercase tracking-widest">{label}</p>
      </div>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </div>
  );
}
