import { Bell, Brush, Code2, PlugZap, UserCircle } from 'lucide-react';
import Card from '../components/Card';
import EmptyState from '../components/EmptyState';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';

const sections = [
  { label: 'Perfil', icon: UserCircle },
  { label: 'Tema', icon: Brush },
  { label: 'Broker', icon: PlugZap },
  { label: 'API', icon: Code2 },
  { label: 'Notificações', icon: Bell }
];

export default function Settings() {
  return (
    <PageContainer>
      <PageTitle eyebrow="Configurações" title="Settings" />
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {sections.map((section) => (
          <Card key={section.label}>
            <section.icon className="text-cyan-300" size={22} />
            <p className="mt-3 text-sm font-black text-white">{section.label}</p>
            <p className="mt-2 text-xs text-slate-400">Reservado para próxima fase.</p>
          </Card>
        ))}
      </div>
      <EmptyState title="Sem lógica nesta Sprint" message="A estrutura está pronta para receber preferências sem alterar comportamento atual." />
    </PageContainer>
  );
}
