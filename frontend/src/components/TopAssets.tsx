import { ArrowDown, ArrowUp, Minus, Trophy } from 'lucide-react';
import type { AssetScannerResult } from '../types/api';

export default function TopAssets({ assets }: { assets: AssetScannerResult[] }) {
  const visibleAssets = assets.length ? assets.slice(0, 12) : fallbackAssets;

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Scanner IA</p>
          <h3 className="mt-1 text-xl font-black text-white">Top 12 Ativos</h3>
        </div>
        <Trophy className="text-amber-300" />
      </div>

      <div className="mt-5 space-y-3">
        {visibleAssets.map((asset, index) => (
          <div key={`${asset.symbol}-${index}`} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] p-3">
            <div className="flex items-center gap-3">
              <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-cyan-400/10 text-sm font-black text-cyan-300">
                {asset.rank ?? index + 1}
              </span>
              <div>
                <p className="font-bold text-white">{asset.symbol}</p>
                <p className="text-xs text-slate-500">{asset.risk_level ?? 'LOW'} • {asset.status ?? 'WATCHLIST'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <SignalIcon signal={asset.signal} />
              <span className="text-lg font-black text-emerald-300">{Math.round(asset.score ?? 0)}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SignalIcon({ signal }: { signal?: string }) {
  if (signal === 'BUY' || signal === 'CALL') return <ArrowUp className="text-emerald-300" size={18} />;
  if (signal === 'SELL' || signal === 'PUT') return <ArrowDown className="text-red-300" size={18} />;
  return <Minus className="text-slate-400" size={18} />;
}

const fallbackAssets: AssetScannerResult[] = [
  { rank: 1, symbol: 'EURUSD-OTC', signal: 'BUY', score: 94, risk_level: 'LOW', status: 'APPROVED' },
  { rank: 2, symbol: 'BTCUSD-OTC', signal: 'WAIT', score: 88, risk_level: 'LOW', status: 'WATCHLIST' },
  { rank: 3, symbol: 'ETHUSD-OTC', signal: 'SELL', score: 85, risk_level: 'LOW', status: 'APPROVED' }
];
