# Polarium Directed Candle Correlation

Sprint: V2.9 — Directed Candle Correlation

Fonte privada analisada: `.jarvis_cache/evidence/trade.polariumbroker.com.har`.

Este documento registra somente evidência sanitizada de dados de mercado. O HAR bruto, headers, cookies, tokens, URLs privadas, credenciais e dados de autenticação não foram reproduzidos.

## Sumário da análise

- Entradas HAR inspecionadas: 1
- Mensagens WebSocket analisadas: 3348
- Eventos WebSocket de mercado correlacionados: 808

## Eventos WebSocket

- `get-first-candles`: CONFIRMADO (3 ocorrência(s)).
- `first-candles`: CONFIRMADO (3 ocorrência(s)).
- `candle-generated`: CONFIRMADO (209 ocorrência(s)).
- `candles-generated`: CONFIRMADO (6 ocorrência(s)).
- `digital-option-client-price-generated`: CONFIRMADO (193 ocorrência(s)).
- `timeSync`: CONFIRMADO (214 ocorrência(s)).
- `subscribeMessage`: CONFIRMADO (127 ocorrência(s)).
- `unsubscribeMessage`: CONFIRMADO (53 ocorrência(s)).

## Correlação request → response

- `request_id=80`: CONFIRMADO `get-first-candles` → `first-candles` para `active_id=76`.
  Tamanhos retornados em `candles_by_size`: `1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000`.
- `request_id=158`: CONFIRMADO `get-first-candles` → `first-candles` para `active_id=2298`.
  Tamanhos retornados em `candles_by_size`: `1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000`.
- `request_id=161`: CONFIRMADO `get-first-candles` → `first-candles` para `active_id=2298`.
  Tamanhos retornados em `candles_by_size`: `1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000`.

## Ativo visual → active_id

- `EURUSD`: PARCIAL (46 ocorrência(s) textual(is)); ainda precisa vínculo direto com `active_id` no mesmo contrato sanitizado.
- `GBPUSD`: PARCIAL (46 ocorrência(s) textual(is)); ainda precisa vínculo direto com `active_id` no mesmo contrato sanitizado.
- `EUR/USD`: PARCIAL (5 ocorrência(s) textual(is)); ainda precisa vínculo direto com `active_id` no mesmo contrato sanitizado.
- `GBP/USD`: PARCIAL (5 ocorrência(s) textual(is)); ainda precisa vínculo direto com `active_id` no mesmo contrato sanitizado.

## Active IDs encontrados

- `active_id=76`: PARCIAL (208 ocorrência(s)); ID observado, símbolo visual não comprovado.
- `active_id=2298`: PARCIAL (19 ocorrência(s)); ID observado, símbolo visual não comprovado.

## Timeframe visual → size

- `size=60`: PARCIAL (114 ocorrência(s)); não há rótulo visual M1/M5/M15 comprovado no mesmo payload.
- `size=300`: PARCIAL (106 ocorrência(s)); não há rótulo visual M1/M5/M15 comprovado no mesmo payload.
- `size=900`: PARCIAL (3 ocorrência(s)); não há rótulo visual M1/M5/M15 comprovado no mesmo payload.

## Size → candle real

- `active_id=76`, `size=60`: CONFIRMADO em `candle-generated`.

```json
{
  "event": "candle-generated",
  "active_id": 76,
  "size": 60,
  "from": 1783721940,
  "to": 1783722000,
  "open": 1.162275,
  "close": 1.162145,
  "min": 1.162145,
  "max": 1.162395,
  "volume": 0
}
```

- `active_id=76`, `size=300`: CONFIRMADO em `candle-generated`.

```json
{
  "event": "candle-generated",
  "active_id": 76,
  "size": 300,
  "from": 1783722000,
  "to": 1783722300,
  "open": 1.162965,
  "close": 1.162765,
  "min": 1.162715,
  "max": 1.163335,
  "volume": 0
}
```

- `active_id=76`, `size=900`: CONFIRMADO via `first-candles` request/response.

## Subscription

- `subscribeMessage:portfolio.position-changed`: PARCIAL (23 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:portfolio.order-changed`: PARCIAL (19 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `unsubscribeMessage:portfolio.position-changed`: PARCIAL (14 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `unsubscribeMessage:portfolio.order-changed`: PARCIAL (11 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:top-assets-updated`: PARCIAL (7 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `unsubscribeMessage:top-assets-updated`: PARCIAL (7 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:trading-settings.digital-option-client-price-generated`: PARCIAL (5 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `unsubscribeMessage:trading-settings.digital-option-client-price-generated`: PARCIAL (5 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:currency-updated`: PARCIAL (3 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:marginal-forex.order-modified`: PARCIAL (3 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:marginal-cfd.order-modified`: PARCIAL (3 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:marginal-crypto.order-modified`: PARCIAL (3 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:candle-generated`: PARCIAL (3 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:profile-changed`: PARCIAL (2 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:forget-user-status-changed`: PARCIAL (2 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `unsubscribeMessage:marginal-forex.order-modified`: PARCIAL (2 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `unsubscribeMessage:marginal-cfd.order-modified`: PARCIAL (2 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `unsubscribeMessage:marginal-crypto.order-modified`: PARCIAL (2 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:customer-steps-data-updated`: PARCIAL (2 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.
- `subscribeMessage:traders-mood-changed`: PARCIAL (2 ocorrência(s)); evento de subscription observado, mas não comprovado como gatilho exclusivo de candle.

## Estrutura final do candle observada

```text
event: candle-generated | first-candles
active_id: presente em candle-generated e no request get-first-candles
size: presente em candle-generated; candles_by_size usa chaves numéricas
from: timestamp inicial
to: timestamp final
open: abertura
close: fechamento
min: candidato para low
max: candidato para high
volume: presente
```

## Conclusões classificadas

| Item | Classificação | Conclusão |
| --- | --- | --- |
| `get-first-candles` gera `first-candles` | CONFIRMADO | Há correlação por `request_id`. |
| `first-candles` retorna candles por tamanho | CONFIRMADO | `candles_by_size` contém OHLCV sanitizado. |
| `candle-generated` contém candle incremental | CONFIRMADO | Evento contém `active_id`, `size`, `from`, `to`, `open`, `close`, `min`, `max`, `volume`. |
| `candles-generated` representa candle completo | PARCIAL | Evento existe, mas a amostra sanitizada não comprova OHLC completo. |
| `active_id=76` é EUR/USD OTC | NÃO CONFIRMADO | ID observado, mas vínculo visual não comprovado. |
| `active_id` de GBP/USD OTC | NÃO CONFIRMADO | Nenhum vínculo visual comprovado. |
| `size=60` é M1 | PARCIAL | Tamanho observado, sem rótulo visual confirmado. |
| `size=300` é M5 | PARCIAL | Tamanho observado, sem rótulo visual confirmado. |
| `size=900` é M15 | PARCIAL | Tamanho observado, sem rótulo visual confirmado. |
| Subscription de candles | PARCIAL | `subscribeMessage` existe, mas gatilho específico não foi comprovado. |

## Limitações

- A captura não traz prova sanitizada suficiente de ativo visual ligado ao `active_id`.
- A captura não traz prova sanitizada suficiente de timeframe visual ligado a `size`.
- Não foi criado parser, integração runtime ou alteração funcional.
- Nenhum endpoint, Connector, Provider, pacote ou lockfile foi alterado.
