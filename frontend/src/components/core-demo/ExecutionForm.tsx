import { Loader2, Play } from 'lucide-react';
import type { FormEvent } from 'react';
import { useState } from 'react';
import type { CoreDemoExecutionRequest } from '../../types/coreDemo';

const identities = [
  { value: 'jarvis.default', label: 'J.A.R.V.I.S Default' },
  { value: 'jarvis.trading', label: 'J.A.R.V.I.S Trading' },
  { value: 'jarvis.marketing', label: 'J.A.R.V.I.S Marketing' },
  { value: 'jarvis.finance', label: 'J.A.R.V.I.S Finance' }
];

const languages = [
  { value: 'pt-BR', label: 'Português' },
  { value: 'en-US', label: 'English' }
];

export default function ExecutionForm({
  loading,
  onExecute
}: {
  loading: boolean;
  onExecute: (request: CoreDemoExecutionRequest) => void;
}) {
  const [identity, setIdentity] = useState('jarvis.default');
  const [language, setLanguage] = useState('pt-BR');
  const [module, setModule] = useState('trading');
  const [market, setMarket] = useState<'OTC' | 'Forex' | 'Crypto'>('OTC');
  const [symbol, setSymbol] = useState('EURUSD');
  const [timeframe, setTimeframe] = useState<'M1' | 'M5' | 'M15' | 'H1'>('M1');
  const [strategy, setStrategy] = useState<'Trend' | 'Price Action' | 'Support Resistance' | 'SMC' | 'ICT'>('Trend');
  const [message, setMessage] = useState('Explique como a Friday AI Platform coordena uma execução pelo Core.');

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (loading || !message.trim()) return;
    onExecute({
      module,
      identity,
      provider: 'mock',
      language,
      message: message.trim(),
      market,
      symbol,
      timeframe,
      strategy,
      metadata: {
        demo_module: module === 'trading' ? 'trading_module' : 'core_demo',
        ui: 'developer_console'
      }
    });
  }

  return (
    <form onSubmit={submit} className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
      <div className="grid gap-3 md:grid-cols-4">
        <label className="space-y-2">
          <span className="text-xs font-black uppercase tracking-widest text-slate-400">Module</span>
          <select value={module} onChange={(event) => setModule(event.target.value)} className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none">
            <option value="trading">Trading</option>
            <option value="documents">Documents</option>
          </select>
        </label>
        <label className="space-y-2">
          <span className="text-xs font-black uppercase tracking-widest text-slate-400">Identity</span>
          <select value={identity} onChange={(event) => setIdentity(event.target.value)} className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none">
            {identities.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        </label>
        <label className="space-y-2">
          <span className="text-xs font-black uppercase tracking-widest text-slate-400">Provider</span>
          <select value="mock" disabled className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-slate-300 outline-none">
            <option value="mock">Mock Provider</option>
          </select>
        </label>
        <label className="space-y-2">
          <span className="text-xs font-black uppercase tracking-widest text-slate-400">Language</span>
          <select value={language} onChange={(event) => setLanguage(event.target.value)} className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none">
            {languages.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        </label>
      </div>

      {module === 'trading' && (
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          <label className="space-y-2">
            <span className="text-xs font-black uppercase tracking-widest text-slate-400">Mercado</span>
            <select value={market} onChange={(event) => setMarket(event.target.value as typeof market)} className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none">
              <option value="OTC">OTC</option>
              <option value="Forex">Forex</option>
              <option value="Crypto">Crypto</option>
            </select>
          </label>
          <label className="space-y-2">
            <span className="text-xs font-black uppercase tracking-widest text-slate-400">Ativo</span>
            <input value={symbol} onChange={(event) => setSymbol(event.target.value)} className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none" />
          </label>
          <label className="space-y-2">
            <span className="text-xs font-black uppercase tracking-widest text-slate-400">Timeframe</span>
            <select value={timeframe} onChange={(event) => setTimeframe(event.target.value as typeof timeframe)} className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none">
              <option value="M1">M1</option>
              <option value="M5">M5</option>
              <option value="M15">M15</option>
              <option value="H1">H1</option>
            </select>
          </label>
          <label className="space-y-2">
            <span className="text-xs font-black uppercase tracking-widest text-slate-400">Estratégia</span>
            <select value={strategy} onChange={(event) => setStrategy(event.target.value as typeof strategy)} className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none">
              <option value="Trend">Trend</option>
              <option value="Price Action">Price Action</option>
              <option value="Support Resistance">Support Resistance</option>
              <option value="SMC">SMC</option>
              <option value="ICT">ICT</option>
            </select>
          </label>
        </div>
      )}

      <label className="mt-4 block space-y-2">
        <span className="text-xs font-black uppercase tracking-widest text-slate-400">Message</span>
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={6}
          disabled={loading}
          className="w-full resize-none rounded-lg border border-white/10 bg-black/25 p-3 text-sm font-semibold leading-6 text-white outline-none disabled:opacity-60"
        />
      </label>

      <div className="mt-4 flex items-center justify-between gap-3">
        <p className="text-xs font-semibold text-slate-400">O formulário chama apenas o DemoService. Nenhum componente acessa engines diretamente.</p>
        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="inline-flex h-11 shrink-0 items-center gap-2 rounded-lg bg-cyan-300 px-4 text-sm font-black uppercase tracking-widest text-slate-950 disabled:cursor-not-allowed disabled:bg-white/10 disabled:text-slate-500"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          {loading ? 'Executando' : 'Execute Friday'}
        </button>
      </div>
    </form>
  );
}
