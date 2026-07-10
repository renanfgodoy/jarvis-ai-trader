import { brand } from '../branding/brand';

const events = [
  'API conectada',
  'Provider Manager ativo',
  'Scanner analisando ativos',
  'Signal Engine calculando indicadores',
  'Risk Manager em modo proteção',
  'Execution Engine em DEMO/DRY RUN'
];

export default function Timeline() {
  return (
    <div className="glass-card p-5 xl:col-span-2">
      <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Timeline</p>
      <h3 className="mt-1 text-xl font-black text-white">Eventos do {brand.shortName}</h3>
      <div className="mt-5 space-y-4">
        {events.map((event, index) => (
          <div key={event} className="flex gap-4">
            <div className="flex flex-col items-center">
              <span className="h-3 w-3 rounded-full bg-cyan-300 shadow-glow" />
              {index !== events.length - 1 && <span className="mt-1 h-8 w-px bg-white/10" />}
            </div>
            <div>
              <p className="text-sm font-bold text-white">{event}</p>
              <p className="text-xs text-slate-500">Agora</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
