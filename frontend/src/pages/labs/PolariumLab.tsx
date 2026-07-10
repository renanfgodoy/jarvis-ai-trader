import { FlaskConical, ShieldAlert } from 'lucide-react';
import Card from '../../components/Card';
import PageContainer from '../../components/PageContainer';
import PageTitle from '../../components/PageTitle';
import PolariumDirectLoginLabPanel from '../../components/PolariumDirectLoginLabPanel';
import PolariumOAuthLabPanel from '../../components/PolariumOAuthLabPanel';
import PolariumSessionInspectorPanel from '../../components/PolariumSessionInspectorPanel';
import PolariumWsRecorderPanel from '../../components/PolariumWsRecorderPanel';

export default function PolariumLab() {
  return (
    <PageContainer>
      <PageTitle eyebrow="Desenvolvimento" title="Polarium Lab" />
      <Card className="border-amber-400/25 bg-amber-400/[0.06]">
        <div className="flex items-start gap-3 text-amber-100">
          <ShieldAlert className="mt-1 text-amber-300" size={24} />
          <div>
            <p className="text-sm font-black uppercase tracking-widest">AMBIENTE DE DESENVOLVIMENTO</p>
            <p className="mt-2 text-sm leading-relaxed text-amber-100/80">
              Ferramentas técnicas para OAuth, direct login, Session Inspector e WS Recorder. Não executam ordens e não participam do fluxo operacional.
            </p>
          </div>
        </div>
      </Card>
      <div className="grid gap-3 xl:grid-cols-2">
        <PolariumOAuthLabPanel />
        <PolariumDirectLoginLabPanel />
        <PolariumSessionInspectorPanel />
        <PolariumWsRecorderPanel />
      </div>
      <Card>
        <p className="flex items-center gap-2 text-sm font-black text-cyan-200"><FlaskConical size={18} /> Laboratórios isolados</p>
        <p className="mt-2 text-sm text-slate-400">Esta área existe para investigação controlada. Prints compartilhados devem mascarar qualquer token, cookie ou sessão.</p>
      </Card>
    </PageContainer>
  );
}
