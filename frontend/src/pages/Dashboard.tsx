import { useQuery } from '@tanstack/react-query';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import TopAssets from '../components/TopAssets';
import AIStatus from '../components/AIStatus';
import ChartCard from '../components/ChartCard';
import RiskCard from '../components/RiskCard';
import Timeline from '../components/Timeline';
import MetricCard from '../components/MetricCard';
import { getCurrentProvider, getExecutionStatus, getHealth, getRiskCheck, getSignalAnalysis, getTopAssets } from '../services/api';

export default function Dashboard() {
  const health = useQuery({ queryKey: ['health'], queryFn: getHealth });
  const provider = useQuery({ queryKey: ['provider'], queryFn: getCurrentProvider });
  const scanner = useQuery({ queryKey: ['scanner'], queryFn: getTopAssets });
  const signal = useQuery({ queryKey: ['signal'], queryFn: getSignalAnalysis });
  const risk = useQuery({ queryKey: ['risk'], queryFn: getRiskCheck });
  const execution = useQuery({ queryKey: ['execution'], queryFn: getExecutionStatus });

  const assets = scanner.data?.top_assets ?? scanner.data?.results ?? [];
  const bestAsset = assets[0];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.18),transparent_35%),radial-gradient(circle_at_top_right,rgba(124,58,237,0.18),transparent_35%)]" />
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <Header health={health.data} provider={provider.data} />
          <section className="space-y-6 p-6">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <MetricCard title="Melhor ativo" value={bestAsset?.symbol ?? 'Aguardando'} subtitle="Scanner Top 12" tone="cyan" />
              <MetricCard title="Score" value={`${Math.round(bestAsset?.score ?? 0)}%`} subtitle="Score técnico + risco" tone="green" />
              <MetricCard title="Execuções DEMO" value={execution.data?.executions ?? 0} subtitle={execution.data?.status ?? 'READY'} tone="violet" />
              <MetricCard title="Modo" value={execution.data?.mode ?? 'DEMO'} subtitle="Sem ordens reais" tone="amber" />
            </div>

            <div className="grid gap-6 xl:grid-cols-3">
              <TopAssets assets={assets} />
              <ChartCard />
            </div>

            <div className="grid gap-6 xl:grid-cols-3">
              <AIStatus signal={signal.data} />
              <RiskCard risk={risk.data} />
              <div className="glass-card p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Execution Engine</p>
                <h3 className="mt-1 text-xl font-black text-white">Controle Operacional</h3>
                <div className="mt-5 rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5 text-center">
                  <p className="text-sm text-slate-400">Status</p>
                  <p className="mt-2 text-4xl font-black text-white">{execution.data?.status ?? 'READY'}</p>
                  <p className="mt-2 text-sm text-cyan-200">Conta DEMO / DRY RUN</p>
                </div>
                <p className="mt-5 text-sm text-slate-400">
                  O executor está preparado para simular entradas. Nenhuma ordem real é enviada nesta versão.
                </p>
              </div>
            </div>

            <Timeline />
          </section>
        </main>
      </div>
    </div>
  );
}
