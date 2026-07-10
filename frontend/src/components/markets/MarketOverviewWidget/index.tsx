import { BarChart3, RefreshCw, ScanSearch } from 'lucide-react';
import Card from '../../Card';

export type MarketOverview = {
  totalAssets: number;
  otcCount: number;
  synchronized: string;
  scannerStatus: string;
  lastUpdated: string;
};

export default function MarketOverviewWidget({ overview }: { overview: MarketOverview }) {
  const items = [
    { label: 'Quantidade de ativos', value: String(overview.totalAssets), icon: BarChart3 },
    { label: 'Quantidade OTC', value: String(overview.otcCount), icon: BarChart3 },
    { label: 'Mercado sincronizado', value: overview.synchronized, icon: RefreshCw },
    { label: 'Scanner ativo', value: overview.scannerStatus, icon: ScanSearch },
    { label: 'Última atualização', value: overview.lastUpdated, icon: RefreshCw }
  ];

  return (
    <Card>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Market Overview</p>
      <h3 className="mt-1 text-lg font-black text-white">Resumo de leitura</h3>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        {items.map((item) => (
          <div key={item.label} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
            <item.icon className="text-cyan-300" size={18} />
            <p className="mt-3 text-[10px] font-black uppercase tracking-widest text-slate-500">{item.label}</p>
            <p className="mt-1 break-words text-sm font-black text-white">{item.value}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
