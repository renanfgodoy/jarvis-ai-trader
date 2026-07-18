# FRIDAY AI TRADER

# SPRINT V5.6C — HISTORY COUNT & CANDLESTORE AUDIT

## Status

PLANEJADA

---

# 1. Objetivo

Descobrir por que o bootstrap histórico recebido da Polarium chega corretamente ao runtime, é aceito pelo parser e pelo CandleStore, porém não incrementa corretamente o `history_count` nem promove o Readiness esperado.

Esta Sprint é exclusivamente de auditoria baseada em evidências.

Nenhuma correção especulativa deverá ser implementada.

---

# 2. Evidências confirmadas

As Sprints anteriores comprovaram:

✔ request enviado

✔ resposta recebida

✔ first-candles recebido

✔ raw_size resolvido corretamente

✔ parser aceitando candles

✔ correlação funcionando

✔ CandleStore recebendo candles

Entretanto:

history_count

permanece:

1 → 1

Mesmo após:

candles_found = 1

candles_accepted = 1

O comportamento ocorre tanto para:

EURUSD-OTC

quanto para:

XAUUSD-OTC

Portanto, a falha não é específica do ativo.

---

# 3. Arquitetura auditada

Auditar detalhadamente:

Session Context

↓

BootstrapRequestFactory

↓

Pending Requests

↓

Parser

↓

HistoricalBootstrapManager

↓

CandleStore

↓

History Count

↓

Readiness

Sem modificar a arquitetura.

---

# 4. Objetivo técnico

Comprovar:

Quem altera o history_count.

Quando altera.

Em qual condição altera.

Por que não altera.

Em qual coleção o contador é baseado.

Quem calcula o Readiness.

Se existe cache intermediário.

Se existe sincronização atrasada.

Se existe substituição ao invés de merge.

Se existe chave incorreta.

---

# 5. Escopo permitido

Adicionar apenas instrumentação.

Registrar:

store_key

bucket

active_id

symbol

raw_size

history_before

history_after

bucket_size

bucket_before

bucket_after

merge_type

append_count

replace_count

ignored_count

deduplicated_count

readiness_before

readiness_after

history_source

caller

stack simplificada

---

# 6. Fora de escopo

Não alterar:

Parser

BootstrapRequestFactory

HistoricalBootstrapManager

Readiness

Session Context

Runtime Guard

Strategy Engine

Scanner

Ranking

IA

CALL

PUT

Backtest

Layout

OAuth

CDP

Browser Bridge

Seleção de ativo

---

# 7. Instrumentação

Criar auditoria específica do CandleStore.

Nome sugerido:

HistoryCountDiagnostic

Registrar automaticamente:

- quem chamou o Store;
- chave utilizada;
- quantidade existente;
- quantidade recebida;
- quantidade gravada;
- quantidade descartada;
- motivo do descarte;
- history_count antes;
- history_count depois;
- readiness antes;
- readiness depois.

---

# 8. Relatório automático

Gerar:

.jarvis_cache/diagnostics/history_count_report.json

e

.jarvis_cache/diagnostics/history_count_report.txt

Resumo esperado:

STORE

symbol

raw_size

history_before

history_after

bucket_before

bucket_after

merge_type

append

replace

ignored

deduplicated

caller

failure_reason

---

# 9. Classificação

Categorias permitidas:

STORE_KEY_MISMATCH

STORE_BUCKET_MISMATCH

MERGE_FAILED

MERGE_SKIPPED

MERGE_REPLACED

HISTORY_NOT_INCREMENTED

READINESS_NOT_UPDATED

DUPLICATE_FILTER

UNKNOWN

---

# 10. Segurança

Nunca registrar:

cookies

tokens

headers

OAuth

payloads completos

credenciais

---

# 11. Testes

Adicionar testes para:

append correto

replace correto

merge correto

history incrementado

history não incrementado

bucket incorreto

bucket correto

readiness atualizado

relatório gerado

dados sensíveis ausentes

M1 preservado

M5 preservado

M15 preservado

---

# 12. Validação automatizada

Executar:

python -m pytest tests/market/providers -v

Depois:

python -m pytest -v

Executar:

npm run build

---

# 13. Validação real

Executar:

Frontend

Backend CDP

Selecionar:

EURUSD M5

Depois:

XAUUSD M5

Executar:

cat .jarvis_cache/diagnostics/history_count_report.txt

O relatório deverá mostrar exatamente quem deixou de incrementar o history_count.

---

# 14. Critério de conclusão

A Sprint termina apenas quando for possível apontar exatamente:

qual método

qual arquivo

qual condição

é responsável por impedir o incremento correto do history_count.

Nenhuma correção deverá ser aplicada nesta Sprint.

---

# 15. Entrega obrigatória

Objetivo

Arquitetura auditada

Arquivos criados

Arquivos modificados

Instrumentação

Testes

Resultados

Build

Exemplo do relatório

git status

git diff

Riscos

Próximos passos

Sugestão de commit

---

# 16. Git

Não executar:

git add

git commit

git push

sem autorização explícita do Renan.

---

# 17. Sugestão de commit

chore(polarium): audit history count and candlestore flow