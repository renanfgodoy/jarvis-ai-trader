import { useMemo, useState } from 'react';
import type { MarketAsset } from '../types/api';

const defaultSymbols = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'BTC/USD', 'EUR/JPY'];

function normalizeSymbol(symbol: string) {
  return symbol.replace('/', '').replace('-OTC', '').toUpperCase();
}

export function useWatchlist(assets: MarketAsset[] = []) {
  const [selectedSymbol, setSelectedSymbol] = useState(defaultSymbols[0]);

  const items = useMemo(() => defaultSymbols.map((symbol) => {
    const normalized = normalizeSymbol(symbol);
    const match = assets.find((asset) => normalizeSymbol(asset.symbol).startsWith(normalized));

    return {
      symbol,
      providerSymbol: match?.symbol ?? null,
      status: match?.status ?? 'Não disponível',
      payout: typeof match?.payout === 'number' ? `${Math.round(match.payout)}%` : 'Não disponível',
      dataQuality: match?.data_quality ?? 'Não disponível',
      isSelected: selectedSymbol === symbol
    };
  }), [assets, selectedSymbol]);

  return { items, selectedSymbol, setSelectedSymbol };
}
