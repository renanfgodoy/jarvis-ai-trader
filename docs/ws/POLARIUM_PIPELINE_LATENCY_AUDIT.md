# Polarium Pipeline Latency Audit

Sprint: V4.9 — Polarium Pipeline Latency Audit

Este documento registra somente instrumentação sanitizada. Nenhum token, cookie, Authorization, bearer, SSID, header privado, HAR bruto ou payload de autenticação deve ser registrado.

## Objetivo

Medir onde a Friday perde tempo entre o recebimento de `candle-generated` e o desenho da vela.

## Timeline Instrumentada

| Marco | Local | Implementação |
| --- | --- | --- |
| T0 `event_received` | Backend | `AuthorizedBrowserBridgeRuntime.ingest()` |
| T1 `parser_finished` | Backend | fim de `adapt_browser_bridge_payload()` |
| T2 `runtime_received` | Backend | imediatamente antes de `MarketPipeline.process()` |
| T3 `candle_store_updated` | Backend | retorno de `MarketPipeline.process()` |
| T4 `response_ready` | Backend | resposta sanitizada pronta |
| T5 `frontend_received` | Frontend | resposta Polarium Chart API ou evento SSE recebido |
| T6 `merge_finished` | Frontend | `reconcileRealCandleSeries()` / `mergeIqOptionCandles()` |
| T7 `series.update()` | Frontend | `RealCandleChart` incremental update |
| T8 `requestAnimationFrame` | Frontend | RAF que aplica evento push |
| T9 `frame_drawn` | Frontend | próximo RAF depois do update da série |

## Como Ler as Métricas

- Backend: `GET /api/v1/polarium/browser-bridge/status` retorna `latency_audit` e `last_trace.latency_*`.
- Frontend: DevTools pode ler `window.__FRIDAY_LATENCY_AUDIT__`.
- Cada amostra contém apenas nomes de etapa, contadores, ids internos, símbolo quando já sanitizado e durações em milissegundos.

## Gargalos Observados por Código

Sem uma sessão Polarium ao vivo durante esta Sprint, os tempos médios, p50 e p95 reais ficam dependentes da próxima validação visual. A instrumentação agora coleta esses valores em runtime.

| Ranking | Trecho | Espera/Buferização | Média | p50 | p95 | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Frontend Polarium polling | `useRealCandles` usa `SYNC_INTERVAL_MS = 1500` | pendente | pendente | pendente | Gargalo provável |
| 2 | Fallback IQ realtime polling | `IQ_REALTIME_POLL_INTERVAL_MS = 1000` | pendente | pendente | pendente | Não é Polarium, mas existe no workspace |
| 3 | Reconciliação periódica IQ | `IQ_POLL_INTERVAL_MS = 5000` | pendente | pendente | pendente | Backup/consistência |
| 4 | Health check SSE | `IQ_PUSH_HEALTH_CHECK_INTERVAL_MS = 2000` | pendente | pendente | pendente | Só detecção de falha |
| 5 | Timeout heartbeat | `IQ_PUSH_HEARTBEAT_TIMEOUT_MS = 15000` | pendente | pendente | pendente | Só fallback |
| 6 | Asset retry | `1000/2000/4000ms` | pendente | pendente | pendente | Fora do candle render |
| 7 | Fetch Chart API Polarium | `/market/chart` após status e series | pendente | pendente | pendente | Sequencial |
| 8 | Merge frontend | `reconcileRealCandleSeries` / `mergeCandlesByTime` | instrumentado | instrumentado | instrumentado | Medido em T6 |
| 9 | Lightweight Charts update | `series.update()` ou `setData()` | instrumentado | instrumentado | instrumentado | Medido em T7 |
| 10 | RAF/render | `requestAnimationFrame` + commit | instrumentado | instrumentado | instrumentado | Medido em T8/T9 |

## Auditoria de Buffers e Filas

- Browser Bridge: não cria fila persistente; processa a mensagem recebida e atualiza `last_trace`.
- Payload Adapter: conversão síncrona; sem debounce.
- MarketPipeline: chamada síncrona a partir do runtime autorizado.
- CandleStore: escrita em memória compartilhada; persistência SQLite ocorre via observador de escrita.
- `useRealCandles`: polling de 1500ms e bloqueio de requisição concorrente com `isRequestInFlight`.
- `MarketChart` IQ: SSE com coalescing por RAF; se múltiplos eventos chegam antes do frame, `pendingPushEvent` mantém o último.
- `RealCandleChart`: preserva `createChart()`; usa `series.update()` para append/update e `setData()` somente em reset.

## Comparação Conceitual com HARs

As evidências sanitizadas em `POLARIUM_HAR_CANDLE_EVIDENCE_SANITIZED.md` e `POLARIUM_DIRECTED_CORRELATION.md` confirmam que a Polarium recebe `candle-generated` via WebSocket com `active_id`, `size`, `from`, `to`, `open`, `close`, `min`, `max` e `volume`.

| Pipeline | Caminho observado | Latência estrutural |
| --- | --- | --- |
| Polarium nativa | WebSocket da página → runtime interno → chart | caminho direto, sem polling HTTP visível no HAR |
| Friday Polarium | Browser Bridge → backend local → adapter → pipeline → store → Chart API polling → React → chart | inclui ponte local e polling de 1500ms no hook Polarium |
| Friday IQ atual | Worker/provider → backend SSE → RAF → merge → chart | push unidirecional com fallback polling |
| TradeAutoPilot | Não há evidência sanitizada no repositório atual suficiente para medir | comparação limitada a arquitetura, não a tempos |

## Leitura Esperada no Runtime

Backend:

```json
{
  "latency_audit": {
    "sample_count": 1,
    "latest": {
      "event_name": "candle-generated",
      "pipeline_processed": true,
      "backend_total_ms": 0.0
    },
    "segments": {
      "event_to_parser_ms": { "mean_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0 }
    }
  }
}
```

Frontend:

```js
window.__FRIDAY_LATENCY_AUDIT__
```

## Conclusão Técnica

A maior perda estrutural provável no caminho Polarium não está no parser nem no CandleStore, mas no modelo de leitura frontend baseado em polling de `/market/chart` a cada 1500ms. A Sprint V4.9 não altera esse comportamento; apenas deixa a medição pronta para confirmar média, p50 e p95 com sessão real.

## Próxima Validação

1. Abrir a Polarium com Browser Bridge ativo.
2. Confirmar `last_event_name = candle-generated`.
3. Consultar `/api/v1/polarium/browser-bridge/status`.
4. Abrir o console da Friday e inspecionar `window.__FRIDAY_LATENCY_AUDIT__`.
5. Coletar pelo menos 30 eventos para calcular p50/p95 confiáveis.
