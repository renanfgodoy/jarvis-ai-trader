import { useEffect, useState } from 'react';
import { LockKeyhole, LogOut, RefreshCw, ShieldAlert, ShieldCheck, WalletCards, Wifi } from 'lucide-react';
import type { PolariumAccountState } from '../types/api';

export default function PolariumLoginPanel({
  account,
  onLogin,
  onLogout,
  onSync,
  onIngestPayload,
  loading = false
}: {
  account?: PolariumAccountState;
  onLogin: (email: string, password: string, remember: boolean) => void;
  onLogout: () => void;
  onSync: () => void;
  onIngestPayload?: (payloadText: string) => void;
  loading?: boolean;
}) {
  const [email, setEmail] = useState(() => localStorage.getItem('jarvis.polarium.email') ?? '');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [payloadText, setPayloadText] = useState('');
  const [payloadError, setPayloadError] = useState<string | null>(null);

  useEffect(() => {
    if (email) localStorage.setItem('jarvis.polarium.email', email);
  }, [email]);

  const connected = Boolean(account?.connected);
  const synced = Boolean(account?.is_balance_synced && ['REAL_SESSION', 'DEVTOOLS_PAYLOAD'].includes(account?.data_source ?? ''));
  const symbol = account?.currency_symbol ?? '';
  const balanceLabel = synced && typeof account?.balance === 'number' ? `${symbol} ${account.balance.toFixed(2)}` : 'Não sincronizado';
  const currencyLabel = synced ? account?.currency ?? '—' : '—';
  const minLabel = synced && typeof account?.minimum_entry === 'number' ? `${symbol} ${account.minimum_entry.toFixed(2)}` : '—';
  const statusLabel = synced ? 'LIVE SYNC' : connected ? 'AGUARDANDO SYNC' : 'OFFLINE';

  return (
    <div className="panel p-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Polarium</p>
          <h3 className="mt-1 text-sm font-black text-white">Live Connection</h3>
        </div>
        <div className={`rounded-full border px-3 py-1 text-[10px] font-black uppercase tracking-widest ${connected ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300' : 'border-amber-400/30 bg-amber-400/10 text-amber-300'}`}>
          {connected ? 'Conectado' : 'Desconectado'}
        </div>
      </div>

      {connected ? (
        <div className="mt-3 space-y-3">
          <div className={`rounded-2xl border p-3 ${synced ? 'border-emerald-400/20 bg-emerald-400/5' : 'border-amber-400/20 bg-amber-400/5'}`}>
            <div className="flex items-center gap-2">
              {synced ? <ShieldCheck size={16} className="text-emerald-300" /> : <ShieldAlert size={16} className="text-amber-300" />}
              <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Status da conexão</p>
                <p className={`text-xs font-black ${synced ? 'text-emerald-300' : 'text-amber-300'}`}>{statusLabel}</p>
              </div>
            </div>
            {!synced && (
              <p className="mt-2 text-[11px] leading-relaxed text-amber-100/80">
                Sessão salva, mas o saldo real ainda não foi sincronizado por uma conexão autorizada. O J.A.R.V.I.S não exibe saldo falso e mantém o AutoTrade bloqueado.
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2">
            <Info icon={<ShieldCheck size={14} />} label="Modo" value={account?.account_mode ?? 'DEMO'} tone="green" />
            <Info icon={<WalletCards size={14} />} label="Saldo" value={balanceLabel} tone={synced ? 'cyan' : 'amber'} />
            <Info label="Moeda" value={currencyLabel} />
            <Info label="Mínimo" value={minLabel} tone="amber" />
          </div>

          <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-3 text-xs text-slate-300">
            <p><b className="text-white">Sessão:</b> {account?.email_masked ?? 'cache local'}</p>
            <p className="mt-1 text-slate-500">Cache: {account?.session_cached ? 'ativo' : 'não salvo'} · senha nunca é armazenada.</p>
            <p className="mt-1 text-slate-500">Fonte: {account?.data_source ?? 'UNAVAILABLE'} · {account?.sync_status ?? 'NOT_SYNCED'}</p>
            {account?.last_sync_error && <p className="mt-2 text-amber-200">{account.last_sync_error}</p>}
          </div>

          <div className="rounded-2xl border border-cyan-400/15 bg-cyan-400/[0.035] p-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-cyan-300">Live payload parser</p>
            <p className="mt-1 text-[11px] leading-relaxed text-slate-400">
              Cole aqui o JSON completo do evento <b>marginal-balance</b> capturado no DevTools da sua sessão Polarium. Isso atualiza o saldo no dashboard sem usar Swagger.
            </p>
            <textarea
              className="mt-2 min-h-[92px] w-full resize-y rounded-2xl border border-white/10 bg-slate-950/70 p-3 font-mono text-[11px] text-slate-200 outline-none focus:border-cyan-400/50"
              value={payloadText}
              onChange={(event) => {
                setPayloadText(event.target.value);
                setPayloadError(null);
              }}
              placeholder='{"name":"marginal-balance","msg":{"available":"16037.53","cash":"16037.53","equity":"16037.53","currency":"USD","id":1241028586,"user_id":191243694}}'
            />
            {payloadError && <p className="mt-1 text-[11px] text-red-300">{payloadError}</p>}
            <button
              type="button"
              disabled={loading || !payloadText.trim() || !onIngestPayload}
              onClick={() => {
                try {
                  JSON.parse(payloadText);
                  setPayloadError(null);
                  onIngestPayload?.(payloadText);
                } catch {
                  setPayloadError('JSON inválido. Copie o objeto completo da mensagem marginal-balance.');
                }
              }}
              className="toolbar-btn mt-2 w-full justify-center border-emerald-400/30 text-emerald-200 disabled:opacity-60"
            >
              <RefreshCw size={14} /> Aplicar payload real no Dashboard
            </button>
          </div>

          <button onClick={onSync} disabled={loading} className="toolbar-btn w-full justify-center border-cyan-400/30 text-cyan-100 disabled:opacity-60">
            <RefreshCw size={14} /> Sincronizar Conta
          </button>
          <button onClick={onLogout} className="toolbar-btn w-full justify-center text-red-200">
            <LogOut size={14} /> Sair da Polarium
          </button>
        </div>
      ) : (
        <form
          className="mt-3 space-y-2"
          onSubmit={(event) => {
            event.preventDefault();
            onLogin(email, password, remember);
          }}
        >
          <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">E-mail Polarium</label>
          <input
            className="login-input"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="seu@email.com"
            type="email"
            required
          />
          <label className="block text-[10px] font-black uppercase tracking-widest text-slate-500">Senha</label>
          <input
            className="login-input"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Senha da Polarium"
            type="password"
            required
          />
          <label className="flex items-center gap-2 text-xs text-slate-400">
            <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />
            Manter sessão no cache local
          </label>
          <button disabled={loading} className="toolbar-btn w-full justify-center border-cyan-400/30 text-cyan-100 disabled:opacity-60">
            <LockKeyhole size={14} /> {loading ? 'Conectando...' : 'Conectar em DEMO'}
          </button>
          <div className="rounded-2xl border border-cyan-400/15 bg-cyan-400/[0.035] p-3 text-[11px] leading-relaxed text-slate-400">
            <p className="flex items-center gap-2 font-black uppercase tracking-widest text-cyan-300"><Wifi size={13} /> No Swagger Flow</p>
            <p className="mt-1">O fluxo normal acontece pelo Dashboard. O Swagger fica apenas para debug técnico.</p>
          </div>
        </form>
      )}
    </div>
  );
}

function Info({ label, value, tone = 'white', icon }: { label: string; value: string; tone?: 'white' | 'cyan' | 'amber' | 'green'; icon?: React.ReactNode }) {
  const colors = { white: 'text-white', cyan: 'text-cyan-300', amber: 'text-amber-300', green: 'text-emerald-300' };
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-2">
      <p className="flex items-center gap-1 text-[9px] font-black uppercase tracking-widest text-slate-500">{icon}{label}</p>
      <p className={`mt-1 text-sm font-black ${colors[tone]}`}>{value}</p>
    </div>
  );
}
