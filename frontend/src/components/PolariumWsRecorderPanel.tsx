import { useMemo, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { ClipboardList, Copy, Radio, SearchCode } from 'lucide-react';
import { analyzePolariumWsFrames, getPolariumWsRecorderSnippet } from '../services/api';
import type { WsMessageSummary, WsRecorderFinding } from '../types/api';

export default function PolariumWsRecorderPanel() {
  const [framesText, setFramesText] = useState('');
  const snippet = useQuery({ queryKey: ['polarium-ws-recorder-snippet'], queryFn: getPolariumWsRecorderSnippet, staleTime: Infinity });
  const analyzer = useMutation({ mutationFn: () => analyzePolariumWsFrames(framesText) });

  const summary = useMemo(() => {
    const data = analyzer.data;
    if (!data) return null;
    return [
      ['Linhas', data.total_lines],
      ['JSON', data.parsed_messages],
      ['Auth', data.auth_candidates.length],
      ['Saldo', data.balance_candidates.length],
      ['Candles', data.candle_candidates.length],
      ['Price', data.price_candidates.length]
    ];
  }, [analyzer.data]);

  async function copySnippet() {
    if (!snippet.data?.snippet) return;
    await navigator.clipboard.writeText(snippet.data.snippet);
  }

  return (
    <div className="panel p-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="eyebrow">WS Session Recorder</p>
          <h3 className="mt-1 text-sm font-black text-white">V0.24 • WebSocket Message Analyzer</h3>
          <p className="mt-1 text-[11px] leading-relaxed text-slate-500">Cole frames do DevTools para mapear auth, saldo, candles e preços. Não opera e não reutiliza tokens.</p>
        </div>
        <StatusBadge status={analyzer.data?.status ?? 'SKIPPED'} />
      </div>

      <details className="mt-3 rounded-2xl border border-amber-400/15 bg-amber-400/5 p-3">
        <summary className="cursor-pointer text-[11px] font-black uppercase tracking-widest text-amber-200"><Radio className="mr-1 inline" size={13} /> Como capturar os frames</summary>
        <ol className="mt-2 list-decimal space-y-1 pl-4 text-[11px] leading-relaxed text-slate-300">
          <li>Abra TradeAutoPilot/Polarium com DevTools em <b>Network</b>.</li>
          <li>Filtre <b>Socket/WS</b> e clique no WebSocket status <b>101</b>.</li>
          <li>Abra <b>Messages</b> ou <b>Frames</b>.</li>
          <li>Copie as primeiras mensagens após conectar e cole abaixo.</li>
        </ol>
      </details>

      <div className="mt-3 grid grid-cols-2 gap-2">
        <button onClick={() => analyzer.mutate()} disabled={!framesText.trim() || analyzer.isPending} className="toolbar-btn justify-center text-cyan-100"><SearchCode size={14} /> Analyze Frames</button>
        <button onClick={copySnippet} disabled={!snippet.data?.snippet} className="toolbar-btn justify-center text-cyan-100"><Copy size={14} /> Copiar Snippet</button>
      </div>

      <textarea
        value={framesText}
        onChange={(event) => setFramesText(event.target.value)}
        placeholder={'Cole aqui linhas JSON copiadas do WebSocket Messages/Frames. Ex:\n{"name":"candle-generated","msg":{...}}\n{"name":"marginal-balance","msg":{...}}'}
        className="mt-3 h-40 w-full rounded-xl border border-white/10 bg-slate-950/70 p-3 font-mono text-[10px] text-slate-200 outline-none focus:border-cyan-400/50"
      />

      {summary && (
        <div className="mt-3 grid grid-cols-3 gap-2">
          {summary.map(([label, value]) => (
            <div key={String(label)} className="rounded-xl border border-white/10 bg-slate-950/30 p-2">
              <p className="text-[9px] font-black uppercase tracking-widest text-slate-500">{label}</p>
              <b className="text-xs text-cyan-200">{String(value)}</b>
            </div>
          ))}
        </div>
      )}

      {snippet.data && (
        <details className="mt-3 rounded-2xl border border-white/10 bg-slate-950/40 p-3">
          <summary className="cursor-pointer text-[11px] font-black uppercase tracking-widest text-slate-400"><ClipboardList className="mr-1 inline" size={13} /> Console snippet opcional</summary>
          <p className="mt-2 text-[11px] leading-relaxed text-amber-200">{snippet.data.warning}</p>
          <pre className="mt-2 max-h-44 overflow-auto rounded-lg border border-white/5 bg-black/30 p-2 text-[10px] text-slate-300">{snippet.data.snippet}</pre>
        </details>
      )}

      <div className="mt-3 space-y-2">
        {analyzer.data && <FindingList findings={analyzer.data.findings} nextAction={analyzer.data.next_action} />}
        {analyzer.data && <CandidateList title="Primeiras mensagens" items={analyzer.data.first_messages} />}
        {analyzer.error && <div className="rounded-2xl border border-red-400/20 bg-red-400/10 p-3 text-xs text-red-100">Erro ao analisar frames. Confira se as linhas têm JSON válido.</div>}
      </div>
    </div>
  );
}

function FindingList({ findings, nextAction }: { findings: WsRecorderFinding[]; nextAction?: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <p className="text-[11px] font-black uppercase tracking-widest text-slate-400">Resultado WS</p>
      <div className="mt-2 space-y-2">
        {findings.map((finding) => (
          <details key={finding.name} className="rounded-xl border border-white/5 bg-slate-950/30 px-3 py-2">
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

function CandidateList({ title, items }: { title: string; items: WsMessageSummary[] }) {
  if (!items.length) return null;
  return (
    <details className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
      <summary className="cursor-pointer text-[11px] font-black uppercase tracking-widest text-slate-400">{title}</summary>
      <pre className="mt-2 max-h-64 overflow-auto rounded-lg border border-white/5 bg-black/30 p-2 text-[10px] text-slate-300">{JSON.stringify(items, null, 2)}</pre>
    </details>
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
