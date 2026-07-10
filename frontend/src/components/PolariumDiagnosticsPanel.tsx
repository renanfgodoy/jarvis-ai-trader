import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Activity, ClipboardCheck, PlugZap, RefreshCw, Wifi } from 'lucide-react';
import { getPolariumDiagnosticSummary, getPolariumOAuthDiagnostic, runPolariumStreamDiagnostic, runPolariumWebSocketDiagnostic } from '../services/api';
import type { DiagnosticCheck } from '../types/api';

const samplePayload = JSON.stringify([
  { name: 'marginal-balance', msg: { available: '16037.53', cash: '16037.53', equity: '16037.53', currency: 'USD', id: 1241028586, type: 4 } },
  { name: 'candle-generated', msg: { open: 1.103, close: 1.104, high: 1.105, low: 1.102 } },
  { name: 'digital-option-client-price-generated', msg: { price: 1.1042 } }
], null, 2);

export default function PolariumDiagnosticsPanel() {
  const [payloadText, setPayloadText] = useState(samplePayload);
  const summary = useQuery({ queryKey: ['polarium-diagnostics-summary'], queryFn: getPolariumDiagnosticSummary, refetchInterval: 15000 });
  const oauth = useMutation({ mutationFn: getPolariumOAuthDiagnostic });
  const websocket = useMutation({ mutationFn: () => runPolariumWebSocketDiagnostic({ timeout_seconds: 4, send_probe: false }) });
  const stream = useMutation({
    mutationFn: () => {
      const parsed = JSON.parse(payloadText);
      return runPolariumStreamDiagnostic(Array.isArray(parsed) ? parsed : [parsed]);
    }
  });

  return (
    <div className="panel p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="eyebrow">Diagnostics Lab</p>
          <h3 className="mt-1 text-sm font-black text-white">Polarium Connection Diagnostic</h3>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-500">V0.22 mede OAuth, WebSocket e eventos. Não promete conectar; mostra onde trava.</p>
        </div>
        <StatusBadge status={summary.data?.status ?? 'SKIPPED'} />
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2">
        <button onClick={() => oauth.mutate()} disabled={oauth.isPending} className="toolbar-btn justify-center text-cyan-100"><Activity size={14} /> OAuth</button>
        <button onClick={() => websocket.mutate()} disabled={websocket.isPending} className="toolbar-btn justify-center text-cyan-100"><Wifi size={14} /> WS</button>
        <button onClick={() => stream.mutate()} disabled={stream.isPending} className="toolbar-btn justify-center text-cyan-100"><ClipboardCheck size={14} /> Stream</button>
      </div>

      <button onClick={() => summary.refetch()} className="toolbar-btn mt-2 w-full justify-center text-slate-200"><RefreshCw size={14} /> Atualizar resumo</button>

      <div className="mt-3 space-y-2">
        <CheckList title="Resumo" checks={summary.data?.checks ?? []} nextAction={summary.data?.next_action} />
        {oauth.data && <CheckList title="OAuth Diagnostic" checks={oauth.data.checks} nextAction={oauth.data.next_action} />}
        {websocket.data && <CheckList title="WebSocket Diagnostic" checks={websocket.data.checks} nextAction={websocket.data.next_action} />}
        {stream.data && <CheckList title="Stream Diagnostic" checks={stream.data.checks} nextAction={stream.data.next_action} />}
        {(oauth.error || websocket.error || stream.error) && (
          <div className="rounded-2xl border border-red-400/20 bg-red-400/10 p-3 text-xs text-red-100">Erro no diagnóstico. Abra o Console/F12 e me mande o print.</div>
        )}
      </div>

      <details className="mt-3 rounded-2xl border border-white/10 bg-slate-950/40 p-3">
        <summary className="cursor-pointer text-[11px] font-black uppercase tracking-widest text-slate-400">Payloads para Stream Diagnostic</summary>
        <textarea value={payloadText} onChange={(event) => setPayloadText(event.target.value)} className="mt-3 h-44 w-full rounded-xl border border-white/10 bg-slate-950/70 p-3 font-mono text-[11px] text-slate-200 outline-none focus:border-cyan-400/50" />
      </details>
    </div>
  );
}

function CheckList({ title, checks, nextAction }: { title: string; checks: DiagnosticCheck[]; nextAction?: string }) {
  if (!checks.length) return null;
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <p className="text-[11px] font-black uppercase tracking-widest text-slate-400">{title}</p>
      <div className="mt-2 space-y-2">
        {checks.map((check) => (
          <div key={`${title}-${check.name}`} className="rounded-xl border border-white/5 bg-slate-950/30 px-3 py-2">
            <div className="flex items-center justify-between gap-2">
              <b className="text-xs text-slate-100">{check.name}</b>
              <StatusBadge status={check.status} />
            </div>
            <p className="mt-1 text-[11px] text-slate-400">{check.message}</p>
          </div>
        ))}
      </div>
      {nextAction && <p className="mt-2 text-[11px] leading-relaxed text-cyan-200">Próximo: {nextAction}</p>}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const classes = status === 'OK'
    ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-300'
    : status === 'FAIL'
      ? 'border-red-400/30 bg-red-400/10 text-red-300'
      : status === 'WARN'
        ? 'border-amber-400/30 bg-amber-400/10 text-amber-300'
        : 'border-slate-500/30 bg-slate-500/10 text-slate-300';
  return <span className={`rounded-full border px-2 py-0.5 text-[9px] font-black uppercase tracking-widest ${classes}`}>{status}</span>;
}
