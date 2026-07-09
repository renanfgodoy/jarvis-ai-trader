import type { Candle } from '../types/api';

type Props = {
  candles: Candle[];
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

function points(values: number[], min: number, max: number, width: number, height: number, padding: number) {
  const step = (width - padding * 2) / Math.max(values.length - 1, 1);
  return values
    .map((value, index) => {
      const x = padding + index * step;
      const y = padding + ((max - value) / Math.max(max - min, 0.000001)) * (height - padding * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');
}

export default function CandlestickChart({ candles }: Props) {
  const visible = candles.slice(-60);
  const width = 980;
  const height = 420;
  const padding = 34;
  const volumeHeight = 70;
  const priceHeight = height - volumeHeight;
  const highs = visible.map((candle) => candle.high);
  const lows = visible.map((candle) => candle.low);
  const closes = visible.map((candle) => candle.close);
  const volumes = visible.map((candle) => candle.volume ?? 0);
  const maxPrice = Math.max(...highs, 1);
  const minPrice = Math.min(...lows, 1);
  const maxVolume = Math.max(...volumes, 1);
  const step = (width - padding * 2) / Math.max(visible.length, 1);
  const candleWidth = Math.max(4, Math.min(11, step * 0.58));
  const ema9 = ema(closes, 9);
  const ema21 = ema(closes, 21);

  const y = (price: number) => padding + ((maxPrice - price) / Math.max(maxPrice - minPrice, 0.000001)) * (priceHeight - padding * 2);
  const x = (index: number) => padding + index * step + step / 2;

  return (
    <div className="relative h-full min-h-[420px] overflow-hidden rounded-[24px] border border-white/10 bg-slate-950/80">
      <div className="absolute left-4 top-4 z-10 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-3 py-2 text-xs font-bold text-cyan-100">
        Candlestick • EMA 9 • EMA 21 • Volume
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full">
        <defs>
          <linearGradient id="chartGlow" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="rgba(34,211,238,0.16)" />
            <stop offset="100%" stopColor="rgba(124,58,237,0.06)" />
          </linearGradient>
        </defs>
        <rect width={width} height={height} fill="url(#chartGlow)" />
        {Array.from({ length: 7 }).map((_, index) => {
          const yy = padding + index * ((priceHeight - padding * 2) / 6);
          return <line key={`grid-${index}`} x1={padding} x2={width - padding} y1={yy} y2={yy} stroke="rgba(148,163,184,0.12)" />;
        })}
        {visible.map((candle, index) => {
          const bullish = candle.close >= candle.open;
          const cx = x(index);
          const openY = y(candle.open);
          const closeY = y(candle.close);
          const highY = y(candle.high);
          const lowY = y(candle.low);
          const bodyY = Math.min(openY, closeY);
          const bodyHeight = Math.max(Math.abs(openY - closeY), 2);
          const color = bullish ? '#22c55e' : '#ef4444';
          const volumeY = priceHeight + 18 + (1 - (candle.volume ?? 0) / maxVolume) * (volumeHeight - 28);
          const volumeBarHeight = height - 12 - volumeY;
          return (
            <g key={`${candle.timestamp}-${index}`}>
              <line x1={cx} x2={cx} y1={highY} y2={lowY} stroke={color} strokeWidth={1.4} strokeLinecap="round" />
              <rect x={cx - candleWidth / 2} y={bodyY} width={candleWidth} height={bodyHeight} rx={2} fill={color} opacity={0.88} />
              <rect x={cx - candleWidth / 2} y={volumeY} width={candleWidth} height={volumeBarHeight} rx={2} fill={color} opacity={0.22} />
            </g>
          );
        })}
        <polyline points={points(ema9, minPrice, maxPrice, width, priceHeight, padding)} fill="none" stroke="#22d3ee" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={points(ema21, minPrice, maxPrice, width, priceHeight, padding)} fill="none" stroke="#a78bfa" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" />
        <line x1={padding} x2={width - padding} y1={priceHeight + 10} y2={priceHeight + 10} stroke="rgba(148,163,184,0.18)" />
        <text x={width - padding - 4} y={padding + 4} textAnchor="end" fill="#94a3b8" fontSize="12">{maxPrice.toFixed(5)}</text>
        <text x={width - padding - 4} y={priceHeight - padding + 4} textAnchor="end" fill="#94a3b8" fontSize="12">{minPrice.toFixed(5)}</text>
      </svg>
    </div>
  );
}
