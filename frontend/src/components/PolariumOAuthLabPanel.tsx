import { useMutation, useQuery } from '@tanstack/react-query';
import { ExternalLink, KeyRound, RefreshCw, ShieldAlert } from 'lucide-react';
import { getPolariumOAuthConfig, getPolariumOAuthSession, startPolariumOAuth } from '../services/api';

export default function PolariumOAuthLabPanel() {
  const config = useQuery({ queryKey: ['polarium-oauth-config'], queryFn: getPolariumOAuthConfig, refetchInterval: 10000 });
  const session = useQuery({ queryKey: ['polarium-oauth-session'], queryFn: getPolariumOAuthSession, refetchInterval: 10000 });
  const start = useMutation({ mutationFn: startPolariumOAuth });
  const current = start.data;
  const ready = Boolean(current?.ready && current.authorize_url);

  return (
    <div className="panel p-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="eyebrow">OAuth Session Engine</p>
          <h3 className="mt-1 text-sm font-black text-white">Conexão Polarium OAuth/PKCE</h3>
        </div>
        <div className={`rounded-full border px-3 py-1 text-[10px] font-black uppercase tracking-widest ${config.data?.configured ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300' : 'border-amber-400/30 bg-amber-400/10 text-amber-300'}`}>
          {config.data?.configured ? 'CONFIG OK' : 'SEM CONFIG'}
        </div>
      </div>

      <div className="mt-3 rounded-2xl border border-white/10 bg-slate-950/40 p-3 text-[11px] leading-relaxed text-slate-400">
        <p><b className="text-white">Status:</b> {session.data?.message ?? 'verificando...'}</p>
        <p className="mt-1"><b className="text-white">Callback:</b> {config.data?.redirect_uri ?? '—'}</p>
        <p className="mt-1"><b className="text-white">Token URL:</b> {config.data?.token_url ?? '—'}</p>
      </div>

      {!config.data?.configured && (
        <div className="mt-3 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-3 text-[11px] leading-relaxed text-amber-100/90">
          <p className="flex items-center gap-2 font-black uppercase tracking-widest text-amber-200"><ShieldAlert size={13} /> Falta configuração</p>
          <p className="mt-1">Configure POLARIUM_OAUTH_CLIENT_ID próprio/autorizado no .env. As URLs authorize/token já vêm preenchidas pelo J.A.R.V.I.S. Não use credenciais de outro app.</p>
        </div>
      )}

      <button onClick={() => start.mutate()} disabled={start.isPending} className="toolbar-btn mt-3 w-full justify-center border-cyan-400/30 text-cyan-100 disabled:opacity-60">
        <KeyRound size={14} /> {start.isPending ? 'Gerando...' : 'Gerar URL de Login'}
      </button>

      {current && (
        <div className="mt-3 space-y-2 rounded-2xl border border-cyan-400/15 bg-cyan-400/[0.035] p-3 text-xs text-slate-300">
          <p><b className="text-white">State:</b> {current.state}</p>
          <p><b className="text-white">Challenge:</b> {current.code_challenge.slice(0, 18)}...</p>
          <p className="text-slate-400">{current.message}</p>
          {ready ? (
            <a href={current.authorize_url ?? '#'} target="_blank" rel="noreferrer" className="toolbar-btn w-full justify-center border-emerald-400/30 text-emerald-200">
              <ExternalLink size={14} /> Abrir login Polarium
            </a>
          ) : (
            <p className="text-amber-200">URL real ainda não gerada por falta de credenciais próprias.</p>
          )}
        </div>
      )}

      <button onClick={() => { config.refetch(); session.refetch(); }} className="toolbar-btn mt-2 w-full justify-center text-slate-200">
        <RefreshCw size={14} /> Atualizar status OAuth
      </button>
    </div>
  );
}
