# SPRINT V5.8C — Bootstrap Payload Trace

## Objetivo

Determinar definitivamente por que alguns ativos (ex.: XAUUSD-OTC e BTCUSD-OTC-op) permanecem com apenas 1 candle após o bootstrap histórico, enquanto EURUSD recebe centenas.

Esta Sprint é exclusivamente de auditoria.

Não alterar parser, CandleStore, Runtime, Readiness, Strategy Engine, Chart API, frontend ou endpoint de seleção.

---

## Evidências já comprovadas

Já está comprovado:

- seleção programática funciona;
- subscribeMessage funciona;
- get-first-candles é enviado;
- Session Context troca corretamente;
- CandleStore recebe pelo menos um candle.

Também está comprovado que:

EURUSD:

history_count:
212 → 312

READY → READY

XAUUSD:

0 → 1

LIMITED

BTCUSD:

0 → 1

LIMITED

Depois disso aparecem apenas DUPLICATE_FILTER.

---

## Missão

Instrumentar exclusivamente o caminho da resposta:

first-candles

até

CandleStore.

Sem modificar comportamento.

---

## Instrumentação obrigatória

Registrar:

request_id

active_id

symbol

raw_size

response_message_type

payload_format_detected

candles_in_payload

candles_after_parser

candles_after_validation

candles_written

candles_ignored

duplicate_count

first_timestamp

last_timestamp

bucket_before

bucket_after

history_before

history_after

readiness_before

readiness_after

---

## Payload

Nunca gravar:

cookies

authorization

bearer

SSID

headers

payload bruto

Registrar apenas:

quantidade de candles

timestamps

estatísticas

---

## Categorias

Adicionar somente:

PAYLOAD_EMPTY

PAYLOAD_SINGLE_CANDLE

PAYLOAD_MULTI_CANDLE

PARSER_DROPPED

VALIDATION_DROPPED

STORE_DROPPED

DUPLICATE_FILTER

SUCCESS

UNKNOWN

---

## Relatórios

Gerar:

.jarvis_cache/diagnostics/bootstrap_payload_report.json

.jarvis_cache/diagnostics/bootstrap_payload_report.txt

---

## Exemplo esperado

XAUUSD:

Payload:

100 candles

↓

Parser:

100

↓

Validation:

100

↓

Store:

1

↓

Duplicates:

99

Categoria:

STORE_DROPPED

ou

Payload:

1 candle

↓

Parser:

1

↓

Categoria:

PAYLOAD_SINGLE_CANDLE

---

## Testes

Adicionar cobertura para:

payload vazio

payload 1 candle

payload 100 candles

parser reduzindo

validation reduzindo

store reduzindo

duplicate filter

EURUSD

XAUUSD

BTCUSD

M1

M5

M15

---

## Build

Executar:

python -m pytest tests/market/providers -v

python -m pytest -v

cd frontend

npm run build

---

## Validação real

Rodar novamente:

POST /api/dev/select-market

para:

EURUSD

XAUUSD

BTCUSD

Comparar bootstrap_payload_report.

---

## Entrega

Obrigatoriamente informar:

Objetivo

Arquitetura

Arquivos criados

Arquivos modificados

Causa comprovada

Resultados

Testes

Build

Validação

git status

git diff

Riscos

Próximos passos

Sugestão de commit

Não executar git add.

Não executar commit.

Não executar push.