import { ArrowDown, ArrowUp, Minus, Trophy } from 'lucide-react';
import type { AssetScannerResult } from '../types/api';

type Props = {
  assets: AssetScannerResult[];
  selectedSymbol?: string;
  onSelect?: (symbol: string) => void;
};

export default function TopAssets({ assets, selectedSymbol, onSelect }: Props) {
  const visibleAssets = assets.length ? assets.slice(0, 12) : fallbackAssets;

  return (
    <div className="panel h-full p-3 scanner-table-panel">
      <div className="flex items-center justify-between px-1">
        <div>
          <p className="eyebrow">Scanner IA · Top 12</p>
          <h3 className="mt-1 text-sm font-black text-white">Mesa de Ativos</h3>
        </div>
        <Trophy className="text-amber-300" size={17} />
      </div>

      <div className="mt-3 overflow-hidden rounded-2xl border border-white/10">
        <div className="grid grid-cols-[28px_1fr_50px_34px] bg-white/[0.035] px-3 py-2 text-[9px] uppercase tracking-widest text-slate-500">
          <span>#</span><span>Ativo</span><span>Score</span><span>IA</span>
        </div>
        <div className="divide-y divide-white/5">
          {visibleAssets.map((asset, index) => {
            const active = asset.symbol === selectedSymbol;
            return (
              <button
                key={`${asset.symbol}-${index}`}
                onClick={() => onSelect?.(asset.symbol)}
                className={`grid w-full grid-cols-[28px_1fr_50px_34px] items-center px-3 py-[9px] text-left text-xs transition ${active ? 'bg-cyan-400/15 ring-1 ring-inset ring-cyan-400/40' : 'hover:bg-cyan-400/10'}`}
              >
                <span className={`font-black ${active ? 'text-cyan-300' : 'text-slate-500'}`}>{asset.rank ?? index + 1}</span>
                <div className="min-w-0">
                  <p className="truncate font-black text-white">{asset.symbol}</p>
                  <p className="text-[9px] uppercase tracking-wider text-slate-500">{asset.risk_level ?? 'LOW'} · {asset.status ?? 'WATCHLIST'}</p>
                </div>
                <span className={`font-black ${scoreColor(asset.score ?? 0)}`}>{Math.round(asset.score ?? 0)}%</span>
                <span className="flex justify-end"><SignalIcon signal={asset.signal} /></span>
              </button>
            );
          })}
        </div>
      </div>
      <p className="mt-3 px-1 text-[11px] leading-relaxed text-slate-500">Clique em um ativo para sincronizar o gráfico, IA e leitura do workspace.</p>
    </div>
  );
}

function scoreColor(score: number) {
  if (score >= 90) return 'text-emerald-300';
  if (score >= 75) return 'text-amber-300';
  return 'text-slate-400';
}

function SignalIcon({ signal }: { signal?: string }) {
  if (signal === 'BUY' || signal === 'CALL') return <ArrowUp className="text-emerald-300" size={15} />;
  if (signal === 'SELL' || signal === 'PUT') return <ArrowDown className="text-red-300" size={15} />;
  return <Minus className="text-slate-400" size={15} />;
}

const fallbackAssets: AssetScannerResult[] = [
  { rank: 1, symbol: 'GBPUSD-OTC', signal: 'BUY', score: 96, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 2, symbol: 'EURUSD-OTC', signal: 'BUY', score: 94, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 3, symbol: 'BTCUSD-OTC', signal: 'SELL', score: 93, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 4, symbol: 'NZDUSD-OTC', signal: 'BUY', score: 92, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 5, symbol: 'AUDUSD-OTC', signal: 'BUY', score: 90, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 6, symbol: 'USDJPY-OTC', signal: 'SELL', score: 89, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 7, symbol: 'EURJPY-OTC', signal: 'BUY', score: 88, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 8, symbol: 'GOLD-OTC', signal: 'BUY', score: 87, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 9, symbol: 'USOIL-OTC', signal: 'BUY', score: 84, risk_level: 'LOW', status: 'WATCHLIST' },
  { rank: 10, symbol: 'ETHUSD-OTC', signal: 'SELL', score: 83, risk_level: 'LOW', status: 'WATCHLIST' },
  { rank: 11, symbol: 'GBPJPY-OTC', signal: 'BUY', score: 81, risk_level: 'LOW', status: 'WATCHLIST' },
  { rank: 12, symbol: 'AUDJPY-OTC', signal: 'SELL', score: 79, risk_level: 'LOW', status: 'WATCHLIST' }
];
