import type { Candle } from '../types/api';

type Props = {
  candles: Candle[];
  signal?: string;
};

function ema(values: number[], period: number) {
  const multiplier = 2 / (period + 1);
  const result: number[] = [];
  values.forEach((value, index) => {
    if (index === 0) result.push(value);
    else result.push(value * multiplier + result[index - 1] * (1 - multiplier));
  });
  return result;
}

function polyline(values: number[], min: number, max: number, width: number, height: number, padding: number) {
  const step = (width - padding * 2) / Math.max(values.length - 1, 1);
  return values
    .map((value, index) => {
      const x = padding + index * step;
      const y = padding + ((max - value) / Math.max(max - min, 0.000001)) * (height - padding * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');
}

export default function CandlestickChart({ candles, signal = 'NEUTRAL' }: Props) {
  const visible = candles.slice(-72);
  const width = 1280;
  const height = 500;
  const padding = 44;
  const volumeHeight = 76;
  const priceHeight = height - volumeHeight;

  if (!visible.length) {
    return (
      <div className="flex h-[500px] items-center justify-center rounded-2xl border border-white/10 bg-[#070920] text-slate-400">
        Aguardando candles...
      </div>
    );
  }

  const highs = visible.map((candle) => candle.high);
  const lows = visible.map((candle) => candle.low);
  const closes = visible.map((candle) => candle.close);
  const volumes = visible.map((candle) => candle.volume ?? 0);
  const rawMaxPrice = Math.max(...highs, 1);
  const rawMinPrice = Math.min(...lows, 1);
  const rawRange = Math.max(rawMaxPrice - rawMinPrice, rawMaxPrice * 0.0018);
  const margin = Math.max(rawRange * 0.16, rawMaxPrice * 0.0002);
  const maxPrice = rawMaxPrice + margin;
  const minPrice = Math.max(0.00001, rawMinPrice - margin);
  const maxVolume = Math.max(...volumes, 1);
  const step = (width - padding * 2) / Math.max(visible.length, 1);
  const candleWidth = Math.max(6, Math.min(13, step * 0.64));
  const ema9 = ema(closes, 9);
  const ema21 = ema(closes, 21);
  const last = visible[visible.length - 1];
  const lastY = y(last.close);

  function y(price: number) {
    return padding + ((maxPrice - price) / Math.max(maxPrice - minPrice, 0.000001)) * (priceHeight - padding * 2);
  }

  function x(index: number) {
    return padding + index * step + step / 2;
  }

  const lastPriceText = last.close.toFixed(last.close > 10 ? 2 : 5);
  const change = last.close - visible[0].open;
  const changePct = (change / Math.max(visible[0].open, 0.00001)) * 100;
  const trendColor = change >= 0 ? '#22c55e' : '#ef4444';

  return (
    <div className="relative h-[500px] overflow-hidden rounded-2xl border border-white/10 bg-[#070920] shadow-[0_0_60px_rgba(34,211,238,0.08)]">
      <div className="absolute left-4 top-4 z-10 flex items-center gap-2">
        <span className="rounded-lg border border-cyan-400/25 bg-cyan-400/10 px-3 py-1.5 text-[11px] font-black text-cyan-100">Candlestick</span>
        <span className="rounded-lg border border-amber-400/25 bg-amber-400/10 px-3 py-1.5 text-[11px] font-black text-amber-100">EMA 9</span>
        <span className="rounded-lg border border-sky-400/25 bg-sky-400/10 px-3 py-1.5 text-[11px] font-black text-sky-100">EMA 21</span>
        <span className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-[11px] font-black text-slate-200">IA: {signal}</span>
      </div>

      <div className="absolute right-4 top-4 z-10 rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-right">
        <p className="text-[10px] uppercase tracking-widest text-slate-500">Variação</p>
        <p className="text-sm font-black" style={{ color: trendColor }}>{change >= 0 ? '+' : ''}{changePct.toFixed(2)}%</p>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
        <defs>
          <linearGradient id="chartBgV132" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="rgba(9,13,45,1)" />
            <stop offset="56%" stopColor="rgba(6,9,32,1)" />
            <stop offset="100%" stopColor="rgba(22,11,63,0.82)" />
          </linearGradient>
        </defs>
        <rect width={width} height={height} fill="url(#chartBgV132)" />

        {Array.from({ length: 8 }).map((_, index) => {
          const yy = padding + index * ((priceHeight - padding * 2) / 7);
          const value = maxPrice - index * ((maxPrice - minPrice) / 7);
          return (
            <g key={`h-grid-${index}`}>
              <line x1={padding} x2={width - padding} y1={yy} y2={yy} stroke="rgba(148,163,184,0.12)" />
              <text x={width - padding + 10} y={yy + 4} fill="#94a3b8" fontSize="11">{value.toFixed(value > 10 ? 2 : 5)}</text>
            </g>
          );
        })}
        {Array.from({ length: 12 }).map((_, index) => {
          const xx = padding + index * ((width - padding * 2) / 11);
          return <line key={`v-grid-${index}`} x1={xx} x2={xx} y1={padding} y2={priceHeight - padding} stroke="rgba(148,163,184,0.07)" />;
        })}

        {visible.map((candle, index) => {
          const bullish = candle.close >= candle.open;
          const cx = x(index);
          const openY = y(candle.open);
          const closeY = y(candle.close);
          const highY = y(candle.high);
          const lowY = y(candle.low);
          const bodyY = Math.min(openY, closeY);
          const bodyHeight = Math.max(Math.abs(openY - closeY), 3.8);
          const color = bullish ? '#00c875' : '#ff4757';
          const wick = bullish ? '#50f0a0' : '#ff7b86';
          const volumeY = priceHeight + 15 + (1 - (candle.volume ?? 0) / maxVolume) * (volumeHeight - 28);
          const volumeBarHeight = height - 12 - volumeY;
          return (
            <g key={`${candle.timestamp}-${index}`}>
              <line x1={cx} x2={cx} y1={highY} y2={lowY} stroke={wick} strokeWidth={1.5} strokeLinecap="round" opacity={0.95} />
              <rect x={cx - candleWidth / 2} y={bodyY} width={candleWidth} height={bodyHeight} rx={1.8} fill={color} opacity={0.98} />
              <rect x={cx - candleWidth / 2} y={volumeY} width={candleWidth} height={volumeBarHeight} rx={1.6} fill={color} opacity={0.32} />
            </g>
          );
        })}

        <polyline points={polyline(ema9, minPrice, maxPrice, width, priceHeight, padding)} fill="none" stroke="#facc15" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={polyline(ema21, minPrice, maxPrice, width, priceHeight, padding)} fill="none" stroke="#38bdf8" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" />
        <line x1={padding} x2={width - padding} y1={lastY} y2={lastY} stroke="rgba(239,68,68,0.64)" strokeDasharray="5 5" />
        <rect x={width - padding - 74} y={lastY - 13} width={70} height={26} rx={6} fill="rgba(239,68,68,0.95)" />
        <text x={width - padding - 39} y={lastY + 5} textAnchor="middle" fill="white" fontSize="11" fontWeight="900">{lastPriceText}</text>
      </svg>
    </div>
  );
}
