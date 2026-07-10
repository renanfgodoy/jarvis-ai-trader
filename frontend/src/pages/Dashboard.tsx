import { ArrowRight, DatabaseZap, PlugZap, WalletCards } from 'lucide-react';
import { useMarketData } from '../market-data/useMarketData';
import ActionButton from '../components/ActionButton';
import Card from '../components/Card';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';

export default function Dashboard() {
  const marketData = useMarketData();
  const account = marketData.polarium.data;

  return (
    <PageContainer>
      <PageTitle eyebrow="Friday Trade V2" title="Dashboard">
        <StatusBadge status={account?.connected ? 'CONECTADO' : 'NÃO CONECTADO'} tone={account?.connected ? 'success' : 'warning'} />
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <SummaryCard icon={PlugZap} label="Broker" value={marketData.context.broker} />
        <SummaryCard icon={DatabaseZap} label="Ambiente" value={marketData.context.environment} />
        <SummaryCard icon={WalletCards} label="Conta" value={marketData.context.account} />
        <SummaryCard icon={WalletCards} label="Moeda" value={marketData.context.currency} />
      </div>

      <Card>
        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Contexto selecionado</p>
            <h2 className="mt-2 text-2xl font-black text-white">{marketData.context.asset || 'Nenhum ativo selecionado'}</h2>
            <p className="mt-2 text-sm text-slate-400">
              Timeframe {marketData.context.timeframe} · Última atualização {marketData.status.lastUpdate} · Fonte {marketData.source.dataQuality}
            </p>
          </div>
          <ActionButton
            type="button"
            onClick={() => {
              window.history.pushState({}, '', '/markets');
              window.dispatchEvent(new PopStateEvent('popstate'));
            }}
            className="justify-center border-cyan-400/30 text-cyan-100"
          >
            Abrir Markets <ArrowRight size={14} />
          </ActionButton>
        </div>
      </Card>

      <Card>
        <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Dados disponíveis</p>
        <p className="mt-2 text-sm leading-relaxed text-slate-400">
          Candles reais Polarium, timestamp oficial do broker, spread, liquidez e probabilidade de WIN ainda não estão disponíveis. O Friday Trade V2 não inventa esses dados.
        </p>
      </Card>
    </PageContainer>
  );
}

function SummaryCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <Card>
      <Icon className="text-cyan-300" size={22} />
      <p className="mt-3 text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </Card>
  );
}
