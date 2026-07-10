import type { PolariumAccountState, PolariumOAuthSessionState } from '../types/api';

export type ConnectionStepState = 'success' | 'running' | 'error' | 'pending' | 'blocked';

export type ConnectionWizardStep = {
  id: string;
  label: string;
  description: string;
  state: ConnectionStepState;
  statusLabel: string;
};

export function useConnectionWizard({
  account,
  oauth,
  loading = false
}: {
  account?: PolariumAccountState;
  oauth?: PolariumOAuthSessionState;
  loading?: boolean;
}): ConnectionWizardStep[] {
  const oauthOk = Boolean(oauth?.has_token || oauth?.status === 'TOKEN_STORED' || oauth?.status === 'CALLBACK_RECEIVED');
  const oauthError = Boolean(oauth?.last_error || oauth?.status === 'EXCHANGE_FAILED');
  const sessionOk = Boolean(account?.connected || account?.session_cached);
  const accountOk = Boolean(account?.connected && account?.email_masked);
  const currencyOk = Boolean(account?.is_balance_synced && account?.currency);
  const readyOk = Boolean(currencyOk && account?.account_mode === 'DEMO' && account?.status === 'CONNECTED');

  return [
    {
      id: 'oauth',
      label: 'OAuth',
      description: oauthOk ? 'Sessão OAuth encontrada.' : oauthError ? 'OAuth precisa de atenção.' : 'Não verificado.',
      state: oauthOk ? 'success' : oauthError ? 'error' : loading ? 'running' : 'pending',
      statusLabel: oauthOk ? 'Concluído' : oauthError ? 'Erro' : loading ? 'Em andamento' : 'Não verificado'
    },
    {
      id: 'session',
      label: 'Sessão',
      description: sessionOk ? 'Sessão operacional disponível.' : account?.connected === false ? 'Sessão não encontrada.' : 'Não verificado.',
      state: sessionOk ? 'success' : oauthError ? 'blocked' : loading ? 'running' : 'pending',
      statusLabel: sessionOk ? 'Concluído' : oauthError ? 'Bloqueado' : loading ? 'Em andamento' : 'Não verificado'
    },
    {
      id: 'websocket',
      label: 'WebSocket',
      description: account?.is_balance_synced ? 'Sincronização de conta recebida.' : sessionOk ? 'Aguardando sincronização.' : 'Não verificado.',
      state: account?.is_balance_synced ? 'success' : sessionOk ? 'running' : 'blocked',
      statusLabel: account?.is_balance_synced ? 'Concluído' : sessionOk ? 'Em andamento' : 'Bloqueado'
    },
    {
      id: 'account',
      label: 'Conta',
      description: accountOk ? 'Conta identificada com segurança.' : sessionOk ? 'Conta ainda não sincronizada.' : 'Não verificado.',
      state: accountOk ? 'success' : sessionOk ? 'pending' : 'blocked',
      statusLabel: accountOk ? 'Concluído' : sessionOk ? 'Aguardando' : 'Bloqueado'
    },
    {
      id: 'currency',
      label: 'Moeda',
      description: currencyOk ? `Moeda identificada: ${account?.currency}.` : accountOk ? 'Moeda da conta não identificada.' : 'Não verificado.',
      state: currencyOk ? 'success' : accountOk ? 'pending' : 'blocked',
      statusLabel: currencyOk ? 'Concluído' : accountOk ? 'Aguardando' : 'Bloqueado'
    },
    {
      id: 'ready',
      label: 'READY',
      description: readyOk ? 'Sessão pronta para análise em modo seguro.' : 'Fluxo bloqueado até sessão e moeda estarem sincronizadas.',
      state: readyOk ? 'success' : 'blocked',
      statusLabel: readyOk ? 'Concluído' : 'Bloqueado'
    }
  ];
}
