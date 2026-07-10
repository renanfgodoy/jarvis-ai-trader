import { ShieldCheck } from 'lucide-react';
import type { MarketDiscoveryReadiness } from '../../../intelligence/types';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export default function MarketReadinessCard({ readiness }: { readiness: MarketDiscoveryReadiness }) {
  const copy = {
    ready: {
      status: 'READY',
      tone: 'success' as const,
      title: 'Discovery completo',
      message: 'Dados mínimos disponíveis para alimentar uma futura camada de IA.'
    },
    partial: {
      status: 'PARCIAL',
      tone: 'warning' as const,
      title: 'Discovery parcial',
      message: 'Mercado disponível, mas a conexão da conta ainda não está completa.'
    },
    blocked: {
      status: 'BLOQUEADO',
      tone: 'danger' as const,
      title: 'Discovery incompleto',
      message: 'Ainda não existem dados suficientes para formar um snapshot confiável.'
    }
  }[readiness];

  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <ShieldCheck className="text-cyan-300" size={24} />
        <StatusBadge status={copy.status} tone={copy.tone} />
      </div>
      <h3 className="mt-5 text-lg font-black text-white">{copy.title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">{copy.message}</p>
      <p className="mt-4 text-[11px] leading-relaxed text-slate-500">Esta Sprint apenas observa o mercado. Não há decisão, recomendação, indicador, AutoTrade ou execução.</p>
    </Card>
  );
}
