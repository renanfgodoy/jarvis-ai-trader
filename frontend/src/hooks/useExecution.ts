import { useCallback, useEffect, useRef, useState } from 'react';
import { executeCoreDemo } from '../services/demoService';
import type {
  CoreDemoExecutionRequest,
  CoreDemoResponse,
  ExecutionHistoryItem,
  ExecutionStats,
  TradingResponse,
  LatencyClassification,
  PipelineStep
} from '../types/coreDemo';

const initialPipeline: PipelineStep[] = [
  { id: 'validation', label: 'Validation', status: 'WAITING' },
  { id: 'identity', label: 'Identity', status: 'WAITING' },
  { id: 'prompt', label: 'Prompt', status: 'WAITING' },
  { id: 'provider', label: 'Provider', status: 'WAITING' },
  { id: 'response', label: 'Response', status: 'WAITING' }
];

function progressPipeline(index: number, failed = false): PipelineStep[] {
  return initialPipeline.map((step, currentIndex) => {
    if (failed && currentIndex === index) return { ...step, status: 'ERROR' };
    if (currentIndex < index) return { ...step, status: 'SUCCESS' };
    if (currentIndex === index) return { ...step, status: 'RUNNING' };
    return { ...step };
  });
}

function completePipeline(): PipelineStep[] {
  return initialPipeline.map((step) => ({ ...step, status: 'SUCCESS' }));
}

function isTradingResponse(response: CoreDemoResponse): response is TradingResponse {
  return 'execution' in response && 'decision' in response;
}

function latencyOf(response: CoreDemoResponse): number {
  return isTradingResponse(response) ? response.execution.latency : response.latency;
}

function statusOf(response: CoreDemoResponse) {
  return isTradingResponse(response) ? response.status : response.status;
}

function classifyLatency(latency: number | null): LatencyClassification | 'Aguardando' {
  if (latency === null) return 'Aguardando';
  if (latency < 0.05) return 'Excelente';
  if (latency < 0.15) return 'Boa';
  if (latency < 0.5) return 'Moderada';
  return 'Lenta';
}

function buildHistoryItem(request: CoreDemoExecutionRequest, response: CoreDemoResponse): ExecutionHistoryItem {
  const executionLatency = latencyOf(response);

  return {
    id: isTradingResponse(response) ? response.execution.execution.request_id : response.request_id,
    time: new Date().toISOString(),
    market: request.market ?? 'Core',
    symbol: request.symbol ?? request.module,
    strategy: request.strategy ?? 'Core Demo',
    decision: isTradingResponse(response) ? response.decision : 'SUCCESS',
    confidence: isTradingResponse(response) ? response.confidence : null,
    status: statusOf(response),
    latency: executionLatency
  };
}

function buildStats(history: ExecutionHistoryItem[]): ExecutionStats {
  const averageLatency = history.length
    ? history.reduce((total, item) => total + item.latency, 0) / history.length
    : null;

  return {
    count: history.length,
    averageLatency,
    lastExecutionAt: history[0]?.time ?? null,
    latencyClassification: classifyLatency(averageLatency)
  };
}

export function useExecution() {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<CoreDemoResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pipeline, setPipeline] = useState<PipelineStep[]>(initialPipeline);
  const [history, setHistory] = useState<ExecutionHistoryItem[]>([]);
  const abortRef = useRef<AbortController | null>(null);
  const activeRequestRef = useRef<string | null>(null);
  const timersRef = useRef<number[]>([]);

  const clearTimers = useCallback(() => {
    timersRef.current.forEach((timer) => window.clearTimeout(timer));
    timersRef.current = [];
  }, []);

  useEffect(() => () => {
    clearTimers();
    abortRef.current?.abort();
  }, [clearTimers]);

  const reset = useCallback(() => {
    clearTimers();
    abortRef.current?.abort();
    activeRequestRef.current = null;
    setLoading(false);
    setResponse(null);
    setError(null);
    setPipeline(initialPipeline);
  }, [clearTimers]);

  const execute = useCallback(async (request: CoreDemoExecutionRequest) => {
    if (loading) return;
    clearTimers();
    const controller = new AbortController();
    const localRequestId = crypto.randomUUID();
    abortRef.current = controller;
    activeRequestRef.current = localRequestId;
    setLoading(true);
    setResponse(null);
    setError(null);
    setPipeline(progressPipeline(0));

    initialPipeline.slice(1).forEach((_, index) => {
      timersRef.current.push(window.setTimeout(() => {
        if (activeRequestRef.current === localRequestId) {
          setPipeline(progressPipeline(index + 1));
        }
      }, 220 * (index + 1)));
    });

    try {
      const nextResponse = await executeCoreDemo(request, controller.signal);
      if (activeRequestRef.current !== localRequestId) return;
      setResponse(nextResponse);
      setPipeline(completePipeline());
      setHistory((current) => [buildHistoryItem(request, nextResponse), ...current].slice(0, 5));
    } catch (caught) {
      if (controller.signal.aborted) return;
      const message = caught instanceof Error ? caught.message : 'Falha ao executar a Friday Core Demo.';
      setError(message);
      setPipeline((current) => {
        const runningIndex = Math.max(0, current.findIndex((step) => step.status === 'RUNNING'));
        return progressPipeline(runningIndex, true);
      });
    } finally {
      if (activeRequestRef.current === localRequestId) {
        setLoading(false);
      }
    }
  }, [clearTimers, loading]);

  return {
    loading,
    response,
    error,
    pipeline,
    history,
    stats: buildStats(history),
    execute,
    reset
  };
}
