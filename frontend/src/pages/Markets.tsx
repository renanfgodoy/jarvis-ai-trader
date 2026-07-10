import { useEffect, useMemo, useState } from 'react';
import { ArrowRight, CheckCircle2, Clock3, DatabaseZap, Search } from 'lucide-react';
import WatchlistWidget from '../components/markets/WatchlistWidget';
import ActionButton from '../components/ActionButton';
import Card from '../components/Card';
import ChartCard from '../components/ChartCard';
import EmptyState from '../components/EmptyState';
import Loading from '../components/Loading';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import TopAssets from '../components/TopAssets';
import { brand } from '../branding/brand';
import { useMarketScanner } from '../hooks/useMarketScanner';
import { useMarketStatus, type MarketWorkspaceTimeframe } from '../hooks/useMarketStatus';
import { useWatchlist } from '../hooks/useWatchlist';
import { useMarketDataContext } from '../market-data/MarketDataContext';
import type { AssetScannerResult, MarketAsset } from '../types/api';

const timeframes: MarketWorkspaceTimeframe[] = ['M1', 'M5', 'M15'];

function normalizeAsset(symbol: string) {
  return symbol.trim().toUpperCase();
}

function isValidOperationalAsset(asset: MarketAsset) {
  return asset.status === 'OPEN' && asset.is_tradable;
}

export default function Markets() {
  const marketContext = useMarketDataContext();
  const [assetDraft, setAssetDraft] = useState(marketContext.asset);

  const market = useMarketStatus(marketContext.timeframe);
  const allAssets = market.marketAssets.data?.assets ?? [];
  const validAssets = useMemo(() => allAssets.filter(isValidOperationalAsset), [allAssets]);
  const selectedAsset = validAssets.find((asset) => asset.symbol === marketContext.asset);
  const hasValidAsset = Boolean(selectedAsset);
  const scanner = useMarketScanner(marketContext.timeframe, hasValidAsset);
  const watchlist = useWatchlist(validAssets);

  useEffect(() => {
    setAssetDraft(marketContext.asset);
  }, [marketContext.asset]);

  const topAssets = useMemo<AssetScannerResult[]>(() => validAssets.slice(0, 12).map((asset, index) => ({
    rank: index + 1,
    symbol: asset.symbol,
    timeframe: marketContext.timeframe,
    status: asset.status,
    payout: asset.payout,
    data_quality: asset.data_quality,
    market_status: asset.status
  })), [marketContext.timeframe, validAssets]);

  const draftSymbol = normalizeAsset(assetDraft);
  const draftMatch = validAssets.find((asset) => asset.symbol === draftSymbol);
  const currentMarket = market.marketAssets.data?.data_quality ?? 'Não disponível';
  const broker = market.provider.data?.provider ?? market.provider.data?.active_provider ?? market.marketAssets.data?.provider ?? 'Não disponível';
  const account = market.polarium.data?.email_masked ?? 'Não disponível';
  const environment = market.polarium.data ? (market.polarium.data.demo_only === false ? 'REAL' : 'DEMO') : 'Não disponível';
  const connectionStatus = market.polarium.data?.connected ? 'Conectado' : 'Não conectado';

  const selectAsset = (symbol: string) => {
    const normalized = normalizeAsset(symbol);
    const match = validAssets.find((asset) => asset.symbol === normalized);
    if (!match) return;
    setAssetDraft(match.symbol);
    marketContext.setAsset(match.symbol);
  };

  const handleDraftChange = (value: string) => {
    const normalized = normalizeAsset(value);
    setAssetDraft(normalized);
    if (marketContext.asset && normalized !== marketContext.asset) {
      marketContext.setAsset('');
    }
  };

  const analyzeAsset = () => {
    if (!hasValidAsset) return;
    window.history.pushState({}, '', '/analysis');
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <PageContainer>
      <PageTitle eyebrow={brand.name} title="Markets">
        <StatusBadge status={hasValidAsset ? 'ATIVO VALIDADO' : 'AGUARDANDO ATIVO'} tone={hasValidAsset ? 'success' : 'neutral'} />
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <HeaderMetric label="Broker" value={broker} />
        <HeaderMetric label="Conta" value={account} />
        <HeaderMetric label="Ambiente" value={environment} />
        <HeaderMetric label="Status" value={connectionStatus} />
        <HeaderMetric label="Última atualização" value={market.lastUpdated} />
      </div>

      {(market.loading || scanner.isLoading) && <Loading label="Carregando dados de mercado" />}

      <Card>
        <div className="grid gap-4 xl:grid-cols-[minmax(260px,1fr)_auto_auto] xl:items-end">
          <div>
            <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Pesquisar ativo</label>
            <div className="mt-2 flex items-center gap-2 rounded-2xl border border-white/10 bg-slate-950/40 px-3 py-2">
              <Search className="shrink-0 text-cyan-300" size={18} />
              <input
                className="min-w-0 flex-1 bg-transparent text-sm font-black uppercase text-white outline-none placeholder:text-slate-600"
                value={assetDraft}
                onChange={(event) => handleDraftChange(event.target.value)}
                placeholder="Ex: USDCHF-OTC"
              />
              {draftMatch && <CheckCircle2 className="shrink-0 text-emerald-300" size={18} />}
            </div>
            <p className={`mt-2 text-xs ${draftSymbol && !draftMatch ? 'text-amber-300' : 'text-slate-500'}`}>
              {draftSymbol && !draftMatch ? 'Ativo não encontrado, fechado ou indisponível para operação.' : 'Digite o símbolo exato ou escolha um card abaixo.'}
            </p>
          </div>

          <div>
            <p className="mb-2 text-[10px] font-black uppercase tracking-widest text-slate-500">Timeframe</p>
            <div className="flex flex-wrap items-center gap-2">
              {timeframes.map((timeframe) => (
                <button
                  key={timeframe}
                  type="button"
                  onClick={() => marketContext.setTimeframe(timeframe)}
                  className={`inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-xs font-black transition ${
                    marketContext.timeframe === timeframe
                      ? 'border-cyan-400/50 bg-cyan-400/20 text-cyan-200'
                      : 'border-white/10 bg-white/[0.035] text-slate-400 hover:bg-white/[0.06]'
                  }`}
                >
                  <Clock3 size={14} /> {timeframe}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <ActionButton
              type="button"
              disabled={!draftMatch}
              onClick={() => draftMatch && selectAsset(draftMatch.symbol)}
              className="justify-center border-white/10 text-slate-200 disabled:opacity-50"
            >
              Usar Ativo
            </ActionButton>
            <ActionButton
              type="button"
              disabled={!hasValidAsset}
              onClick={analyzeAsset}
              className="justify-center border-cyan-400/30 text-cyan-100 disabled:opacity-50"
            >
              Analisar Ativo <ArrowRight size={14} />
            </ActionButton>
          </div>
        </div>
      </Card>

      <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_360px]">
        {topAssets.length ? (
          <TopAssets
            assets={topAssets}
            selectedSymbol={marketContext.asset}
            onSelect={selectAsset}
            dataQuality={currentMarket}
            totalAssets={market.marketAssets.data?.total_assets ?? topAssets.length}
            openAssets={market.marketAssets.data?.open_assets ?? topAssets.length}
          />
        ) : (
          <EmptyState title="Nenhum ativo válido disponível." message="A fonte atual não retornou ativos abertos e tradáveis para o Top 12." />
        )}
        <WatchlistWidget items={watchlist.items} onSelect={(symbol) => {
          watchlist.setSelectedSymbol(symbol);
          selectAsset(symbol);
        }} />
      </div>

      {hasValidAsset ? (
        <ChartCard symbol={selectedAsset?.symbol ?? marketContext.asset} timeframe={marketContext.timeframe} />
      ) : (
        <EmptyState title="Selecione um ativo para iniciar a análise." message="O gráfico e o WebSocket permanecem desligados até um ativo válido ser selecionado." />
      )}

      <Card>
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Fonte dos dados</p>
            <h3 className="mt-1 text-lg font-black text-white">Contexto operacional</h3>
          </div>
          <DatabaseZap className="text-cyan-300" size={22} />
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          <SourceMetric label="Broker" value={broker} />
          <SourceMetric label="Origem" value={market.marketAssets.data?.provider ?? 'Não disponível'} />
          <SourceMetric label="Disponibilidade" value={market.marketAssets.data ? `${market.marketAssets.data.open_assets}/${market.marketAssets.data.total_assets} abertos` : 'Não disponível'} />
          <SourceMetric label="Qualidade" value={currentMarket} />
          <SourceMetric label="Atualização" value={market.lastUpdated} />
        </div>
      </Card>
    </PageContainer>
  );
}

function HeaderMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </div>
  );
}

function SourceMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </div>
  );
}
