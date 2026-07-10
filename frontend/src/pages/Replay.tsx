import { Plus } from 'lucide-react';
import ActionButton from '../components/ActionButton';
import Card from '../components/Card';
import EmptyState from '../components/EmptyState';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';

export default function Replay() {
  return (
    <PageContainer>
      <PageTitle eyebrow="Friday Trade V2" title="Replay" />

      <Card>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Registro manual</p>
            <h2 className="mt-1 text-xl font-black text-white">Nenhuma análise registrada.</h2>
          </div>
          <ActionButton type="button" className="border-cyan-400/30 text-cyan-100">
            <Plus size={14} /> Novo Registro
          </ActionButton>
        </div>
      </Card>

      <EmptyState title="Replay em preparação" message="A estrutura local está pronta para registrar WIN, LOSS ou NÃO ENTREI em uma Sprint futura, sem executar ordens." />
    </PageContainer>
  );
}
