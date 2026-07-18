import { TerminalSquare } from 'lucide-react';
import BrandLogo from '../components/BrandLogo';
import ExecutionForm from '../components/core-demo/ExecutionForm';
import ExecutionPanel from '../components/core-demo/ExecutionPanel';
import ExecutionStatsCards from '../components/core-demo/ExecutionStatsCards';
import StatusBadge from '../components/core-demo/StatusBadge';
import SystemStatusCards from '../components/core-demo/SystemStatusCards';
import PageContainer from '../components/PageContainer';
import { useExecution } from '../hooks/useExecution';

export default function CoreDemo() {
  const { loading, response, error, pipeline, history, stats, execute, reset } = useExecution();

  return (
    <PageContainer className="p-4 lg:p-6">
      <div className="mb-5 flex flex-col gap-4 rounded-xl border border-cyan-300/15 bg-white/[0.035] p-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-4">
          <BrandLogo compact />
          <div>
            <p className="flex items-center gap-2 text-xs font-black uppercase tracking-[0.18em] text-cyan-200">
              <TerminalSquare size={15} />
              Friday AI Platform
            </p>
            <h1 className="mt-1 text-2xl font-black text-white">Developer Console</h1>
            <p className="mt-1 max-w-3xl text-sm font-semibold leading-6 text-slate-300">
              Demonstração funcional do fluxo Frontend → Demo Module → Core Orchestrator → Identity → Prompt → Provider Engine → Mock Provider.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={loading ? 'RUNNING' : response ? response.status : 'READY'} />
          <button type="button" onClick={reset} className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-black uppercase tracking-widest text-slate-200 hover:bg-white/10">
            Reset
          </button>
        </div>
      </div>

      <div className="space-y-4">
        <SystemStatusCards loading={loading} response={response} error={error} pipeline={pipeline} />
        <ExecutionStatsCards stats={stats} />
        <ExecutionForm loading={loading} onExecute={execute} />
        <ExecutionPanel response={response} error={error} pipeline={pipeline} history={history} />
      </div>
    </PageContainer>
  );
}
