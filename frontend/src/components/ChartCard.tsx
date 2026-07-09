import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, Camera, Clock3, Expand, Settings, SlidersHorizontal, Wifi } from 'lucide-react';
import CandlestickChart from './CandlestickChart';
import { getLiveTick, getLiveWorkspace, getLiveWorkspaceWebSocketUrl } from '../services/api';
import type { LiveTick, LiveWorkspaceResponse } from '../types/api';

export default function ChartCard({ symbol = 'EURUSD-OTC' }: { symbol?: string }) {
  const workspace = useQuery({ queryKey: ['live-workspace', symbol], queryFn: () => getLiveWorkspace(symbol), refetchInterval: 8000 });
  const tickFallback = useQuery({ queryKey: ['live-tick-fallback', symbol], queryFn: () => getLiveTick(symbol), refetchInterval: 3000 });
  const [streamTick, setStreamTick] = useState<LiveTick | null>(null);
  const [socketStatus, setSocketStatus] = useState<'connecting' | 'online' | 'fallback'>('connecting');

  useEffect(() => {
    let closed = false;
    const ws = new WebSocket(getLiveWorkspaceWebSocketUrl(symbol));
    setSocketStatus('connecting');
    ws.onopen = () => !closed && setSocketStatus('online');
    ws.onmessage = (event) => {
      if (closed) return;
      try {
        setStreamTick(JSON.parse(event.data) as LiveTick);
        setSocketStatus('online');
      } catch {
        setSocketStatus('fallback');
      }
    };
    ws.onerror = () => !closed && setSocketStatus('fallback');
    ws.onclose = () => !closed && setSocketStatus('fallback');
    return () => {
      closed = true;
      ws.close();
    };
  }, [symbol]);

  const data = useMemo(() => {
    if (streamTick) {
      return {
        mode: streamTick.mode,
        symbol: streamTick.symbol,
        timeframe: streamTick.timeframe,
        provider: streamTick.provider,
        candles: streamTick.candles,
        signal: streamTick.signal,
        top_assets: streamTick.top_assets,
        scanner_total: streamTick.scanner_total,
        countdown_seconds: streamTick.countdown_seconds,
        last_price: streamTick.price,
        events: streamTick.events,
        disclaimer: streamTick.disclaimer
      } as LiveWorkspaceResponse;
    }
    if (tickFallback.data) {
      const fallback = tickFallback.data;
      return {
        mode: fallback.mode,
        symbol: fallback.symbol,
        timeframe: fallback.timeframe,
        provider: fallback.provider,
        candles: fallback.candles,
        signal: fallback.signal,
        top_assets: fallback.top_assets,
        scanner_total: fallback.scanner_total,
        countdown_seconds: fallback.countdown_seconds,
        last_price: fallback.price,
        events: fallback.events,
        disclaimer: fallback.disclaimer
      } as LiveWorkspaceResponse;
    }
    return workspace.data;
  }, [streamTick, tickFallback.data, workspace.data]);

  const signal = data?.signal;
  const candles = data?.candles ?? [];
  const latest = candles[candles.length - 1];
  const countdown = data?.countdown_seconds ?? 0;
  const price = data?.last_price ?? latest?.close ?? 0;
  const priceText = price.toFixed(price > 10 ? 2 : 5);

  return (
    <div className="panel p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <Badge icon={<Clock3 size={13} />} text="1m" active />
          <Badge text="$ Aberto" />
          <Badge text={`${Math.round(signal?.strength ?? 0)}%`} tone="green" />
        </div>
        <div className="flex items-center gap-2">
          <button className="toolbar-btn"><span>Candlestick</span></button>
          <button className="toolbar-icon"><BarChart3 size={16} /></button>
          <button className="toolbar-icon"><SlidersHorizontal size={16} /></button>
          <button className="toolbar-icon"><Settings size={16} /></button>
          <button className="toolbar-icon"><Expand size={16} /></button>
          <button className="toolbar-icon"><Camera size={16} /></button>
        </div>
      </div>

      <div className="mb-3 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h3 className="text-2xl font-black text-white">{data?.symbol ?? symbol}</h3>
          <p className="mt-1 text-sm text-slate-400">
            {data?.timeframe ?? 'M1'} · J.A.R.V.I.S · Provider: {data?.provider ?? 'carregando'}
          </p>
        </div>
        <div className="text-right">
          <p className="text-[10px] uppercase tracking-widest text-slate-500">Último preço</p>
          <p className="text-2xl font-black text-emerald-300">{priceText}</p>
        </div>
      </div>

      <CandlestickChart candles={candles} signal={signal?.trend} />

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="text-cyan-300">EMA 9</span>
          <b className="text-white">{signal?.ema9?.toFixed(5) ?? '--'}</b>
          <span className="text-sky-300">EMA 21</span>
          <b className="text-white">{signal?.ema21?.toFixed(5) ?? '--'}</b>
          <span>RSI {signal?.rsi14?.toFixed(2) ?? '--'}</span>
          <span>ATR {signal?.atr14?.toFixed(5) ?? '--'}</span>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 font-bold text-emerald-200">
          <Wifi size={13} /> {socketStatus === 'online' ? 'WebSocket online' : socketStatus === 'connecting' ? 'Conectando' : 'REST fallback'} · próxima vela 00:{String(countdown).padStart(2, '0')}
        </div>
      </div>
    </div>
  );
}

function Badge({ text, icon, active, tone = 'cyan' }: { text: string; icon?: React.ReactNode; active?: boolean; tone?: 'cyan' | 'green' }) {
  const color = tone === 'green' ? 'bg-emerald-400/15 text-emerald-300 border-emerald-400/20' : 'bg-cyan-400/15 text-cyan-300 border-cyan-400/20';
  return <span className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-black ${active ? color : 'border-white/10 bg-white/[0.035] text-slate-300'}`}>{icon}{text}</span>;
}
