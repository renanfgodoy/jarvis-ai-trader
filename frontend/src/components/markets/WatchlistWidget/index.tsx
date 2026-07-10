import { Star } from 'lucide-react';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

type WatchlistItem = {
  symbol: string;
  providerSymbol: string | null;
  status: string;
  payout: string;
  dataQuality: string;
  isSelected: boolean;
};

export default function WatchlistWidget({
  items,
  onSelect
}: {
  items: WatchlistItem[];
  onSelect: (symbol: string) => void;
}) {
  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Watchlist</p>
          <h3 className="mt-1 text-lg font-black text-white">Ativos favoritos</h3>
        </div>
        <Star className="text-cyan-300" size={20} />
      </div>
      <div className="mt-4 space-y-2">
        {items.map((item) => (
          <button
            key={item.symbol}
            type="button"
            onClick={() => onSelect(item.symbol)}
            className={`w-full rounded-2xl border p-3 text-left transition ${
              item.isSelected
                ? 'border-cyan-400/40 bg-cyan-400/10'
                : 'border-white/10 bg-white/[0.025] hover:bg-white/[0.05]'
            }`}
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-black text-white">{item.symbol}</p>
                <p className="mt-1 text-xs text-slate-500">{item.providerSymbol ?? 'Não disponível'}</p>
              </div>
              <StatusBadge status={item.status} tone={item.status === 'OPEN' ? 'success' : item.status === 'Não disponível' ? 'neutral' : 'warning'} />
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
              <Mini label="Payout" value={item.payout} />
              <Mini label="Dados" value={item.dataQuality} />
            </div>
          </button>
        ))}
      </div>
    </Card>
  );
}

function Mini({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-950/40 px-3 py-2">
      <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-1 font-black text-slate-200">{value}</p>
    </div>
  );
}
