import { Activity, Server, Wifi } from 'lucide-react';
import Card from '../components/Card';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import PolariumDiagnosticsPanel from '../components/PolariumDiagnosticsPanel';
import { useSystemStatus } from '../hooks/useSystemStatus';

export default function Diagnostics() {
  const { health, provider } = useSystemStatus();

  return (
    <PageContainer>
      <PageTitle eyebrow="Diagnósticos" title="System Diagnostics">
        <StatusBadge status={health.data?.status ?? 'OFFLINE'} tone={health.data?.status === 'online' ? 'success' : 'danger'} />
      </PageTitle>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <DiagnosticCard icon={Server} label="Backend" value={health.data?.status ?? 'offline'} />
        <DiagnosticCard icon={Wifi} label="Connector" value={provider.data?.provider ?? provider.data?.active_provider ?? 'Não disponível'} />
        <DiagnosticCard icon={Activity} label="Frontend" value="online" />
      </div>
      <PolariumDiagnosticsPanel />
      <Card>
        <p className="eyebrow">Logs</p>
        <p className="mt-2 text-sm text-slate-400">Logs operacionais permanecem no backend e no console do navegador. Esta página reserva o painel central de observabilidade.</p>
      </Card>
    </PageContainer>
  );
}

function DiagnosticCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <Card>
      <Icon className="text-cyan-300" size={22} />
      <p className="mt-3 text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-black text-white">{value}</p>
    </Card>
  );
}
