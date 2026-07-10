import { useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { FileSearch, ShieldCheck, Search, UploadCloud } from 'lucide-react';
import { inspectPolariumHar, probePolariumClientStorage } from '../services/api';
import type { InspectorFinding } from '../types/api';

export default function PolariumSessionInspectorPanel() {
  const [harText, setHarText] = useState('');
  const harInspection = useMutation({
    mutationFn: () => {
      const parsed = JSON.parse(harText);
      return inspectPolariumHar(parsed);
    }
  });
  const storageProbe = useMutation({
    mutationFn: () => probePolariumClientStorage({
      local_storage_keys: Object.keys(window.localStorage ?? {}),
      session_storage_keys: Object.keys(window.sessionStorage ?? {}),
      cookie_names: document.cookie ? document.cookie.split(';').map((item) => item.trim().split('=')[0]).filter(Boolean) : [],
      origin: window.location.origin
    })
  });

  const summary = useMemo(() => {
    if (!harInspection.data) return null;
    return [
      ['Entries', harInspection.data.total_entries],
      ['Authorize', harInspection.data.oauth_authorize_found ? 'OK' : '—'],
      ['Token', harInspection.data.oauth_token_found ? 'OK' : '—'],
      ['WebSocket', harInspection.data.websocket_found ? 'OK' : '—'],
      ['Bearer', harInspection.data.bearer_found ? 'OK' : '—'],
      ['Cookie/Auth', harInspection.data.cookie_auth_found ? 'OK' : '—']
    ];
  }, [harInspection.data]);

  return (
    <div className="panel p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="eyebrow">Session Inspector</p>
          <h3 className="mt-1 text-sm font-black text-white">V0.23 • HAR / Storage Analyzer</h3>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-500">Analisa HAR e armazenamento do origin atual. Mascara tokens e não reutiliza credenciais.</p>
        </div>
        <StatusBadge status={harInspection.data?.status ?? storageProbe.data?.status ?? 'SKIPPED'} />
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2">
        <button onClick={() => storageProbe.mutate()} disabled={storageProbe.isPending} className="toolbar-btn justify-center text-cyan-100"><ShieldCheck size={14} /> Storage</button>
        <button onClick={() => harInspection.mutate()} disabled={!harText.trim() || harInspection.isPending} className="toolbar-btn justify-center text-cyan-100"><FileSearch size={14} /> Inspect HAR</button>
      </div>

      {summary && (
        <div className="mt-3 grid grid-cols-2 gap-2">
          {summary.map(([label, value]) => (
            <div key={String(label)} className="rounded-xl border border-white/10 bg-slate-950/30 p-2">
              <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">{label}</p>
              <b className="text-xs text-cyan-200">{String(value)}</b>
            </div>
          ))}
        </div>
      )}

      <details className="mt-3 rounded-2xl border border-white/10 bg-slate-950/40 p-3">
        <summary className="cursor-pointer text-[11px] font-black uppercase tracking-widest text-slate-400"><UploadCloud className="mr-1 inline" size={13} /> Colar HAR com conteúdo</summary>
        <p className="mt-2 text-[11px] leading-relaxed text-amber-200">HAR pode conter tokens/cookies. Esta tela envia para seu backend local e mascara a saída, mas salve/compartilhe com cuidado.</p>
        <textarea value={harText} onChange={(event) => setHarText(event.target.value)} placeholder="Cole aqui o conteúdo JSON do arquivo .har" className="mt-3 h-44 w-full rounded-xl border border-white/10 bg-slate-950/70 p-3 font-mono text-[10px] text-slate-200 outline-none focus:border-cyan-400/50" />
      </details>

      <div className="mt-3 space-y-2">
        {storageProbe.data && <FindingList title="Client Storage Probe" findings={storageProbe.data.findings} nextAction={storageProbe.data.next_action} />}
        {harInspection.data && <FindingList title="HAR Inspection" findings={harInspection.data.findings} nextAction={harInspection.data.next_action} />}
        {(harInspection.error || storageProbe.error) && <div className="rounded-2xl border border-red-400/20 bg-red-400/10 p-3 text-xs text-red-100">Erro no inspector. Confira se o HAR é JSON válido e mande print do Console.</div>}
      </div>
    </div>
  );
}

function FindingList({ title, findings, nextAction }: { title: string; findings: InspectorFinding[]; nextAction?: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <p className="text-[11px] font-black uppercase tracking-widest text-slate-400"><Search className="mr-1 inline" size={13} /> {title}</p>
      <div className="mt-2 space-y-2">
        {findings.map((finding) => (
          <details key={`${title}-${finding.name}`} className="rounded-xl border border-white/5 bg-slate-950/30 px-3 py-2">
            <summary className="cursor-pointer list-none">
              <div className="flex items-center justify-between gap-2">
                <b className="text-xs text-slate-100">{finding.name}</b>
                <StatusBadge status={finding.status} />
              </div>
              <p className="mt-1 text-[11px] text-slate-400">{finding.message}</p>
            </summary>
            <pre className="mt-2 max-h-56 overflow-auto rounded-lg border border-white/5 bg-black/30 p-2 text-[10px] text-slate-300">{JSON.stringify(finding.detail, null, 2)}</pre>
          </details>
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
