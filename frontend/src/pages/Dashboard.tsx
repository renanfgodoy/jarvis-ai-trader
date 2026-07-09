import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Bell, Bot, CircleDot, Download, TrendingUp } from 'lucide-react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import TopAssets from '../components/TopAssets';
import AIStatus from '../components/AIStatus';
import MarketIntelligencePanel from '../components/MarketIntelligencePanel';
import ChartCard from '../components/ChartCard';
import RiskCard from '../components/RiskCard';
import Timeline from '../components/Timeline';
import TimeframeControl from '../components/TimeframeControl';
import { checkAutoTradeGate, getCurrentProvider, getExecutionStatus, getHealth, getMarketAssets, getMarketIntelligence, getMarketIntelligenceTop, getRiskCheck, getSignalAnalysis } from '../services/api';
import type { AccountCurrency, AssetScannerResult, Timeframe } from '../types/api';

export default function Dashboard() {
  const [selectedSymbol, setSelectedSymbol] = useState('EURUSD-OTC');
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe | null>(null);
  const [autoTradeEnabled, setAutoTradeEnabled] = useState(false);
  const [accountCurrency, setAccountCurrency] = useState<AccountCurrency>('BRL');
  const entryValue = accountCurrency === 'BRL' ? 10 : 1;
  const activeTimeframe = selectedTimeframe ?? 'M1';

  const health = useQuery({ queryKey: ['health'], queryFn: getHealth, refetchInterval: 5000 });
  const provider = useQuery({ queryKey: ['provider'], queryFn: getCurrentProvider, refetchInterval: 5000 });
  const marketAssets = useQuery({ queryKey: ['market-assets'], queryFn: getMarketAssets, refetchInterval: 5000 });
  const scanner = useQuery({
    queryKey: ['scanner', activeTimeframe],
    queryFn: () => getMarketIntelligenceTop(activeTimeframe),
    refetchInterval: 3000,
    enabled: Boolean(selectedTimeframe)
  });
  const risk = useQuery({ queryKey: ['risk', accountCurrency, entryValue], queryFn: () => getRiskCheck(accountCurrency, entryValue), refetchInterval: 5000 });
  const execution = useQuery({ queryKey: ['execution'], queryFn: getExecutionStatus, refetchInterval: 3000 });

  const assetMeta = useMemo(() => new Map((marketAssets.data?.assets ?? []).map((asset) => [asset.symbol, asset])), [marketAssets.data]);
  const assets = useMemo(() => (scanner.data?.results ?? []).map((asset, index) => ({
    rank: index + 1,
    symbol: asset.symbol,
    timeframe: asset.timeframe,
    signal: asset.signal,
    score: asset.score,
    risk_level: asset.risk_bias,
    status: asset.status,
    trend: asset.trend,
    volatility: asset.volatility,
    reasons: asset.reasons,
    payout: asset.payout,
    data_quality: assetMeta.get(asset.symbol)?.data_quality ?? marketAssets.data?.data_quality ?? 'SIMULATED',
    market_status: assetMeta.get(asset.symbol)?.status ?? 'OPEN'
  })), [scanner.data, assetMeta]);
  const selectedAsset = useMemo(() => {
    return assets.find((asset) => asset.symbol === selectedSymbol) ?? assets[0] ?? fallbackAsset;
  }, [assets, selectedSymbol]);
  const activeSymbol = selectedAsset.symbol ?? selectedSymbol;
  const signal = useQuery({
    queryKey: ['signal', activeSymbol, activeTimeframe],
    queryFn: () => getSignalAnalysis(activeSymbol, activeTimeframe),
    refetchInterval: 5000,
    enabled: Boolean(selectedTimeframe)
  });

  const intelligence = useQuery({
    queryKey: ['market-intelligence', activeSymbol, activeTimeframe],
    queryFn: () => getMarketIntelligence(activeSymbol, activeTimeframe),
    refetchInterval: 5000,
    enabled: Boolean(selectedTimeframe)
  });

  const gate = useQuery({
    queryKey: ['autotrade-gate', activeSymbol, selectedTimeframe, accountCurrency, entryValue, autoTradeEnabled, selectedAsset.score, risk.data?.allowed, execution.data?.status],
    queryFn: () => checkAutoTradeGate({
      symbol: activeSymbol,
      timeframe: selectedTimeframe,
      account_type: 'DEMO',
      currency: accountCurrency,
      balance: 200,
      entry_value: entryValue,
      score: Math.round(selectedAsset.score ?? 0),
      minimum_score: 80,
      risk_approved: Boolean(risk.data?.allowed ?? true),
      websocket_online: true,
      execution_ready: (execution.data?.status ?? 'READY') === 'READY',
      asset_valid: Boolean(activeSymbol),
      autotrade_requested: autoTradeEnabled
    }),
    refetchInterval: 2500
  });

  return (
    <div className="min-h-screen bg-[#05051f] text-slate-200">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.12),transparent_28%),radial-gradient(circle_at_top_right,rgba(99,102,241,0.12),transparent_36%),linear-gradient(180deg,#060626,#05051f)]" />
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <Header health={health.data} provider={provider.data} marketAssets={marketAssets.data} />
          <section className="mx-auto max-w-[1960px] space-y-3 p-3 2xl:p-4">
            <TimeframeControl
              selected={selectedTimeframe}
              onSelect={(tf) => {
                setSelectedTimeframe(tf);
                // Safety rule: timeframe selection starts analysis immediately; changing TF pauses execution mode.
                setAutoTradeEnabled(false);
              }}
              autoTradeEnabled={autoTradeEnabled}
              onToggleAutoTrade={() => setAutoTradeEnabled((current) => !current)}
              gateStatus={gate.data?.status}
            />

            <TopAssets
              assets={assets}
              selectedSymbol={activeSymbol}
              onSelect={setSelectedSymbol}
              dataQuality={marketAssets.data?.data_quality ?? 'SIMULATED'}
              totalAssets={marketAssets.data?.total_assets ?? 0}
              openAssets={marketAssets.data?.open_assets ?? 0}
            />

            <TradeCommandBar
              selectedAsset={selectedAsset}
              timeframe={selectedTimeframe}
              countdown={gate.data?.status ?? 'WAITING'}
              autoTradeEnabled={autoTradeEnabled}
              gateAllowed={Boolean(gate.data?.allowed)}
            />

            <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_330px] 2xl:grid-cols-[minmax(0,1fr)_360px]">
              <div className="min-w-0 space-y-3">
                <ChartCard symbol={activeSymbol} timeframe={activeTimeframe} selectedAsset={selectedAsset} autotradeEnabled={autoTradeEnabled} />
                <div className="grid gap-3 xl:grid-cols-[1.05fr_0.9fr_1.25fr]">
                  <TradingManagement selectedAsset={selectedAsset} timeframe={selectedTimeframe} currency={accountCurrency} setCurrency={setAccountCurrency} entryValue={entryValue} gateAllowed={Boolean(gate.data?.allowed)} />
                  <StatsPanel />
                  <CompactLog />
                </div>
              </div>
              <aside className="space-y-3 xl:sticky xl:top-3 xl:self-start">
                <MarketIntelligencePanel intelligence={intelligence.data} enabled={Boolean(selectedTimeframe)} />
                <RiskCard risk={risk.data} compact />
                <ExecutionPanel status={execution.data?.status ?? 'READY'} mode={execution.data?.mode ?? 'DEMO'} executions={execution.data?.executions ?? 0} gateStatus={gate.data?.status ?? 'WAITING'} />
                <GatePanel reasons={gate.data?.reasons ?? []} warnings={gate.data?.warnings ?? []} />
              </aside>
            </div>

            <div className="grid gap-3 xl:grid-cols-[1fr_1fr]">
              <Timeline />
              <RecentOperations />
            </div>

            <InstallPanel />
          </section>
        </main>
      </div>
    </div>
  );
}

function TradeCommandBar({ selectedAsset, timeframe, countdown, autoTradeEnabled, gateAllowed }: { selectedAsset: AssetScannerResult; timeframe: Timeframe | null; countdown: string; autoTradeEnabled: boolean; gateAllowed: boolean }) {
  const signal = selectedAsset.signal === 'SELL' || selectedAsset.signal === 'PUT' ? 'SELL' : selectedAsset.signal === 'BUY' || selectedAsset.signal === 'CALL' ? 'BUY' : 'WAIT';
  return (
    <div className="panel command-bar px-4 py-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xl font-black text-white">{selectedAsset.symbol}</span>
          <span className="command-chip">{timeframe ?? 'TF?'}</span>
          <span className={`command-chip ${signal === 'BUY' ? 'chip-buy' : signal === 'SELL' ? 'chip-sell' : ''}`}>{signal}</span>
          <span className="command-chip">Score {Math.round(selectedAsset.score ?? 0)}%</span>
          <span className="command-chip">Payout {Math.round((selectedAsset as any).payout ?? 0)}%</span>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs font-black uppercase tracking-widest">
          <span className={gateAllowed ? 'text-emerald-300' : 'text-amber-300'}>Gate: {countdown}</span>
          <span className={autoTradeEnabled ? 'text-emerald-300' : 'text-slate-400'}>AutoTrade {autoTradeEnabled ? 'ON' : 'OFF'}</span>
        </div>
      </div>
    </div>
  );
}

function CompactLog() {
  const lines = [
    ['Agora', 'Scanner ativo'],
    ['Agora', 'IA recalculando confluência'],
    ['Agora', 'Risk Manager aguardando gate'],
    ['Agora', 'Execution em DEMO']
  ];
  return (
    <div className="panel p-3">
      <p className="eyebrow">Log operacional</p>
      <div className="mt-3 space-y-2 text-xs">
        {lines.map(([time, text]) => (
          <div key={text} className="flex items-center justify-between gap-3 rounded-xl border border-white/5 bg-white/[0.025] px-3 py-2">
            <span className="text-cyan-300">{time}</span>
            <b className="text-slate-200">{text}</b>
          </div>
        ))}
      </div>
    </div>
  );
}

function TradingManagement({ selectedAsset, timeframe, currency, setCurrency, entryValue, gateAllowed }: { selectedAsset: AssetScannerResult; timeframe: Timeframe | null; currency: AccountCurrency; setCurrency: (currency: AccountCurrency) => void; entryValue: number; gateAllowed: boolean }) {
  return (
    <div className="panel p-3">
      <p className="eyebrow">Trading Panel</p>
      <h3 className="mt-1 text-sm font-black text-white">{selectedAsset.symbol} · {timeframe ?? 'Selecione M1/M5/M15'}</h3>
      <div className="mt-3 grid grid-cols-4 gap-2 text-center">
        <Info label="Moeda" value={currency} color="cyan" />
        <Info label="Entrada" value={`${currency === 'BRL' ? 'R$' : 'US$'}${entryValue}`} color="cyan" />
        <Info label="Mínimo" value={currency === 'BRL' ? 'R$5' : 'US$1'} color="amber" />
        <Info label="Gate" value={gateAllowed ? 'OK' : 'WAIT'} color={gateAllowed ? 'green' : 'amber'} />
      </div>
      <div className="mt-3 flex gap-2">
        <button onClick={() => setCurrency('BRL')} className={`toolbar-btn ${currency === 'BRL' ? 'border-cyan-400/40 text-cyan-200' : ''}`}>Conta BRL</button>
        <button onClick={() => setCurrency('USD')} className={`toolbar-btn ${currency === 'USD' ? 'border-cyan-400/40 text-cyan-200' : ''}`}>Conta USD</button>
      </div>
      <p className="mt-3 text-[11px] text-slate-500">DEMO obrigatório. Timeframe analisa automaticamente; AutoTrade só executa se o gate aprovar.</p>
    </div>
  );
}

function StatsPanel() {
  return (
    <div className="panel grid grid-cols-2 gap-4 p-4 text-center">
      <div className="flex flex-col items-center justify-center">
        <CircleDot className="text-cyan-300" size={28} />
        <p className="mt-3 text-3xl font-black text-white">48%</p>
        <p className="text-xs text-slate-500">Taxa de acerto demo</p>
      </div>
      <div className="flex flex-col items-center justify-center">
        <TrendingUp className="text-cyan-300" size={28} />
        <p className="mt-3 text-3xl font-black text-white">75</p>
        <p className="text-xs text-slate-500">Operações simuladas</p>
      </div>
    </div>
  );
}

function ExecutionPanel({ status, mode, executions, gateStatus }: { status: string; mode: string; executions: number; gateStatus: string }) {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">Execution</p>
          <h3 className="mt-1 text-base font-black text-white">Controle DEMO</h3>
        </div>
        <Bot className="text-cyan-300" size={20} />
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2">
        <Info label="Status" value={status} color="cyan" />
        <Info label="Modo" value={mode} color="amber" />
        <Info label="Gate" value={gateStatus} />
        <Info label="Conta" value="DEMO" color="green" />
      </div>
    </div>
  );
}

function Info({ label, value, color = 'white' }: { label: string; value: string | number; color?: 'white' | 'cyan' | 'amber' | 'green' }) {
  const colors = { white: 'text-white', cyan: 'text-cyan-300', amber: 'text-amber-300', green: 'text-emerald-300' };
  return <div className="rounded-xl border border-white/10 bg-white/[0.035] p-3"><p className="text-[10px] uppercase tracking-widest text-slate-500">{label}</p><p className={`mt-1 text-base font-black ${colors[color]}`}>{value}</p></div>;
}

function GatePanel({ reasons, warnings }: { reasons: string[]; warnings: string[] }) {
  const messages = [...reasons, ...warnings].slice(0, 6);
  return <div className="panel p-4"><p className="eyebrow">AutoTrade Gate</p><div className="mt-3 space-y-2 text-xs text-slate-300">{messages.length ? messages.map((item) => <p key={item}>• {item}</p>) : <p>Selecione M1/M5/M15 para analisar. AutoTrade fica separado e só libera execução quando o gate aprovar.</p>}</div></div>;
}

function RecentOperations() {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between"><p className="eyebrow">Operações Recentes</p><a className="text-sm font-black text-cyan-300">Ver todas →</a></div>
      <div className="mt-3 grid grid-cols-4 gap-2 text-xs text-slate-400">
        <span>Horário</span><span>Ativo</span><span>IA</span><span>Resultado</span>
        <b className="text-slate-200">--:--</b><b className="text-slate-200">Aguardando</b><b className="text-cyan-300">DEMO</b><b className="text-amber-300">Pendente</b>
      </div>
    </div>
  );
}

function InstallPanel() {
  return <div className="panel flex items-center justify-between p-4"><div><p className="eyebrow">J.A.R.V.I.S AI TRADER</p><p className="mt-2 text-sm text-slate-400">V0.17.0 · Professional Trading Workspace.</p></div><button className="toolbar-btn"><Download size={16} /> Instalar PWA</button></div>;
}

const fallbackAsset: AssetScannerResult = { rank: 1, symbol: 'EURUSD-OTC', signal: 'BUY', score: 94, risk_level: 'LOW', status: 'APPROVED' };
