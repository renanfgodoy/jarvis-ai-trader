export default function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 text-center">
      <p className="text-sm font-black text-white">{title}</p>
      <p className="mt-2 text-xs text-slate-400">{message}</p>
    </div>
  );
}
