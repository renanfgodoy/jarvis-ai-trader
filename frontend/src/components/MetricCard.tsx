type MetricCardProps = {
  title: string;
  value: string | number;
  subtitle?: string;
  tone?: 'cyan' | 'green' | 'amber' | 'red' | 'violet';
};

const toneMap = {
  cyan: 'text-cyan-300 border-cyan-400/20 bg-cyan-400/10',
  green: 'text-emerald-300 border-emerald-400/20 bg-emerald-400/10',
  amber: 'text-amber-300 border-amber-400/20 bg-amber-400/10',
  red: 'text-red-300 border-red-400/20 bg-red-400/10',
  violet: 'text-violet-300 border-violet-400/20 bg-violet-400/10'
};

export default function MetricCard({ title, value, subtitle, tone = 'cyan' }: MetricCardProps) {
  return (
    <div className="glass-card p-5">
      <p className="text-sm text-slate-400">{title}</p>
      <div className={`mt-3 inline-flex rounded-2xl border px-4 py-2 text-2xl font-black ${toneMap[tone]}`}>
        {value}
      </div>
      {subtitle && <p className="mt-3 text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
}
