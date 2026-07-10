import { useQuery } from '@tanstack/react-query';
import { Activity, Clock3, PlugZap, RefreshCw, WalletCards, Wifi } from 'lucide-react';
import Card from '../../components/Card';
import PageContainer from '../../components/PageContainer';
import PageTitle from '../../components/PageTitle';
import Section from '../../components/Section';
import StatusBadge from '../../components/StatusBadge';
import PolariumLoginPanel from '../../components/PolariumLoginPanel';
import { usePolariumAccount } from '../../hooks/usePolariumAccount';
import { getPolariumOAuthSession } from '../../services/api';

export default function PolariumConnections() {
  const { polarium, login, logout, sync, ingestPayload, loading } = usePolariumAccount();
  const oauth = useQuery({ queryKey: ['polarium-oauth-session'], queryFn: getPolariumOAuthSession, refetchInterval: 10000 });
  const account = polarium.data;
  const synced = Boolean(account?.is_balance_synced);

  return (
    <PageContainer>
      <PageTitle eyebrow="Conexões" title="Polarium Connection Center">
        <StatusBadge status={account?.connected ? 'CONECTADO' : 'OFFLINE'} tone={account?.connected ? 'success' : 'warning'} />
      </PageTitle>

      <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_380px]">
        <Section title="Fluxo visual">
          <div className="grid gap-2 md:grid-cols-6">
            <FlowStep icon={PlugZap} label="Não conectado" active={!account?.connected} />
            <FlowStep icon={Activity} label="OAuth" active={Boolean(oauth.data?.has_token)} />
            <FlowStep icon={Clock3} label="Sessão" active={Boolean(account?.session_cached)} />
            <FlowStep icon={Wifi} label="WebSocket" active={synced} />
            <FlowStep icon={WalletCards} label="Conta" active={synced} />
            <FlowStep icon={RefreshCw} label="Pronto" active={synced && account?.account_mode === 'DEMO'} />
          </div>
        </Section>

        <PolariumLoginPanel
          account={account}
          loading={loading}
          onLogin={(email, password, remember) => login.mutate({ email, password, remember })}
          onLogout={() => logout.mutate()}
          onSync={() => sync.mutate()}
          onIngestPayload={(payloadText) => ingestPayload.mutate(payloadText)}
        />
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <InfoCard label="Status" value={account?.status ?? 'DISCONNECTED'} tone={account?.connected ? 'success' : 'warning'} />
        <InfoCard label="OAuth" value={oauth.data?.status ?? 'READY'} tone={oauth.data?.has_token ? 'success' : 'neutral'} />
        <InfoCard label="Moeda" value={account?.currency ?? '—'} />
        <InfoCard label="Última sincronização" value={account?.last_sync ?? '—'} />
      </div>

      {account?.last_sync_error && (
        <Card>
          <p className="eyebrow">Último erro</p>
          <p className="mt-2 text-sm text-amber-200">{account.last_sync_error}</p>
        </Card>
      )}
    </PageContainer>
  );
}

function FlowStep({ icon: Icon, label, active }: { icon: React.ElementType; label: string; active: boolean }) {
  return (
    <div className={`rounded-2xl border p-3 text-center ${active ? 'border-cyan-400/30 bg-cyan-400/10 text-cyan-200' : 'border-white/10 bg-white/[0.025] text-slate-400'}`}>
      <Icon className="mx-auto" size={22} />
      <p className="mt-2 text-[10px] font-black uppercase tracking-widest">{label}</p>
    </div>
  );
}

function InfoCard({ label, value, tone = 'neutral' }: { label: string; value: string; tone?: 'success' | 'warning' | 'neutral' }) {
  const color = tone === 'success' ? 'text-emerald-300' : tone === 'warning' ? 'text-amber-300' : 'text-white';
  return (
    <Card>
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className={`mt-2 break-words text-sm font-black ${color}`}>{value}</p>
    </Card>
  );
}
