import type { VisionAnalysisRequestPayload, VisionAnalysisResult, VisionHistoryItem, VisionStatus } from '../types/vision';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1';

export class VisionApiError extends Error {
  errorCode: string;
  status: number;

  constructor(message: string, errorCode: string, status: number) {
    super(message);
    this.name = 'VisionApiError';
    this.errorCode = errorCode;
    this.status = status;
  }
}

export async function getVisionStatus(signal?: AbortSignal): Promise<VisionStatus> {
  const response = await fetch(`${API_BASE_URL}/vision/status`, { signal });
  return parseResponse<VisionStatus>(response);
}

export async function analyzeVisionScreenshot(payload: VisionAnalysisRequestPayload): Promise<VisionAnalysisResult> {
  const form = new FormData();
  form.append('image', payload.image);
  if (payload.asset?.trim()) {
    form.append('asset', payload.asset.trim());
  }
  form.append('timeframe', payload.timeframe);
  form.append('expiration', payload.expiration);
  form.append('strategy_mode', payload.strategy_mode);
  if (payload.user_notes?.trim()) {
    form.append('user_notes', payload.user_notes.trim());
  }

  const response = await fetch(`${API_BASE_URL}/vision/analyze`, {
    method: 'POST',
    body: form,
    signal: payload.signal,
    headers: {
      'X-Request-ID': payload.requestId
    }
  });
  return parseResponse<VisionAnalysisResult>(response);
}

export async function getVisionHistory(signal?: AbortSignal): Promise<VisionHistoryItem[]> {
  const response = await fetch(`${API_BASE_URL}/vision/history`, { signal });
  const data = await parseResponse<{ items: VisionHistoryItem[] }>(response);
  return data.items;
}

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errorCode = data?.detail?.error_code ?? data?.error_code ?? 'VISION_REQUEST_FAILED';
    throw new VisionApiError(errorCode, errorCode, response.status);
  }
  return data as T;
}
