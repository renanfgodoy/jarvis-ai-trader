import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import ConnectionActions from '../../components/connections/ConnectionActions';
import ConnectionAttemptHistory from '../../components/connections/ConnectionAttemptHistory';
import ConnectionErrorAlert from '../../components/connections/ConnectionErrorAlert';
import ConnectionStatusCard from '../../components/connections/ConnectionStatusCard';
import ConnectionSummary, { type ConnectionSummaryItem } from '../../components/connections/ConnectionSummary';
import ConnectionWizard from '../../components/connections/ConnectionWizard';
import Loading from '../../components/Loading';
import PageContainer from '../../components/PageContainer';
import PageTitle from '../../components/PageTitle';
import StatusBadge from '../../components/StatusBadge';
import { useConnectionHistory, sanitizeConnectionMessage } from '../../hooks/useConnectionHistory';
import { useConnectionWizard } from '../../hooks/useConnectionWizard';
import { usePolariumAccount } from '../../hooks/usePolariumAccount';
import { usePolariumConnection } from '../../hooks/usePolariumConnection';
import { getMarketAssets, getPolariumOAuthSession } from '../../services/api';

export default function PolariumConnections() {
  const { polarium, login, logout, sync, loading } = usePolariumAccount();
  const oauth = useQuery({ queryKey: ['polarium-oauth-session'], queryFn: getPolariumOAuthSession, refetchInterval: 10000 });
  const market = useQuery({ queryKey: ['market-assets'], queryFn: getMarketAssets, refetchInterval: 10000 });
  const { attempts, addAttempt, clearAttempts } = useConnectionHistory();
  const [feedback, setFeedback] = useState<string | null>(null);

  const account = polarium.data;
  const pageLoading = polarium.isLoading || oauth.isLoading || market.isLoading;
  const actionLoading = loading || polarium.isFetching || oauth.isFetching || market.isFetching;
  const steps = useConnectionWizard({ account, oauth: oauth.data, market: market.data, loading: actionLoading });
  const connection = usePolariumConnection({ account, oauth: oauth.data, market: market.data, steps });

  const summaryItems = useMemo<ConnectionSummaryItem[]>(() => [
    { label: 'Broker', value: connection.broker },
    { label: 'Tipo de conta', value: connection.accountMode, tone: connection.accountMode === 'DEMO' ? 'success' : 'warning' },
    { label: 'Ambiente', value: connection.environment, tone: connection.environment === 'DEMO' ? 'success' : 'warning' },
    { label: 'Moeda', value: connection.currency, tone: connection.currency === 'Não identificada' ? 'warning' : 'success' },
    { label: 'Saldo', value: connection.balance, tone: connection.balance === 'Não sincronizado' ? 'warning' : 'success' },
    { label: 'Connector status', value: connection.connectorStatus, tone: account?.connected ? 'success' : 'warning' },
    { label: 'WebSocket status', value: connection.websocketStatus, tone: connection.websocketStatus === 'Sincronizado' ? 'success' : 'warning' },
    { label: 'Market status', value: connection.marketStatus, tone: market.data ? 'success' : 'warning' },
    { label: 'Operação disponível', value: connection.operationAvailable, tone: connection.readiness === 'ready' ? 'success' : 'danger' }
  ], [account?.connected, connection, market.data]);

  const runAction = async (action: string, step: string, callback: () => Promise<{ message?: string } | unknown>) => {
    if (actionLoading) return;
    setFeedback(null);
    try {
      const response = await callback();
      const message = sanitizeConnectionMessage(response, `${action} concluído.`);
      setFeedback(message);
      addAttempt({ action, step, result: 'success', message });
    } catch (error) {
      const message = sanitizeConnectionMessage(extractErrorMessage(error), `${action} falhou.`);
      setFeedback(message);
      addAttempt({ action, step, result: 'error', message });
    }
  };

  return (
    <PageContainer>
      <PageTitle eyebrow="Conexões" title="Polarium Connection Center">
        <StatusBadge status={connection.statusLabel} tone={connection.statusTone} />
      </PageTitle>

      {pageLoading && <Loading label="Verificando conexão Polarium" />}

      <ConnectionStatusCard data={{
        broker: connection.broker,
        statusLabel: connection.statusLabel,
        statusTone: connection.statusTone,
        environment: connection.environment,
        accountLabel: connection.accountLabel,
        currency: connection.currency,
        balance: connection.balance,
        lastSync: connection.lastSync,
        lastUpdate: connection.lastUpdate,
        lastError: connection.lastError
      }} />

      <ConnectionWizard steps={steps} />

      <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_420px]">
        <ConnectionSummary items={summaryItems} readiness={connection.readiness} />
        <ConnectionActions
          connected={Boolean(account?.connected)}
          loading={actionLoading}
          feedback={feedback}
          onConnect={(email, password, remember) => runAction('Conectar', 'OAuth', () => login.mutateAsync({ email, password, remember }))}
          onSync={() => runAction('Sincronizar', 'Conta', () => sync.mutateAsync())}
          onRefresh={() => runAction('Atualizar status', 'Status', async () => {
            await Promise.all([polarium.refetch(), oauth.refetch(), market.refetch()]);
            return { message: 'Status atualizado.' };
          })}
          onDisconnect={() => runAction('Desconectar', 'Sessão', () => logout.mutateAsync())}
        />
      </div>

      <ConnectionErrorAlert message={connection.lastError || oauth.data?.last_error || null} />

      <details className="rounded-2xl border border-white/10 bg-white/[0.025] p-4">
        <summary className="cursor-pointer text-[10px] font-black uppercase tracking-widest text-slate-400">Detalhes técnicos sanitizados</summary>
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <SafeDetail label="OAuth" value={connection.oauthStatus} />
          <SafeDetail label="Fonte" value={account?.data_source ?? 'UNAVAILABLE'} />
          <SafeDetail label="Sync" value={account?.sync_status ?? 'NOT_SYNCED'} />
          <SafeDetail label="Passos bloqueados" value={String(connection.blockedSteps)} />
        </div>
      </details>

      <ConnectionAttemptHistory attempts={attempts} onClear={clearAttempts} />
    </PageContainer>
  );
}

function SafeDetail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className="mt-2 break-words text-sm font-black text-white">{sanitizeConnectionMessage(value, 'Não verificado')}</p>
    </div>
  );
}

function extractErrorMessage(error: unknown): unknown {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const response = (error as { response?: { data?: { message?: unknown; detail?: unknown } } }).response;
    return response?.data?.message ?? response?.data?.detail ?? error;
  }

  return error;
}
