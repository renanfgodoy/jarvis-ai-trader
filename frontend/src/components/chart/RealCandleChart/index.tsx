import { useEffect, useMemo, useRef } from 'react';
import { ColorType, CrosshairMode, LineStyle, createChart, type IChartApi, type ISeriesApi, type UTCTimestamp } from 'lightweight-charts';
import { classifyRealCandleSync } from './sync';
import { recordChartBindingTrace, summarizeChartBindingCandles } from '../../../debug/chartBindingTrace';
import { recordFridayLatencyAudit } from '../../../utils/latencyAudit';

export type RealChartCandle = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
};

type Props = {
  activeId: number | null;
  symbol?: string | null;
  rawSize: number;
  candles: RealChartCandle[];
  chartClassName?: string;
  compact?: boolean;
};

function toChartData(candles: RealChartCandle[]) {
  return candles.map((candle) => ({
    time: candle.time as UTCTimestamp,
    open: candle.open,
    high: candle.high,
    low: candle.low,
    close: candle.close
  }));
}

export default function RealCandleChart({ activeId, symbol, rawSize, candles, chartClassName = 'h-[620px]', compact = false }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const previousDataRef = useRef<ReturnType<typeof toChartData>>([]);
  const hasFittedContentRef = useRef(false);
  const renderCountRef = useRef(0);
  renderCountRef.current += 1;
  const data = useMemo(() => toChartData(candles), [candles]);

  useEffect(() => {
    recordChartBindingTrace('GRAPH_PROPS_UPDATED', {
      active_id: activeId,
      raw_size: rawSize,
      symbol: symbol ?? null,
      graph_prop_count: candles.length,
      ...summarizeChartBindingCandles(candles)
    });
    recordFridayLatencyAudit('react_render_committed', {
      active_id: activeId,
      symbol: symbol ?? null,
      raw_size: rawSize,
      candle_count: candles.length,
      render_count: renderCountRef.current
    });
  });

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
        scaleMargins: { top: 0.08, bottom: 0.08 }
      },
      timeScale: {
        borderVisible: false,
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 8,
        barSpacing: 10,
        minBarSpacing: 5
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
        vertTouchDrag: false
      }
    });

    const candleSeries = chart.addCandlestickSeries({
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

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;

    return () => {
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    previousDataRef.current = [];
    hasFittedContentRef.current = false;
    candleSeriesRef.current?.setData([]);
  }, [activeId, rawSize, symbol]);

  useEffect(() => {
    const candleSeries = candleSeriesRef.current;
    if (!candleSeries) {
      recordChartBindingTrace('GRAPH_LOADING', {
        active_id: activeId,
        raw_size: rawSize,
        symbol: symbol ?? null,
        graph_prop_count: candles.length,
        reason: 'SERIES_NOT_READY'
      });
      return;
    }

    const previousData = previousDataRef.current;
    const syncAction = classifyRealCandleSync(previousData, data);

    if (syncAction === 'unchanged') {
      recordChartBindingTrace(data.length ? 'GRAPH_RENDERED' : 'GRAPH_EMPTY', {
        active_id: activeId,
        raw_size: rawSize,
        symbol: symbol ?? null,
        graph_prop_count: data.length,
        reason: 'UNCHANGED',
        ...summarizeChartBindingCandles(candles)
      });
      return;
    }

    if (!data.length) {
      recordChartBindingTrace('GRAPH_EMPTY', {
        active_id: activeId,
        raw_size: rawSize,
        symbol: symbol ?? null,
        graph_prop_count: 0,
        reason: 'NO_CANDLES'
      });
      return;
    }

    try {
      if ((syncAction === 'append' || syncAction === 'update') && data.length) {
        const startedAt = performance.now();
        candleSeries.update(data[data.length - 1]);
        recordFridayLatencyAudit('t7_series_update', {
          active_id: activeId,
          symbol: symbol ?? null,
          raw_size: rawSize,
          candle_count: data.length,
          sync_action: syncAction,
          duration_ms: Math.round((performance.now() - startedAt) * 1000) / 1000
        });
      } else {
        const startedAt = performance.now();
        candleSeries.setData(data);
        recordFridayLatencyAudit('chart_series_set_data', {
          active_id: activeId,
          symbol: symbol ?? null,
          raw_size: rawSize,
          candle_count: data.length,
          sync_action: syncAction,
          duration_ms: Math.round((performance.now() - startedAt) * 1000) / 1000
        });
      }
    } catch (error) {
      recordChartBindingTrace('GRAPH_ERROR', {
        active_id: activeId,
        raw_size: rawSize,
        symbol: symbol ?? null,
        graph_prop_count: data.length,
        reason: error instanceof Error ? error.name : 'UNKNOWN_ERROR'
      });
      throw error;
    }

    previousDataRef.current = data;
    recordChartBindingTrace('GRAPH_RENDERED', {
      active_id: activeId,
      raw_size: rawSize,
      symbol: symbol ?? null,
      graph_prop_count: data.length,
      reason: syncAction,
      ...summarizeChartBindingCandles(candles)
    });

    if (typeof window !== 'undefined') {
      window.requestAnimationFrame(() => {
        recordFridayLatencyAudit('t9_frame_drawn', {
          active_id: activeId,
          symbol: symbol ?? null,
          raw_size: rawSize,
          candle_count: data.length,
          sync_action: syncAction
        });
      });
    }

    if (data.length && !hasFittedContentRef.current) {
      chartRef.current?.timeScale().fitContent();
      hasFittedContentRef.current = true;
    }
  }, [activeId, data, rawSize, symbol]);

  return (
    <section className="overflow-hidden rounded-2xl border border-cyan-400/15 bg-[#070920] shadow-[0_0_70px_rgba(34,211,238,0.10)]">
      <div className={`flex flex-wrap items-center justify-between gap-3 border-b border-white/10 ${compact ? 'px-3 py-2' : 'px-4 py-3'}`}>
        <div>
          <h2 className={`${compact ? 'text-sm' : 'text-lg'} font-black text-white`}>{symbol ?? 'Ativo não identificado'} · {formatRawSize(rawSize)}</h2>
        </div>
        <div className={`rounded-xl border border-white/10 bg-white/[0.035] px-3 ${compact ? 'py-1.5' : 'py-2'} text-right`}>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Candles</p>
          <p className="text-sm font-black text-cyan-200">{candles.length}</p>
        </div>
      </div>
      <div className={`relative ${chartClassName}`}>
        {!candles.length && (
          <div className="absolute inset-0 z-10 flex items-center justify-center px-6 text-center">
            <div>
              <p className="text-sm font-black text-white">Aguardando dados do mercado...</p>
              <p className="mt-2 max-w-xl text-xs leading-relaxed text-slate-400">
                O gráfico será desenhado somente após receber candles reais.
              </p>
            </div>
          </div>
        )}
        <div ref={containerRef} className="absolute inset-0" />
      </div>
    </section>
  );
}

function formatRawSize(rawSize: number) {
  if (rawSize === 60) return 'M1';
  if (rawSize === 300) return 'M5';
  if (rawSize === 900) return 'M15';
  return `${rawSize}s`;
}
