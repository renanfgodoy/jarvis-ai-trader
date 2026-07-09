import { useQuery } from '@tanstack/react-query';
import { Activity, Clock3 } from 'lucide-react';
import CandlestickChart from './CandlestickChart';
import { getLiveWorkspace } from '../services/api';

export default function ChartCard({ symbol = 'EURUSD-OTC' }: { symbol?: string }) {
  const workspace = useQuery({
    queryKey: ['live-workspace', symbol],
    queryFn: () => getLiveWorkspace(symbol),
    refetchInterval: 5000
  });

  const data = workspace.data;
  const signal = data?.signal;
  const candles = data?.candles ?? [];
  const latest = candles[candles.length - 1];

  return (
    <div className="glass-card p-5 xl:col-span-2">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Live Trading Workspace</p>
          <h3 className="mt-1 text-xl font-black text-white">Candlestick Profissional</h3>
          <p className="mt-1 text-sm text-slate-400">{data?.symbol ?? symbol} • {data?.timeframe ?? 'M1'} • Provider: {data?.provider ?? 'carregando'}</p>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-bold text-emerald-200">
          <Activity size={14} /> Atualização automática
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_220px]">
        <CandlestickChart candles={candles} />
        <div className="space-y-3">
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Sinal IA</p>
            <p className="mt-2 text-4xl font-black text-white">{signal?.trend ?? 'WAIT'}</p>
            <p className="mt-1 text-sm text-slate-400">Força: {signal?.strength ?? 0}%</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-violet-300">Indicadores</p>
            <div className="mt-3 space-y-2 text-sm">
              <Row label="EMA 9" value={signal?.ema9?.toFixed(5)} />
              <Row label="EMA 21" value={signal?.ema21?.toFixed(5)} />
              <Row label="RSI 14" value={signal?.rsi14?.toFixed(2)} />
              <Row label="ATR 14" value={signal?.atr14?.toFixed(5)} />
            </div>
          </div>
          <div className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-4">
            <div className="flex items-center gap-2 text-amber-200">
              <Clock3 size={16} />
              <p className="text-sm font-bold">Próxima vela</p>
            </div>
            <p className="mt-2 text-3xl font-black text-white">M1</p>
            <p className="text-xs text-slate-400">Countdown real será conectado no streaming.</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Último preço</p>
            <p className="mt-2 text-2xl font-black text-white">{latest?.close?.toFixed(5) ?? '---'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value?: string }) {
  return (
    <div className="flex items-center justify-between border-b border-white/5 pb-2">
      <span className="text-slate-400">{label}</span>
      <span className="font-bold text-white">{value ?? '--'}</span>
    </div>
  );
}
