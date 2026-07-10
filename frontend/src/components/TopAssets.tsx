import { ChevronLeft, ChevronRight, Trophy } from 'lucide-react';
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

export default function TopAssets({ assets, selectedSymbol, onSelect, dataQuality = 'Não disponível', totalAssets = 0, openAssets = 0 }: Props) {
  const visibleAssets = assets.slice(0, 12);
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
            <p className="eyebrow">Top 12</p>
            <h3 className="mt-1 text-base font-black text-white">Ativos disponíveis</h3>
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
                        <span className={`quality-badge ${(asset as any).data_quality === 'REAL' ? 'quality-real' : 'quality-sim'}`}>{(asset as any).data_quality ?? 'N/D'}</span>
                      </div>
                      <h4 className="mt-3 text-lg font-black tracking-tight text-white">{asset.symbol}</h4>
                      <p className="mt-1 text-[10px] font-black uppercase tracking-widest text-slate-500">{asset.timeframe ?? 'N/D'} · {(asset as any).market_status ?? asset.status ?? 'N/D'}</p>
                    </div>
                    <span className="rounded-full border border-white/10 bg-white/[0.035] px-3 py-1 text-[10px] font-black uppercase tracking-widest text-slate-300">{asset.status ?? 'N/D'}</span>
                  </div>

                  <div className="mt-4 grid grid-cols-3 gap-2">
                    <MiniMetric label="Payout" value={typeof (asset as any).payout === 'number' ? `${Math.round((asset as any).payout)}%` : 'N/D'} tone="cyan" />
                    <MiniMetric label="Fonte" value={(asset as any).data_quality ?? 'N/D'} />
                    <MiniMetric label="Mercado" value={(asset as any).market_status ?? asset.status ?? 'N/D'} />
                  </div>
                </button>
              );
            })}
          </div>
        ))}
      </div>

      <p className="mt-3 px-1 text-[11px] leading-relaxed text-slate-500">Role horizontalmente de 3 em 3. Clique em um card para selecionar explicitamente o ativo.</p>
    </div>
  );
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
