import { useCallback, useState } from 'react';

export type ConnectionAttemptResult = 'success' | 'error' | 'info';

export type ConnectionAttempt = {
  id: string;
  time: string;
  action: string;
  step: string;
  result: ConnectionAttemptResult;
  message: string;
};

const sensitivePatterns = [
  /bearer\s+[a-z0-9._-]+/gi,
  /authorization[:=]\s*[^,\s}]+/gi,
  /refresh[_-]?token[:=]\s*[^,\s}]+/gi,
  /access[_-]?token[:=]\s*[^,\s}]+/gi,
  /ssid[:=]\s*[^,\s}]+/gi,
  /cookie[:=]\s*[^,\s}]+/gi,
  /password[:=]\s*[^,\s}]+/gi,
  /token[:=]\s*[^,\s}]+/gi
];

export function sanitizeConnectionMessage(value: unknown, fallback = 'Ação processada.'): string {
  const raw = typeof value === 'string'
    ? value
    : value instanceof Error
      ? value.message
      : typeof value === 'object' && value !== null && 'message' in value
        ? String((value as { message?: unknown }).message ?? fallback)
        : fallback;

  return sensitivePatterns
    .reduce((message, pattern) => message.replace(pattern, '[redigido]'), raw)
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 180) || fallback;
}

export function useConnectionHistory() {
  const [attempts, setAttempts] = useState<ConnectionAttempt[]>([]);

  const addAttempt = useCallback((attempt: Omit<ConnectionAttempt, 'id' | 'time' | 'message'> & { message?: unknown }) => {
    const nextAttempt: ConnectionAttempt = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      action: attempt.action,
      step: attempt.step,
      result: attempt.result,
      message: sanitizeConnectionMessage(attempt.message)
    };

    setAttempts((current) => [nextAttempt, ...current].slice(0, 12));
  }, []);

  const clearAttempts = useCallback(() => setAttempts([]), []);

  return { attempts, addAttempt, clearAttempts };
}
