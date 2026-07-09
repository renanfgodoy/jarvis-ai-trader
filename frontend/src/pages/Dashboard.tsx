import { useQuery } from '@tanstack/react-query';
import { Bell, Bot, CircleDot, Download, Radio, TrendingUp } from 'lucide-react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import TopAssets from '../components/TopAssets';
import AIStatus from '../components/AIStatus';
import ChartCard from '../components/ChartCard';
import RiskCard from '../components/RiskCard';
import Timeline from '../components/Timeline';
import { getCurrentProvider, getExecutionStatus, getHealth, getRiskCheck, getSignalAnalysis, getTopAssets } from '../services/api';
import type { AssetScannerResult } from '../types/api';

export default function Dashboard() {
  const health = useQuery({ queryKey: ['health'], queryFn: getHealth });
  const provider = useQuery({ queryKey: ['provider'], queryFn: getCurrentProvider });
  const scanner = useQuery({ queryKey: ['scanner'], queryFn: getTopAssets, refetchInterval: 3000 });
  const risk = useQuery({ queryKey: ['risk'], queryFn: getRiskCheck });
  const execution = useQuery({ queryKey: ['execution'], queryFn: getExecutionStatus, refetchInterval: 3000 });

  const assets = scanner.data?.top_assets ?? scanner.data?.results ?? [];
  const bestAsset = assets[0] ?? fallbackAsset;
  const signal = useQuery({ queryKey: ['signal', bestAsset.symbol], queryFn: () => getSignalAnalysis(bestAsset.symbol), refetchInterval: 5000 });

  return (
    <div className="min-h-screen bg-[#05051f] text-slate-200">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.16),transparent_32%),radial-gradient(circle_at_top_right,rgba(37,99,235,0.16),transparent_34%),linear-gradient(180deg,#060626,#05051f)]" />
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <Header health={health.data} provider={provider.data} />
          <section className="mx-auto max-w-[1500px] space-y-4 p-4 2xl:p-5">
            <div className="grid gap-4 xl:grid-cols-[1.05fr_1fr_1.15fr]">
              <AssetSelector assets={assets} />
              <TradingManagement />
              <OperationArea />
            </div>

            <div className="grid gap-4 xl:grid-cols-[360px_minmax(0,1fr)]">
              <TopAssets assets={assets} />
              <ChartCard symbol={bestAsset.symbol} />
            </div>

            <div className="grid gap-4 xl:grid-cols-[1fr_1fr_1fr]">
              <StatsPanel />
              <UsersPanel />
              <RiskCard risk={risk.data} />
            </div>

            <div className="grid gap-4 xl:grid-cols-[1fr_1.35fr]">
              <AIStatus signal={signal.data} />
              <ExecutionPanel status={execution.data?.status ?? 'READY'} mode={execution.data?.mode ?? 'DEMO'} executions={execution.data?.executions ?? 0} />
            </div>

            <NewsPanel />
            <RecentOperations />
            <InstallPanel />
            <Timeline />
          </section>
        </main>
      </div>
    </div>
  );
}

function AssetSelector({ assets }: { assets: AssetScannerResult[] }) {
  const top = (assets.length ? assets : [fallbackAsset, { ...fallbackAsset, symbol: 'RAYDIUMUSD-OTC', score: 76 }, { ...fallbackAsset, symbol: 'GOOGLE-OTC', score: 78 }]).slice(0, 3);
  return (
    <div className="panel p-4">
      <p className="eyebrow">Selecionar Ativo</p>
      <h3 className="mt-1 text-base font-black text-white">Top 3 · Criptomoedas</h3>
      <div className="mt-4 grid grid-cols-3 gap-3">
        {top.map((asset, index) => (
          <div key={asset.symbol} className={`rounded-2xl border p-3 text-center ${index === 0 ? 'border-cyan-400/70 bg-cyan-400/10 shadow-glow' : 'border-white/10 bg-white/[0.035]'}`}>
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 text-xl font-black text-white">{asset.symbol[0]}</div>
            <p className="mt-3 min-h-[34px] text-sm font-black text-white">{asset.symbol}</p>
            <p className="text-[11px] text-slate-500">Digital · Aberto</p>
            <p className="mt-2 text-xl font-black text-cyan-300">{Math.round(asset.score ?? 0)}%</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function TradingManagement() {
  return (
    <div className="panel p-4">
      <p className="eyebrow">Gerenciamento de Trading</p>
      <h3 className="mt-1 text-base font-black text-white">Ajuste os parâmetros da IA</h3>
      <label className="mt-4 block text-xs uppercase tracking-widest text-slate-500">Valor</label>
      <div className="mt-2 rounded-xl border border-white/10 bg-[#0b0b35] px-4 py-3 text-lg font-black text-white">R$ 10</div>
      <p className="mt-4 text-xs uppercase tracking-widest text-slate-500">Gales</p>
      <div className="mt-2 grid grid-cols-4 gap-2">
        {[0, 1, 2, 3].map((item) => <button key={item} className={`rounded-xl border py-3 text-sm font-black ${item === 1 ? 'border-cyan-400 bg-cyan-400 text-slate-950' : 'border-white/10 bg-white/[0.035] text-slate-300'}`}>{item}</button>)}
      </div>
      <p className="mt-4 text-xs text-slate-500">Mínimo: R$5,00 · Valor inicial e tentativas de recuperação.</p>
    </div>
  );
}

function OperationArea() {
  return (
    <div className="panel relative overflow-hidden p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">Área de Operação</p>
          <span className="mt-2 inline-flex rounded-full bg-emerald-400/15 px-3 py-1 text-xs font-black text-emerald-300">Sistema ativo</span>
        </div>
        <Bot className="text-cyan-300" />
      </div>
      <div className="mt-5 flex h-[250px] items-center justify-center rounded-2xl border border-white/10 bg-[linear-gradient(135deg,rgba(37,99,235,0.12),rgba(14,165,233,0.06))]">
        <div className="relative flex h-44 w-44 items-center justify-center rounded-full bg-cyan-400/20 shadow-[0_0_80px_rgba(34,211,238,0.45)]">
          <div className="absolute inset-[-22px] rounded-full border border-cyan-300/20" />
          <div className="absolute inset-[-42px] rounded-full border border-blue-500/10" />
          <button className="h-36 w-36 rounded-full bg-gradient-to-br from-cyan-300 to-blue-600 text-center text-xl font-black text-white shadow-[inset_0_0_40px_rgba(255,255,255,0.24)]">
            GERAR SINAL
            <span className="block text-xs font-semibold text-cyan-100">IA Autopilot</span>
          </button>
        </div>
      </div>
    </div>
  );
}

function StatsPanel() {
  return (
    <div className="panel grid grid-cols-2 gap-4 p-5 text-center">
      <div className="flex flex-col items-center justify-center">
        <CircleDot className="text-cyan-300" size={36} />
        <p className="mt-4 text-4xl font-black text-white">48%</p>
        <p className="text-xs text-slate-500">Taxa de acerto</p>
        <div className="mt-3 h-1 w-24 rounded-full bg-slate-800"><div className="h-1 w-1/2 rounded-full bg-cyan-400" /></div>
      </div>
      <div className="flex flex-col items-center justify-center">
        <TrendingUp className="text-cyan-300" size={36} />
        <p className="mt-4 text-4xl font-black text-white">75</p>
        <p className="text-xs text-slate-500">Total de operações</p>
      </div>
    </div>
  );
}

function UsersPanel() {
  return (
    <div className="panel p-5">
      <p className="eyebrow">Usuários Ativos</p>
      <div className="mt-5 flex items-center gap-2">
        <div className="flex -space-x-2">
          {['R', 'J', 'M', 'P', 'C'].map((avatar) => <span key={avatar} className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-950 bg-gradient-to-br from-cyan-400 to-violet-500 text-xs font-black text-white">{avatar}</span>)}
        </div>
        <span className="text-sm font-black text-emerald-300">+864 online agora</span>
      </div>
      <p className="mt-4 text-2xl font-black text-cyan-300">+126 <span className="text-sm font-medium text-slate-400">usuários lucraram nas últimas 24 horas</span></p>
      <div className="mt-4 rounded-xl border border-white/10 bg-white/[0.035] p-3 text-sm text-slate-300">Priscila Freitas resgatou bônus de <b className="float-right text-amber-300">R$ 50,00</b></div>
    </div>
  );
}

function ExecutionPanel({ status, mode, executions }: { status: string; mode: string; executions: number }) {
  return (
    <div className="panel p-5">
      <p className="eyebrow">Execution Engine</p>
      <h3 className="mt-1 text-xl font-black text-white">Controle Operacional</h3>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <Info label="Status" value={status} color="cyan" />
        <Info label="Modo" value={mode} color="amber" />
        <Info label="Execuções" value={executions} />
        <Info label="Conta" value="DEMO" color="green" />
      </div>
    </div>
  );
}

function Info({ label, value, color = 'white' }: { label: string; value: string | number; color?: 'white' | 'cyan' | 'amber' | 'green' }) {
  const colors = { white: 'text-white', cyan: 'text-cyan-300', amber: 'text-amber-300', green: 'text-emerald-300' };
  return <div className="rounded-xl border border-white/10 bg-white/[0.035] p-3"><p className="text-xs text-slate-500">{label}</p><p className={`mt-1 text-lg font-black ${colors[color]}`}>{value}</p></div>;
}

function NewsPanel() {
  return <div className="panel flex items-center justify-between p-5"><div><p className="eyebrow">Notícias · Ao vivo</p><p className="mt-2 text-sm text-slate-300">Dados de inflação podem movimentar o mercado. · Calendário Econômico</p></div><Bell className="text-cyan-300" /></div>;
}

function RecentOperations() {
  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between"><p className="eyebrow">Operações Recentes</p><a className="text-sm font-black text-cyan-300">Ver todas →</a></div>
      <div className="mt-4 flex gap-3 text-xs font-black"><span className="tag-green">✓ 135 Wins</span><span className="tag-red">× 46 Losses</span><span className="tag-blue">R$ 325,91</span></div>
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        {['BTCUSD-OTC-op', 'ETHUSD-OTC', 'SOLUSD-OTC', 'BTCUSD-OTC'].map((item, index) => <div key={item} className="rounded-xl border border-white/10 bg-white/[0.035] p-3"><p className="font-black text-white">{item}</p><p className={index === 3 ? 'mt-3 text-emerald-300' : 'mt-3 text-red-300'}>{index === 3 ? 'Lucro +R$ 161,16' : 'Perda R$ 30,00'}</p></div>)}
      </div>
    </div>
  );
}

function InstallPanel() {
  return <div className="panel flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between"><div className="flex items-center gap-3"><Download className="text-cyan-300" /><div><p className="font-black text-white">Instale Nosso App</p><p className="text-sm text-slate-400">Tenha acesso rápido e notificações em tempo real</p></div></div><div className="grid w-full gap-3 md:w-auto md:grid-cols-2"><button className="rounded-xl border border-white/10 px-12 py-3 font-black text-white">Instalar no iOS</button><button className="rounded-xl border border-white/10 px-12 py-3 font-black text-emerald-300">Instalar no Android</button></div></div>;
}

const fallbackAsset: AssetScannerResult = { rank: 1, symbol: 'GBPUSD-OTC', signal: 'BUY', score: 96, risk_level: 'LOW', status: 'APPROVED' };
