# SPRINT V4.9 — POLARIUM PIPELINE LATENCY AUDIT

## Objetivo

Descobrir exatamente onde a Friday perde tempo entre o recebimento do evento da Polarium e a atualização visual do gráfico.

Não criar novos providers.

Não alterar arquitetura.

Não trocar IQ Option.

Não criar estratégias.

A Sprint é exclusivamente de auditoria e medição.

---

# CONTEXTO

Os HARs analisados mostram que TradeAutoPilot e Polarium utilizam os eventos:

- first-candles
- candle-generated
- candles
- timeSync

A Friday já utiliza esses mesmos eventos em sua arquitetura.

O objetivo agora é medir:

evento recebido

↓

parser

↓

runtime

↓

CandleStore

↓

SSE/browser bridge

↓

React

↓

RealCandleChart

↓

render

Não assumir onde está o gargalo.

Medir.

---

# PARTE 1 — TIMELINE

Registrar timestamps em todas as etapas.

Para cada candle:

T0
evento recebido

T1
parser terminou

T2
runtime recebeu

T3
CandleStore atualizado

T4
payload enviado ao frontend

T5
frontend recebeu

T6
merge concluído

T7
series.update()

T8
requestAnimationFrame

T9
frame desenhado

Calcular:

T1-T0

T2-T1

...

T9-T8

e total:

T9-T0

---

# PARTE 2 — PIPELINE

Auditar:

browser bridge

payload adapter

runtime

event parser

store

sync

RealCandleChart

requestAnimationFrame

Verificar se existe:

buffer

debounce

throttle

timeout

polling

setInterval

fila

espera desnecessária

render duplicado

merge repetido

re-render React

---

# PARTE 3 — DUPLICAÇÕES

Confirmar:

quantos:

series.update()

por candle

quantos:

setState()

por evento

quantos:

renders React

por candle

---

# PARTE 4 — COMPARAÇÃO

Comparar:

TradeAutoPilot

↓

Friday

Responder:

qual etapa existe apenas na Friday

qual etapa adiciona mais latência

qual etapa pode ser removida

---

# PARTE 5 — GARGALOS

Listar:

Top 10 maiores gargalos

com tempo médio

p50

p95

máximo

---

# PARTE 6 — PROPOSTAS

Somente após medir.

Para cada gargalo:

ganho esperado

risco

arquivos envolvidos

---

# PARTE 7 — TESTES

Executar:

pytest frontend

pytest completo

build

---

# ENTREGA

Entregar:

1. timeline completa

2. tabela por etapa

3. gráfico de latência (opcional)

4. gargalo principal

5. gargalo secundário

6. quantidade de renders

7. quantidade de series.update()

8. quantidade de merges

9. buffers encontrados

10. waits encontrados

11. polling encontrados

12. comparação Friday x TradeAutoPilot

13. arquivos envolvidos

14. testes

15. build

16. riscos

17. sugestão de commit

Não fazer commit.

Não fazer push.

Não alterar arquitetura antes da auditoria.