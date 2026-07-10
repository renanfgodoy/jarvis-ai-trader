import Card from '../components/Card';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import { useMarketData } from '../market-data/useMarketData';

export default function AIAnalysis() {
  const marketData = useMarketData();
  const hasAsset = Boolean(marketData.context.asset);

  return (
    <PageContainer>
      <PageTitle eyebrow="Friday Trade V2" title="AI Analysis">
        <StatusBadge status="PREPARADO" tone="neutral" />
      </PageTitle>

      <Card>
        <h2 className="text-xl font-black text-white">Aguardando dados do mercado.</h2>
        <p className="mt-3 text-sm leading-relaxed text-slate-400">
          {hasAsset ? 'Contexto recebido de Markets. A engine de decisão ainda não foi implementada.' : 'Selecione um ativo em Markets para iniciar.'}
        </p>
      </Card>

      {hasAsset && (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          <Info label="Ativo" value={marketData.context.asset} />
          <Info label="Timeframe" value={marketData.context.timeframe} />
          <Info label="Broker" value={marketData.context.broker} />
          <Info label="Ambiente" value={marketData.context.environment} />
          <Info label="Origem" value={marketData.source.dataQuality} />
        </div>
      )}

      <Card>
        <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Limites atuais</p>
        <p className="mt-2 text-sm text-slate-400">Sem sinais, indicadores, probabilidades ou recomendações nesta Sprint.</p>
      </Card>
    </PageContainer>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </Card>
  );
}
