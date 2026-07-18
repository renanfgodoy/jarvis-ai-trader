import { AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import type { VisionAnalysisResult, VisionDecision } from '../../types/vision';

export default function VisionAnalysisPanel({ result }: { result: VisionAnalysisResult }) {
  const decision = decisionLabel(result.decision);
  return (
    <section className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.18em] text-cyan-200">Resultado Friday Vision</p>
          <h2 className="mt-1 text-2xl font-black text-white">{decision}</h2>
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
          <Metric label="Confiança visual" value={`${result.confidence}%`} />
          <Metric label="Risco" value={result.risk} />
          <Metric label="Tendência" value={result.trend} />
          <Metric label="Mercado" value={result.market_state} />
        </div>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <Block title="Resumo" text={result.summary} />
        <Block title="Leitura do mercado" text={result.market_reading} />
        <Block title="Condição de entrada" text={result.entry_condition} />
        <Block title="Condição de invalidação" text={result.invalidation_condition} />
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-2">
        <List title="Suportes visuais" items={result.support_zones} />
        <List title="Resistências visuais" items={result.resistance_zones} />
        <List title="Alertas" items={result.warnings} icon="warning" />
        <List title="Limitações" items={result.limitations} icon="limit" />
      </div>

      <p className="mt-4 rounded-lg border border-amber-300/20 bg-amber-300/10 p-3 text-xs font-semibold leading-5 text-amber-100">
        A Friday realiza uma leitura visual do print enviado. A análise não garante resultado e não substitui sua gestão de risco.
      </p>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 px-3 py-2">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-1 whitespace-nowrap text-sm font-black text-white">{value}</p>
    </div>
  );
}

function Block({ title, text }: { title: string; text: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/15 p-3">
      <p className="text-xs font-black uppercase tracking-widest text-slate-400">{title}</p>
      <p className="mt-2 text-sm font-semibold leading-6 text-slate-100">{text}</p>
    </div>
  );
}

function List({ title, items, icon = 'ok' }: { title: string; items: string[]; icon?: 'ok' | 'warning' | 'limit' }) {
  const Icon = icon === 'warning' ? AlertTriangle : icon === 'limit' ? ShieldAlert : CheckCircle2;
  return (
    <div className="rounded-lg border border-white/10 bg-black/15 p-3">
      <p className="text-xs font-black uppercase tracking-widest text-slate-400">{title}</p>
      <div className="mt-2 space-y-2">
        {(items.length ? items : ['Não informado.']).map((item) => (
          <p key={item} className="flex gap-2 text-sm font-semibold leading-5 text-slate-200">
            <Icon size={15} className="mt-0.5 shrink-0 text-cyan-200" />
            <span>{item}</span>
          </p>
        ))}
      </div>
    </div>
  );
}

function decisionLabel(decision: VisionDecision) {
  return {
    CALL: 'Possível cenário comprador',
    PUT: 'Possível cenário vendedor',
    WAIT: 'Aguardar confirmação',
    DO_NOT_TRADE: 'Não operar neste contexto'
  }[decision];
}
