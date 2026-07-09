import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight, Flame, Minus, ShieldCheck, Trophy } from 'lucide-react';
import { useMemo, useRef } from 'react';
import type { AssetScannerResult } from '../types/api';

type Props = {
  assets: AssetScannerResult[];
  selectedSymbol?: string;
  onSelect?: (symbol: string) => void;
  dataQuality?: string;
  totalAssets?: number;
  openAssets?: number;
};

export default function TopAssets({ assets, selectedSymbol, onSelect, dataQuality = 'SIMULATED', totalAssets = 0, openAssets = 0 }: Props) {
  const visibleAssets = assets.length ? assets.slice(0, 12) : fallbackAssets;
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const groups = useMemo(() => {
    const chunks: AssetScannerResult[][] = [];
    for (let index = 0; index < visibleAssets.length; index += 3) {
      chunks.push(visibleAssets.slice(index, index + 3));
    }
    return chunks;
  }, [visibleAssets]);

  const scroll = (direction: 'left' | 'right') => {
    const container = scrollRef.current;
    if (!container) return;
    container.scrollBy({ left: direction === 'right' ? container.clientWidth : -container.clientWidth, behavior: 'smooth' });
  };

  return (
    <div className="panel p-3 opportunity-carousel-panel">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-2xl border border-amber-300/20 bg-amber-300/10">
            <Trophy className="text-amber-300" size={19} />
          </div>
          <div>
            <p className="eyebrow">Scanner IA · Top 12</p>
            <h3 className="mt-1 text-base font-black text-white">Melhores oportunidades</h3>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-400">
          <span className="rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2">{dataQuality}</span>
          <span className="rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2">{openAssets}/{totalAssets || visibleAssets.length} abertos</span>
          <button aria-label="Voltar oportunidades" onClick={() => scroll('left')} className="toolbar-icon"><ChevronLeft size={16} /></button>
          <button aria-label="Avançar oportunidades" onClick={() => scroll('right')} className="toolbar-icon"><ChevronRight size={16} /></button>
        </div>
      </div>

      <div ref={scrollRef} className="opportunity-scroll flex snap-x snap-mandatory gap-3 overflow-x-auto pb-1">
        {groups.map((group, groupIndex) => (
          <div key={`group-${groupIndex}`} className="grid min-w-full snap-start grid-cols-1 gap-3 md:grid-cols-3">
            {group.map((asset, index) => {
              const active = asset.symbol === selectedSymbol;
              const rank = asset.rank ?? groupIndex * 3 + index + 1;
              return (
                <button
                  key={`${asset.symbol}-${rank}`}
                  onClick={() => onSelect?.(asset.symbol)}
                  className={`opportunity-card group text-left transition ${active ? 'is-active' : ''}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="rank-badge">#{rank}</span>
                        <span className={`quality-badge ${(asset as any).data_quality === 'REAL' ? 'quality-real' : 'quality-sim'}`}>{(asset as any).data_quality ?? 'SIM'}</span>
                      </div>
                      <h4 className="mt-3 text-lg font-black tracking-tight text-white">{asset.symbol}</h4>
                      <p className="mt-1 text-[10px] font-black uppercase tracking-widest text-slate-500">{asset.timeframe ?? 'M1'} · {(asset as any).market_status ?? asset.status ?? 'OPEN'}</p>
                    </div>
                    <SignalPill signal={asset.signal} />
                  </div>

                  <div className="mt-4 grid grid-cols-3 gap-2">
                    <MiniMetric label="Score" value={`${Math.round(asset.score ?? 0)}%`} tone={asset.score && asset.score >= 90 ? 'green' : 'amber'} />
                    <MiniMetric label="Payout" value={`${Math.round((asset as any).payout ?? 80)}%`} tone="cyan" />
                    <MiniMetric label="Risk" value={asset.risk_level ?? 'LOW'} tone="green" />
                  </div>

                  <div className="mt-4 flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/40 px-3 py-2">
                    <span className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-400"><ShieldCheck size={13} /> Gate</span>
                    <span className={`text-xs font-black ${asset.status === 'APPROVED' ? 'text-emerald-300' : 'text-amber-300'}`}>{asset.status ?? 'WATCHLIST'}</span>
                  </div>
                </button>
              );
            })}
          </div>
        ))}
      </div>

      <p className="mt-3 px-1 text-[11px] leading-relaxed text-slate-500">Role horizontalmente de 3 em 3. Clique em um card para sincronizar ativo, timeframe, gráfico, IA e AutoTrade Gate.</p>
    </div>
  );
}

function SignalPill({ signal }: { signal?: string }) {
  const normalized = signal === 'CALL' ? 'BUY' : signal === 'PUT' ? 'SELL' : signal ?? 'WAIT';
  if (normalized === 'BUY') return <span className="signal-pill signal-buy"><ArrowUp size={14} /> BUY</span>;
  if (normalized === 'SELL') return <span className="signal-pill signal-sell"><ArrowDown size={14} /> SELL</span>;
  return <span className="signal-pill signal-wait"><Minus size={14} /> WAIT</span>;
}

function MiniMetric({ label, value, tone = 'white' }: { label: string; value: string | number; tone?: 'white' | 'cyan' | 'amber' | 'green' }) {
  const colors = { white: 'text-white', cyan: 'text-cyan-300', amber: 'text-amber-300', green: 'text-emerald-300' };
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-2 text-center">
      <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className={`mt-1 text-sm font-black ${colors[tone]}`}>{value}</p>
    </div>
  );
}

const fallbackAssets: AssetScannerResult[] = [
  { rank: 1, symbol: 'GBPUSD-OTC', timeframe: 'M1', signal: 'BUY', score: 96, risk_level: 'LOW', status: 'APPROVED', payout: 92, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 2, symbol: 'EURUSD-OTC', timeframe: 'M1', signal: 'BUY', score: 94, risk_level: 'LOW', status: 'APPROVED', payout: 91, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 3, symbol: 'BTCUSD-OTC', timeframe: 'M5', signal: 'SELL', score: 93, risk_level: 'LOW', status: 'APPROVED', payout: 90, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 4, symbol: 'NZDUSD-OTC', timeframe: 'M1', signal: 'BUY', score: 92, risk_level: 'LOW', status: 'APPROVED', payout: 89, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 5, symbol: 'AUDUSD-OTC', timeframe: 'M5', signal: 'BUY', score: 90, risk_level: 'LOW', status: 'APPROVED', payout: 88, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 6, symbol: 'USDJPY-OTC', timeframe: 'M15', signal: 'SELL', score: 89, risk_level: 'LOW', status: 'APPROVED', payout: 87, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 7, symbol: 'EURJPY-OTC', timeframe: 'M1', signal: 'BUY', score: 88, risk_level: 'LOW', status: 'APPROVED', payout: 86, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 8, symbol: 'GOLD-OTC', timeframe: 'M5', signal: 'BUY', score: 87, risk_level: 'LOW', status: 'APPROVED', payout: 85, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 9, symbol: 'USOIL-OTC', timeframe: 'M15', signal: 'BUY', score: 84, risk_level: 'LOW', status: 'WATCHLIST', payout: 84, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 10, symbol: 'ETHUSD-OTC', timeframe: 'M5', signal: 'SELL', score: 83, risk_level: 'LOW', status: 'WATCHLIST', payout: 83, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 11, symbol: 'GBPJPY-OTC', timeframe: 'M1', signal: 'BUY', score: 81, risk_level: 'LOW', status: 'WATCHLIST', payout: 82, data_quality: 'SIMULATED', market_status: 'OPEN' },
  { rank: 12, symbol: 'AUDJPY-OTC', timeframe: 'M15', signal: 'SELL', score: 79, risk_level: 'LOW', status: 'WATCHLIST', payout: 81, data_quality: 'SIMULATED', market_status: 'OPEN' }
];
