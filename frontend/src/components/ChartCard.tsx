import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const data = Array.from({ length: 36 }, (_, index) => ({
  time: `${index}`,
  price: 1.17 + Math.sin(index / 3) * 0.002 + index * 0.00008
}));

export default function ChartCard() {
  return (
    <div className="glass-card p-5 xl:col-span-2">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Mercado</p>
          <h3 className="mt-1 text-xl font-black text-white">Gráfico Técnico</h3>
        </div>
        <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-bold text-cyan-200">TradingView Widget em breve</span>
      </div>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="price" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.45} />
                <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
            <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 12 }} />
            <YAxis tick={{ fill: '#64748b', fontSize: 12 }} domain={['dataMin - 0.001', 'dataMax + 0.001']} />
            <Tooltip contentStyle={{ background: '#020617', border: '1px solid rgba(255,255,255,.12)', borderRadius: 16 }} />
            <Area type="monotone" dataKey="price" stroke="#22d3ee" fill="url(#price)" strokeWidth={3} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
