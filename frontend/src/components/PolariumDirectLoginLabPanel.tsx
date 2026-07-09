import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { RefreshCw, ShieldAlert, Terminal, Trash2 } from 'lucide-react';
import { clearPolariumDirectSession, getPolariumDirectConfig, getPolariumDirectSession, probePolariumDirectLogin } from '../services/api';

export default function PolariumDirectLoginLabPanel() {
  const queryClient = useQueryClient();
  const config = useQuery({ queryKey: ['polarium-direct-config'], queryFn: getPolariumDirectConfig, refetchInterval: 7000 });
  const session = useQuery({ queryKey: ['polarium-direct-session'], queryFn: getPolariumDirectSession, refetchInterval: 7000 });
  const probe = useMutation({
    mutationFn: (dryRun: boolean) => probePolariumDirectLogin({ dry_run: dryRun, force_demo: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['polarium-direct-session'] });
      queryClient.invalidateQueries({ queryKey: ['polarium-direct-config'] });
    }
  });
  const clear = useMutation({
    mutationFn: clearPolariumDirectSession,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['polarium-direct-session'] })
  });

  const cfg = config.data;
  const current = probe.data;
  const sess = session.data;
  const configured = Boolean(cfg?.configured);
  const hasSession = Boolean(sess?.has_session);

  return (
    <div className="panel p-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Polarium</p>
          <h3 className="mt-1 text-sm font-black text-white">Direct Login Lab</h3>
        </div>
        <span className={`rounded-full border px-3 py-1 text-[10px] font-black uppercase tracking-widest ${configured ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300' : 'border-amber-400/30 bg-amber-400/10 text-amber-300'}`}>
          {configured ? 'CONFIG OK' : 'SEM CONFIG'}
        </span>
      </div>

      <div className="mt-3 rounded-2xl border border-white/10 bg-slate-950/45 p-3 text-[11px] leading-relaxed text-slate-400">
        <p className="flex items-center gap-2 font-black uppercase tracking-widest text-cyan-300"><Terminal size={13} /> Lab seguro</p>
        <p className="mt-1">Este teste usa apenas seu <b>.env local</b>. Senha não é digitada no dashboard e não é salva no código.</p>
        <p className="mt-1 text-amber-200">AutoTrade continua bloqueado até DEMO + saldo + moeda reais serem confirmados.</p>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2">
        <Info label="Login URL" value={cfg?.login_url_configured ? 'OK' : 'Falta'} tone={cfg?.login_url_configured ? 'green' : 'amber'} />
        <Info label="E-mail" value={cfg?.email_configured ? 'OK' : 'Falta'} tone={cfg?.email_configured ? 'green' : 'amber'} />
        <Info label="Senha" value={cfg?.password_configured ? 'OK' : 'Falta'} tone={cfg?.password_configured ? 'green' : 'amber'} />
        <Info label="Sessão" value={hasSession ? 'Salva' : 'Vazia'} tone={hasSession ? 'green' : 'white'} />
      </div>

      {cfg?.message && <p className="mt-3 text-[11px] text-slate-400">{cfg.message}</p>}
      {sess?.message && <p className="mt-2 text-[11px] text-slate-500">{sess.message}</p>}
      {current && (
        <div className="mt-3 rounded-2xl border border-cyan-400/15 bg-cyan-400/[0.035] p-3 text-[11px] text-slate-300">
          <p><b className="text-white">Status:</b> {current.status}</p>
          <p><b className="text-white">HTTP:</b> {current.http_status ?? '—'}</p>
          <p><b className="text-white">Token salvo:</b> {current.token_stored ? 'sim' : 'não'}</p>
          <p className="mt-1 text-slate-400">{current.message}</p>
          {current.warnings?.length ? <p className="mt-1 text-amber-200">{current.warnings[0]}</p> : null}
        </div>
      )}

      <div className="mt-3 flex flex-col gap-2">
        <button disabled={probe.isPending} onClick={() => probe.mutate(true)} className="toolbar-btn w-full justify-center text-cyan-100 disabled:opacity-60">
          <RefreshCw size={14} /> Testar dry run
        </button>
        <button disabled={probe.isPending || !configured} onClick={() => probe.mutate(false)} className="toolbar-btn w-full justify-center border-amber-400/30 text-amber-100 disabled:opacity-60">
          <ShieldAlert size={14} /> Tentar login direto
        </button>
        <button disabled={clear.isPending} onClick={() => clear.mutate()} className="toolbar-btn w-full justify-center text-red-200 disabled:opacity-60">
          <Trash2 size={14} /> Limpar sessão direta
        </button>
      </div>
    </div>
  );
}

function Info({ label, value, tone = 'white' }: { label: string; value: string; tone?: 'white' | 'green' | 'amber' }) {
  const color = tone === 'green' ? 'text-emerald-300' : tone === 'amber' ? 'text-amber-300' : 'text-white';
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-2">
      <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">{label}</p>
      <p className={`mt-1 text-xs font-black ${color}`}>{value}</p>
    </div>
  );
}
