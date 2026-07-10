export default function Loading({ label = 'Carregando' }: { label?: string }) {
  return <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-4 text-xs font-black uppercase tracking-widest text-cyan-300">{label}</div>;
}
