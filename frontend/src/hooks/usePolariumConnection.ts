import type { MarketAssetsResponse, PolariumAccountState, PolariumOAuthSessionState } from '../types/api';
import { sanitizeConnectionMessage } from './useConnectionHistory';
import type { ConnectionWizardStep } from './useConnectionWizard';

export type ConnectionReadiness = 'ready' | 'blocked' | 'pending';

export function usePolariumConnection({
  account,
  oauth,
  market,
  steps
}: {
  account?: PolariumAccountState;
  oauth?: PolariumOAuthSessionState;
  market?: MarketAssetsResponse;
  steps: ConnectionWizardStep[];
}) {
  const synced = Boolean(account?.is_balance_synced);
  const ready = Boolean(
    account?.connected &&
    account?.status === 'CONNECTED' &&
    synced &&
    account?.currency &&
    market &&
    market.data_quality !== 'UNAVAILABLE'
  );

  const readiness: ConnectionReadiness = ready ? 'ready' : account?.connected ? 'pending' : 'blocked';
  const blockedSteps = steps.filter((step) => step.state === 'blocked' || step.state === 'error').length;

  const formatMoney = () => {
    if (!synced || typeof account?.balance !== 'number') return 'Não sincronizado';
    return `${account.currency_symbol ?? ''} ${account.balance.toFixed(2)}`.trim();
  };

  return {
    broker: 'Polarium',
    statusLabel: account?.connected ? 'Conectado' : 'Não conectado',
    statusTone: account?.connected ? 'success' as const : 'warning' as const,
    accountLabel: account?.email_masked ?? 'Não identificada',
    accountMode: account?.account_mode ?? 'DEMO',
    environment: account?.demo_only === false ? 'REAL' : 'DEMO',
    currency: synced && account?.currency ? account.currency : 'Não identificada',
    balance: formatMoney(),
    lastSync: account?.last_sync ?? 'Não verificada',
    lastUpdate: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    lastError: account?.last_sync_error ? sanitizeConnectionMessage(account.last_sync_error, 'Falha ao sincronizar conta.') : null,
    connectorStatus: account?.status ?? 'DISCONNECTED',
    websocketStatus: synced ? 'Sincronizado' : account?.connected ? 'Não verificado' : 'Bloqueado',
    marketStatus: market ? `${market.data_quality} · ${market.open_assets}/${market.total_assets} abertos` : 'Não verificado',
    operationAvailable: ready ? 'Disponível para análise' : 'Bloqueada',
    readiness,
    blockedSteps,
    oauthStatus: oauth?.status ?? 'Não verificado'
  };
}
