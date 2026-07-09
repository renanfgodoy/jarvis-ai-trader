import { useEffect, useMemo, useRef } from 'react';
import {
  ColorType,
  CrosshairMode,
  LineStyle,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type UTCTimestamp
} from 'lightweight-charts';
import type { Candle } from '../types/api';

type Props = {
  candles: Candle[];
  signal?: string;
  resetKey?: string;
};

type ChartCandle = {
  time: UTCTimestamp;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
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

function fallbackCandles(): Candle[] {
  const now = Date.now();
  let close = 1.2232;
  return Array.from({ length: 150 }).map((_, index) => {
    const cycle = Math.sin(index / 5.3) * 0.0022 + Math.sin(index / 13) * 0.0032;
    const micro = Math.sin(index * 1.71) * 0.0016;
    const drift = index < 42 ? -0.00012 * index : index < 96 ? 0.00018 * (index - 42) - 0.005 : 0.00002 * index + 0.002;
    const open = close;
    close = 1.2205 + cycle + micro + drift;
    const high = Math.max(open, close) + 0.0012 + Math.abs(Math.cos(index * 0.83)) * 0.0018;
    const low = Math.min(open, close) - 0.0012 - Math.abs(Math.sin(index * 0.77)) * 0.0016;

    return {
      symbol: 'GBPUSD-OTC',
      timeframe: 'M1',
      timestamp: new Date(now - (150 - index) * 60_000).toISOString(),
      open,
      high,
      low,
      close,
      volume: 350 + Math.round(Math.abs(Math.sin(index * 0.48)) * 1100 + Math.abs(Math.cos(index * 0.21)) * 420)
    };
  });
}

function isTooFlat(candles: Candle[]) {
  if (candles.length < 35) return true;
  const highs = candles.map((item) => item.high);
  const lows = candles.map((item) => item.low);
  const max = Math.max(...highs);
  const min = Math.min(...lows);
  return max - min < Math.max(max * 0.0012, 0.0007);
}

function toTimestamp(timestamp: string, index: number): UTCTimestamp {
  const parsed = Math.floor(new Date(timestamp).getTime() / 1000);
  if (Number.isFinite(parsed) && parsed > 0) return parsed as UTCTimestamp;
  return (Math.floor(Date.now() / 1000) - (150 - index) * 60) as UTCTimestamp;
}

function normalizeCandles(source: Candle[]): ChartCandle[] {
  const base = source.length && !isTooFlat(source) ? source : fallbackCandles();
  const last150 = base.slice(-150);
  return last150.map((candle, index) => ({
    time: toTimestamp(candle.timestamp, index),
    open: Number(candle.open),
    high: Number(candle.high),
    low: Number(candle.low),
    close: Number(candle.close),
    volume: Number(candle.volume ?? 0)
  }));
}

export default function CandlestickChart({ candles, signal = 'NEUTRAL', resetKey = 'default' }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const ema9SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const ema21SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const ema200SeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const initializedKeyRef = useRef<string | null>(null);

  const data = useMemo(() => normalizeCandles(candles), [candles]);
  const latest = data[data.length - 1];
  const first = data[0];
  const change = latest && first ? latest.close - first.open : 0;
  const changePct = first ? (change / Math.max(first.open, 0.00001)) * 100 : 0;
  const priceText = latest ? latest.close.toFixed(latest.close > 10 ? 2 : 5) : '0.00000';
  const signalTone = signal === 'BUY' ? 'text-emerald-300 border-emerald-400/30 bg-emerald-400/10' : signal === 'SELL' ? 'text-red-300 border-red-400/30 bg-red-400/10' : 'text-cyan-200 border-cyan-400/30 bg-cyan-400/10';

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: '#070920' },
        textColor: '#94a3b8',
        fontFamily: 'Inter, ui-sans-serif, system-ui, sans-serif',
        fontSize: 11
      },
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: { top: 0.08, bottom: 0.22 }
      },
      timeScale: {
        borderVisible: false,
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 8,
        barSpacing: 9,
        minBarSpacing: 5,
        fixLeftEdge: false
      },
      grid: {
        vertLines: { color: 'rgba(148,163,184,0.075)', style: LineStyle.Solid },
        horzLines: { color: 'rgba(148,163,184,0.11)', style: LineStyle.Solid }
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: 'rgba(34,211,238,0.55)', width: 1, style: LineStyle.Dashed, labelBackgroundColor: '#0891b2' },
        horzLine: { color: 'rgba(34,211,238,0.55)', width: 1, style: LineStyle.Dashed, labelBackgroundColor: '#0891b2' }
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true
      },
      handleScroll: {
        horzTouchDrag: true,
        mouseWheel: true,
        pressedMouseMove: true,
        vertTouchDrag: true
      }
    });

    const candlesSeries = chart.addCandlestickSeries({
      upColor: '#00c875',
      downColor: '#ff4757',
      borderUpColor: '#00f59f',
      borderDownColor: '#ff6673',
      wickUpColor: '#56f0a6',
      wickDownColor: '#ff7b86',
      priceLineColor: '#22c55e',
      priceLineWidth: 1,
      priceFormat: { type: 'price', precision: 5, minMove: 0.00001 }
    });

    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      lastValueVisible: false,
      priceLineVisible: false
    });
    volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });

    const ema9Series = chart.addLineSeries({ color: '#facc15', lineWidth: 2, priceLineVisible: false, lastValueVisible: false });
    const ema21Series = chart.addLineSeries({ color: '#38bdf8', lineWidth: 2, priceLineVisible: false, lastValueVisible: false });
    const ema200Series = chart.addLineSeries({ color: '#d946ef', lineWidth: 2, priceLineVisible: false, lastValueVisible: false });

    chartRef.current = chart;
    candleSeriesRef.current = candlesSeries;
    volumeSeriesRef.current = volumeSeries;
    ema9SeriesRef.current = ema9Series;
    ema21SeriesRef.current = ema21Series;
    ema200SeriesRef.current = ema200Series;

    return () => {
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
      ema9SeriesRef.current = null;
      ema21SeriesRef.current = null;
      ema200SeriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!data.length) return;
    const closes = data.map((item) => item.close);
    const ema9 = ema(closes, 9);
    const ema21 = ema(closes, 21);
    const ema200 = ema(closes, 80);

    candleSeriesRef.current?.setData(data.map(({ time, open, high, low, close }) => ({ time, open, high, low, close })));
    volumeSeriesRef.current?.setData(data.map((item) => ({
      time: item.time,
      value: item.volume,
      color: item.close >= item.open ? 'rgba(0,200,117,0.36)' : 'rgba(255,71,87,0.36)'
    })));
    ema9SeriesRef.current?.setData(data.map((item, index) => ({ time: item.time, value: ema9[index] })));
    ema21SeriesRef.current?.setData(data.map((item, index) => ({ time: item.time, value: ema21[index] })));
    ema200SeriesRef.current?.setData(data.map((item, index) => ({ time: item.time, value: ema200[index] })));
    const chart = chartRef.current;
    if (chart && initializedKeyRef.current !== resetKey) {
      initializedKeyRef.current = resetKey;
      const barsToShow = Math.min(95, data.length);
      chart.timeScale().setVisibleLogicalRange({
        from: Math.max(0, data.length - barsToShow),
        to: data.length + 8
      });
    }
  }, [data, resetKey]);

  return (
    <div className="relative h-[760px] overflow-hidden rounded-2xl border border-slate-700/60 bg-[#070920] shadow-[0_0_70px_rgba(34,211,238,0.10)]">
      <div className="pointer-events-none absolute left-0 right-0 top-0 z-10 flex items-start justify-between bg-gradient-to-b from-[#070920]/92 via-[#070920]/62 to-transparent px-4 py-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-lg border border-white/10 bg-slate-950/70 px-2.5 py-1 text-[10px] font-black uppercase tracking-widest text-slate-200">Candlestick</span>
            <span className="rounded-lg border border-amber-400/20 bg-amber-400/10 px-2.5 py-1 text-[10px] font-black text-amber-200">EMA 9</span>
            <span className="rounded-lg border border-sky-400/20 bg-sky-400/10 px-2.5 py-1 text-[10px] font-black text-sky-200">EMA 21</span>
            <span className="rounded-lg border border-fuchsia-400/20 bg-fuchsia-400/10 px-2.5 py-1 text-[10px] font-black text-fuchsia-200">EMA 200</span>
            <span className={`rounded-lg border px-2.5 py-1 text-[10px] font-black ${signalTone}`}>IA {signal}</span>
          </div>
        </div>
        <div className="rounded-xl border border-white/10 bg-slate-950/80 px-3 py-2 text-right backdrop-blur">
          <p className="text-[10px] uppercase tracking-widest text-slate-500">Último preço</p>
          <p className="text-base font-black text-emerald-300">{priceText}</p>
          <p className={`text-xs font-black ${changePct >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>{changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%</p>
        </div>
      </div>

      <div ref={containerRef} className="absolute inset-0" />
    </div>
  );
}
