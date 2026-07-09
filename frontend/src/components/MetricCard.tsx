type MetricCardProps = {
  title: string;
  value: string | number;
  subtitle?: string;
  tone?: 'cyan' | 'green' | 'amber' | 'red' | 'violet';
};

const toneMap = {
  cyan: 'text-cyan-300',
  green: 'text-emerald-300',
  amber: 'text-amber-300',
  red: 'text-red-300',
  violet: 'text-violet-300'
};

export default function MetricCard({ title, value, subtitle, tone = 'cyan' }: MetricCardProps) {
  return (
    <div className="panel p-4">
      <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">{title}</p>
      <p className={`mt-2 text-2xl font-black ${toneMap[tone]}`}>{value}</p>
      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
}
