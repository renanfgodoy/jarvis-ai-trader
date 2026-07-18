import { AlertCircle, BrainCircuit, Loader2, ShieldCheck } from 'lucide-react';
import type { ReactNode } from 'react';
import { useEffect, useMemo, useRef, useState } from 'react';
import PageContainer from '../components/PageContainer';
import PageTitle from '../components/PageTitle';
import VisionAnalysisPanel from '../components/vision/VisionAnalysisPanel';
import VisionUploader from '../components/vision/VisionUploader';
import { VisionApiError, analyzeVisionScreenshot, getVisionStatus } from '../services/visionApi';
import type { VisionAnalysisResult, VisionStrategyMode, VisionUiState } from '../types/vision';

const TIMEFRAMES = ['M1', 'M5', 'M15'] as const;
const EXPIRATIONS = ['1 minuto', '5 minutos', '15 minutos'] as const;
const STRATEGY_MODES: Array<{ value: VisionStrategyMode; label: string }> = [
  { value: 'COMPLETE', label: 'Completa' },
  { value: 'PRICE_ACTION', label: 'Price Action' },
  { value: 'SUPPORT_RESISTANCE', label: 'Suporte e resistência' },
  { value: 'TREND', label: 'Tendência' }
];

export default function Vision() {
  const [file, setFile] = useState<File | null>(null);
  const [asset, setAsset] = useState('');
  const [timeframe, setTimeframe] = useState<(typeof TIMEFRAMES)[number]>('M1');
  const [expiration, setExpiration] = useState<(typeof EXPIRATIONS)[number]>('1 minuto');
  const [strategyMode, setStrategyMode] = useState<VisionStrategyMode>('COMPLETE');
  const [userNotes, setUserNotes] = useState('');
  const [uiState, setUiState] = useState<VisionUiState>('IDLE');
  const [result, setResult] = useState<VisionAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [statusLabel, setStatusLabel] = useState('Verificando Friday Vision');
  const [cooldownUntil, setCooldownUntil] = useState(0);
  const requestRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    getVisionStatus(controller.signal)
      .then((status) => setStatusLabel(status.analysis_available ? `Provider ${status.provider}` : 'Análise indisponível'))
      .catch(() => setStatusLabel('Status indisponível'));
    return () => {
      controller.abort();
      abortRef.current?.abort();
    };
  }, []);

  useEffect(() => {
    if (!file && uiState !== 'ANALYZING') {
      setUiState('IDLE');
      setResult(null);
      setError(null);
    } else if (file && uiState === 'IDLE') {
      setUiState('IMAGE_READY');
    }
  }, [file, uiState]);

  const cooldownActive = Date.now() < cooldownUntil;
  const formValid = Boolean(file && timeframe && expiration && strategyMode);
  const analyzing = uiState === 'ANALYZING' || uiState === 'VALIDATING';
  const canAnalyze = formValid && !analyzing && !cooldownActive;

  const helper = useMemo(() => {
    if (!file) return 'Envie um print do gráfico para liberar a análise.';
    if (cooldownActive) return 'Aguarde alguns segundos antes de uma nova análise.';
    return 'A análise usa confiança visual, não probabilidade de lucro.';
  }, [cooldownActive, file]);

  async function submitAnalysis() {
    if (!file || !canAnalyze) return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const requestId = crypto.randomUUID();
    requestRef.current = requestId;
    setUiState('ANALYZING');
    setError(null);
    setResult(null);
    try {
      const response = await analyzeVisionScreenshot({
        image: file,
        asset,
        timeframe,
        expiration,
        strategy_mode: strategyMode,
        user_notes: userNotes,
        requestId,
        signal: controller.signal
      });
      if (requestRef.current !== requestId) return;
      setResult(response);
      setUiState('SUCCESS');
      setCooldownUntil(Date.now() + 3000);
    } catch (caught) {
      if (controller.signal.aborted) return;
      const message =
        caught instanceof VisionApiError ? translateVisionError(caught.errorCode) : 'Não foi possível analisar o print agora.';
      setError(message);
      setUiState('ERROR');
      setCooldownUntil(Date.now() + 3000);
    }
  }

  return (
    <PageContainer className="p-4 lg:p-6">
      <PageTitle eyebrow="Friday Vision" title="Análise visual de gráfico">
        <div className="flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-2 text-xs font-black uppercase tracking-widest text-cyan-100">
          <BrainCircuit size={15} />
          {statusLabel}
        </div>
      </PageTitle>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.65fr)]">
        <div className="space-y-4">
          <VisionUploader file={file} onFileChange={setFile} disabled={analyzing} />
          {result && <VisionAnalysisPanel result={result} />}
          {error && (
            <div className="flex gap-3 rounded-xl border border-red-300/20 bg-red-500/10 p-4 text-sm font-semibold text-red-100">
              <AlertCircle size={18} className="shrink-0" />
              {error}
            </div>
          )}
        </div>

        <aside className="space-y-4 rounded-xl border border-white/10 bg-white/[0.035] p-4">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.18em] text-cyan-200">Contexto informado</p>
            <p className="mt-2 text-sm font-semibold leading-6 text-slate-300">
              Preencha apenas o que você sabe. A Friday não deve inventar ativo, timeframe ou informações que não apareçam no print.
            </p>
          </div>

          <Field label="Ativo">
            <input
              value={asset}
              onChange={(event) => setAsset(event.target.value)}
              placeholder="EUR/USD OTC"
              className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none"
            />
          </Field>

          <Field label="Timeframe">
            <select
              value={timeframe}
              onChange={(event) => setTimeframe(event.target.value as typeof timeframe)}
              className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none"
            >
              {TIMEFRAMES.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </Field>

          <Field label="Expiração">
            <select
              value={expiration}
              onChange={(event) => setExpiration(event.target.value as typeof expiration)}
              className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none"
            >
              {EXPIRATIONS.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </Field>

          <Field label="Modo de análise">
            <select
              value={strategyMode}
              onChange={(event) => setStrategyMode(event.target.value as VisionStrategyMode)}
              className="h-11 w-full rounded-lg border border-white/10 bg-black/25 px-3 text-sm font-semibold text-white outline-none"
            >
              {STRATEGY_MODES.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Observações">
            <textarea
              value={userNotes}
              onChange={(event) => setUserNotes(event.target.value)}
              rows={4}
              placeholder="Ex.: print logo após rejeição em resistência."
              className="w-full resize-none rounded-lg border border-white/10 bg-black/25 p-3 text-sm font-semibold text-white outline-none"
            />
          </Field>

          <button
            type="button"
            disabled={!canAnalyze}
            onClick={submitAnalysis}
            className="flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-cyan-300 px-4 text-sm font-black uppercase tracking-widest text-slate-950 disabled:cursor-not-allowed disabled:bg-white/10 disabled:text-slate-500"
          >
            {analyzing && <Loader2 size={16} className="animate-spin" />}
            {analyzing ? 'FRIDAY ESTÁ ANALISANDO...' : 'ANALISAR GRÁFICO'}
          </button>
          <p className="text-xs font-semibold leading-5 text-slate-400">{helper}</p>

          <div className="rounded-lg border border-amber-300/20 bg-amber-300/10 p-3">
            <p className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-amber-100">
              <ShieldCheck size={15} />
              Aviso de risco
            </p>
            <p className="mt-2 text-xs font-semibold leading-5 text-amber-100/90">
              A Friday realiza uma leitura visual do print enviado. A análise não garante resultado e não substitui sua gestão de risco.
            </p>
          </div>
        </aside>
      </div>
    </PageContainer>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block space-y-2">
      <span className="text-xs font-black uppercase tracking-widest text-slate-400">{label}</span>
      {children}
    </label>
  );
}

function translateVisionError(errorCode: string) {
  const messages: Record<string, string> = {
    VISION_PROVIDER_NOT_CONFIGURED: 'Configure a chave do provedor no backend para executar a validação real.',
    VISION_IMAGE_TOO_LARGE: 'A imagem ultrapassa o limite configurado.',
    VISION_IMAGE_TOO_SMALL: 'A imagem é pequena demais para análise visual confiável.',
    VISION_IMAGE_UNSUPPORTED: 'Formato de imagem não suportado. Use PNG, JPG ou WEBP.',
    VISION_IMAGE_CORRUPTED: 'Não foi possível decodificar a imagem.',
    VISION_PROVIDER_RATE_LIMIT: 'Limite temporário de análises atingido.',
    VISION_COOLDOWN_ACTIVE: 'Aguarde alguns segundos antes de enviar outra análise.',
    VISION_INVALID_PROVIDER_RESPONSE: 'O provedor retornou uma estrutura inválida.'
  };
  return messages[errorCode] ?? `Falha na análise: ${errorCode}`;
}
