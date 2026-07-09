import { ArrowDown, ArrowUp, Minus, Trophy } from 'lucide-react';
import type { AssetScannerResult } from '../types/api';

export default function TopAssets({ assets }: { assets: AssetScannerResult[] }) {
  const visibleAssets = assets.length ? assets.slice(0, 12) : fallbackAssets;

  return (
    <div className="panel h-full p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">Scanner IA · Top 12</p>
          <h3 className="mt-1 text-base font-black text-white">Selecionar Ativo</h3>
        </div>
        <Trophy className="text-amber-300" size={18} />
      </div>

      <div className="mt-4 overflow-hidden rounded-2xl border border-white/10">
        <div className="grid grid-cols-[34px_1fr_60px_42px] bg-white/[0.035] px-3 py-2 text-[10px] uppercase tracking-widest text-slate-500">
          <span>#</span><span>Ativo</span><span>Score</span><span>Dir.</span>
        </div>
        <div className="divide-y divide-white/5">
          {visibleAssets.map((asset, index) => (
            <div key={`${asset.symbol}-${index}`} className="grid grid-cols-[34px_1fr_60px_42px] items-center px-3 py-2.5 text-sm transition hover:bg-cyan-400/10">
              <span className="text-xs font-black text-slate-500">{asset.rank ?? index + 1}</span>
              <div className="min-w-0">
                <p className="truncate font-black text-white">{asset.symbol}</p>
                <p className="text-[10px] uppercase tracking-wider text-slate-500">{asset.risk_level ?? 'LOW'} · {asset.status ?? 'WATCHLIST'}</p>
              </div>
              <span className={`font-black ${scoreColor(asset.score ?? 0)}`}>{Math.round(asset.score ?? 0)}%</span>
              <span className="flex justify-end"><SignalIcon signal={asset.signal} /></span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function scoreColor(score: number) {
  if (score >= 90) return 'text-emerald-300';
  if (score >= 75) return 'text-amber-300';
  return 'text-slate-400';
}

function SignalIcon({ signal }: { signal?: string }) {
  if (signal === 'BUY' || signal === 'CALL') return <ArrowUp className="text-emerald-300" size={17} />;
  if (signal === 'SELL' || signal === 'PUT') return <ArrowDown className="text-red-300" size={17} />;
  return <Minus className="text-slate-400" size={17} />;
}

const fallbackAssets: AssetScannerResult[] = [
  { rank: 1, symbol: 'MSFT/AAPL-OTC', signal: 'BUY', score: 81, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 2, symbol: 'RAYDIUMUSD-OTC', signal: 'BUY', score: 76, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 3, symbol: 'GOOGLE-OTC', signal: 'SELL', score: 78, risk_level: 'LOW', status: 'WATCHLIST' }
];
