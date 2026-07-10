import { useState } from 'react';
import DiscoveryTimeline from '../components/intelligence/DiscoveryTimeline';
import MarketDiscoveryStatus from '../components/intelligence/MarketDiscoveryStatus';
import MarketReadinessCard from '../components/intelligence/MarketReadinessCard';
import MarketSnapshotCard from '../components/intelligence/MarketSnapshotCard';
import MarketSourceCard from '../components/intelligence/MarketSourceCard';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import StatusBadge from '../components/StatusBadge';
import { brand } from '../branding/brand';
import { useMarketDiscovery } from '../intelligence/useMarketDiscovery';
import type { Timeframe } from '../types/api';

const timeframes: Timeframe[] = ['M1', 'M5', 'M15'];

export default function MarketIntelligence() {
  const [asset, setAsset] = useState('EURUSD-OTC');
  const [timeframe, setTimeframe] = useState<Timeframe>('M1');
  const discovery = useMarketDiscovery(asset, timeframe);

  return (
    <PageContainer>
      <PageTitle eyebrow={brand.name} title="Market Intelligence Discovery">
        <StatusBadge status="SEM IA" tone="neutral" />
      </PageTitle>

      <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_360px]">
        <div className="panel p-4">
          <p className="eyebrow">Resumo</p>
          <h2 className="mt-1 text-xl font-black text-white">Market Discovery observa. Ainda não decide.</h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-400">
            Esta camada organiza ativo, timeframe, broker, conta, moeda, ambiente, fonte e atualização para preparar o futuro AI Decision Engine.
          </p>
          <div className="mt-4 flex flex-wrap items-center gap-2">
            <input
              className="login-input max-w-[220px]"
              value={asset}
              onChange={(event) => setAsset(event.target.value.toUpperCase())}
              aria-label="Ativo observado"
            />
            {timeframes.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setTimeframe(item)}
                className={`rounded-xl border px-4 py-2 text-xs font-black transition ${
                  timeframe === item
                    ? 'border-cyan-400/50 bg-cyan-400/20 text-cyan-200'
                    : 'border-white/10 bg-white/[0.035] text-slate-400 hover:bg-white/[0.06]'
                }`}
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        <MarketReadinessCard readiness={discovery.readiness} />
      </div>

      <MarketSnapshotCard snapshot={discovery.snapshot} />

      <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_360px]">
        <MarketDiscoveryStatus items={discovery.discovery} />
        <MarketSourceCard source={discovery.source} />
      </div>

      <DiscoveryTimeline items={discovery.timeline} />
    </PageContainer>
  );
}
