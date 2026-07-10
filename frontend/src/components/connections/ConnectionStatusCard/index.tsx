import { AlertTriangle, Clock3, Landmark, RefreshCw, WalletCards } from 'lucide-react';
import Card from '../../Card';
import StatusBadge from '../../StatusBadge';

export type ConnectionStatusCardData = {
  broker: string;
  statusLabel: string;
  statusTone: 'success' | 'warning' | 'danger' | 'neutral';
  environment: string;
  accountLabel: string;
  currency: string;
  balance: string;
  lastSync: string;
  lastUpdate: string;
  lastError: string | null;
};

export default function ConnectionStatusCard({ data }: { data: ConnectionStatusCardData }) {
  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Broker</p>
          <h2 className="mt-1 text-2xl font-black text-white">{data.broker}</h2>
        </div>
        <StatusBadge status={data.statusLabel} tone={data.statusTone} />
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Metric icon={Landmark} label="Ambiente" value={data.environment} />
        <Metric icon={WalletCards} label="Conta identificada" value={data.accountLabel} />
        <Metric icon={WalletCards} label="Moeda" value={data.currency} />
        <Metric icon={WalletCards} label="Saldo disponível" value={data.balance} />
        <Metric icon={RefreshCw} label="Última sincronização" value={data.lastSync} />
        <Metric icon={Clock3} label="Última atualização" value={data.lastUpdate} />
        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-3 md:col-span-2">
          <div className="flex items-center gap-2 text-amber-300">
            <AlertTriangle size={15} />
            <p className="text-[10px] font-black uppercase tracking-widest">Último erro sanitizado</p>
          </div>
          <p className="mt-2 text-sm font-semibold text-slate-300">{data.lastError ?? 'Nenhum erro registrado.'}</p>
        </div>
      </div>
    </Card>
  );
}

function Metric({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon size={15} />
        <p className="text-[10px] font-black uppercase tracking-widest">{label}</p>
      </div>
      <p className="mt-2 break-words text-sm font-black text-white">{value}</p>
    </div>
  );
}
