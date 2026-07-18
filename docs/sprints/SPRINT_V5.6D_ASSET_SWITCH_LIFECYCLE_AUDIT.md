# FRIDAY AI TRADER

# SPRINT V5.6D — ASSET SWITCH LIFECYCLE AUDIT

## Status

PLANEJADA

---

# 1. Objetivo

Auditar completamente o ciclo de troca de ativo da Friday para descobrir por que determinados ativos continuam exibindo bootstrap incompleto ou gráfico inconsistente mesmo após o backend comprovar que:

- parser funciona;
- bootstrap funciona;
- CandleStore funciona;
- history_count incrementa corretamente;
- Readiness chega em READY.

Esta Sprint é exclusivamente de auditoria.

Nenhuma correção deverá ser implementada.

---

# 2. Evidências confirmadas

As Sprints anteriores comprovaram:

✔ Parser funcional

✔ Bootstrap funcional

✔ CandleStore funcional

✔ History Count incrementando

✔ Readiness funcionando

✔ Merge append funcionando

✔ 200 candles sendo adicionados corretamente

Portanto, o problema não está mais na ingestão de dados.

---

# 3. Hipótese principal

O problema pode estar no ciclo de troca de ativo.

Fluxo auditado:

Usuário seleciona ativo

↓

Session Context

↓

Bootstrap solicitado

↓

Resposta recebida

↓

Bucket ativo atualizado

↓

Chart API

↓

Frontend

↓

Renderização

---

# 4. Objetivos técnicos

Auditar:

- mudança do Session Context;
- atualização do active_id;
- atualização do symbol;
- atualização do display_name;
- atualização do bucket ativo;
- troca da fonte do gráfico;
- descarte do bucket anterior;
- sincronização frontend/backend;
- múltiplos bootstraps concorrentes;
- respostas atrasadas;
- race conditions.

---

# 5. Escopo permitido

Adicionar apenas instrumentação.

Registrar:

selection_id

active_id anterior

active_id novo

symbol anterior

symbol novo

bucket anterior

bucket novo

request iniciado

request finalizado

request cancelado

request descartado

response ignorada

response aplicada

chart source anterior

chart source novo

render iniciado

render concluído

tempo entre etapas

---

# 6. Fora de escopo

Não alterar:

Parser

CandleStore

History Count

Readiness

HistoricalBootstrapManager

BootstrapRequestFactory

Scanner

Ranking

IA

Strategy Engine

Layout

Frontend visual

OAuth

Browser Bridge

CDP

---

# 7. Diagnóstico

Criar um componente:

AssetSwitchDiagnostic

Registrar automaticamente cada troca de ativo.

Cada troca deverá possuir um identificador único.

---

# 8. Relatório

Gerar:

.jarvis_cache/diagnostics/asset_switch_report.json

e

.jarvis_cache/diagnostics/asset_switch_report.txt

Resumo esperado:

Selection

symbol_before

symbol_after

active_before

active_after

bucket_before

bucket_after

bootstrap_started

bootstrap_finished

chart_updated

frontend_updated

failure_step

failure_reason

---

# 9. Categorias

ASSET_NOT_SWITCHED

SESSION_CONTEXT_STALE

BOOTSTRAP_NOT_STARTED

BOOTSTRAP_TIMEOUT

BOOTSTRAP_DISCARDED

BUCKET_NOT_UPDATED

CHART_NOT_UPDATED

FRONTEND_STALE

RACE_CONDITION

UNKNOWN

---

# 10. Segurança

Nunca registrar:

cookies

tokens

credenciais

headers

payloads completos

---

# 11. Testes

Adicionar testes cobrindo:

troca correta

troca repetida

troca concorrente

troca cancelada

frontend sincronizado

bucket atualizado

chart atualizado

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

Frontend

Backend CDP

Abrir:

EURUSD

↓

XAUUSD

↓

EURUSD

↓

XAUUSD

Comparar:

asset_switch_report.txt

---

# 14. Critério de conclusão

A Sprint termina apenas quando for possível identificar exatamente em qual etapa da troca de ativo ocorre a divergência.

Nenhuma correção deverá ser implementada.

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

chore(polarium): audit asset switch lifecycle