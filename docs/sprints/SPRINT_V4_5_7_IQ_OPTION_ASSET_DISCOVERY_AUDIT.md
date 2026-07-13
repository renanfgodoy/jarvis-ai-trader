# SPRINT V4.5.7 — IQ OPTION ASSET DISCOVERY AUDIT

## Objetivo

Auditar exclusivamente a descoberta de ativos da IQ Option.

IMPORTANTE:

Não alterar MarketChart, RealCandleChart, CandleStore, Chart API ou fluxo de candles.

Os gráficos já estão funcionando corretamente.

---

## Situação atual

Comprovado:

- OTC renderiza gráfico.
- REGULAR renderiza gráfico.
- 500 candles carregam normalmente.
- Bootstrap funciona.
- Polling funciona.
- Alternância OTC/REGULAR funciona.

Problema restante:

A lista de ativos continua vindo vazia ou incompleta.

O frontend usa corretamente o fallback:

OTC
→ EURUSD-OTC

REGULAR
→ EURUSD

O fallback não deve ser removido.

---

## Escopo

Auditar somente:

IQ Provider
↓
Asset Discovery
↓
response.assets

Sem alterar:

- fluxo React
- bootstrap
- polling
- renderização

---

## Verificar

### 1.

Onde exatamente os ativos são obtidos.

Localizar:

- provider IQ
- worker
- adapter
- parser

---

### 2.

Descobrir o retorno bruto da biblioteca.

Registrar:

quantidade total

exemplo:

raw assets = 37

ou

raw assets = []

---

### 3.

Comparar:

antes do parser

↓

depois do parser

↓

response.assets

---

### 4.

Verificar filtros.

Especialmente:

OTC

REGULAR

OPEN

enabled

visible

tradable

is_open

---

### 5.

Identificar se existe timeout.

Caso exista:

mostrar exatamente onde ocorre.

Não aumentar timeout sem comprovar necessidade.

---

### 6.

Verificar se a biblioteca mudou algum método interno.

Exemplo:

get_all_open_time

get_all_ACTIVES_OPCODE

subscribe_top_assets_updated

ou equivalente.

Não substituir método sem comprovação.

---

### 7.

Registrar exatamente:

quantos ativos

chegam ao worker

quantos chegam ao provider

quantos chegam à API

quantos chegam ao frontend

---

## Não fazer

Não alterar:

- bootstrap
- polling
- fallback
- gráfico
- Chart API
- CandleStore

Não criar nova arquitetura.

Não instalar dependências.

Não alterar Runtime Guard.

Não tocar na Polarium.

---

## Entrega esperada

Informar:

1.
Causa raiz comprovada.

2.
Arquivo(s) alterado(s).

3.
Quantidade de ativos encontrada.

4.
Quantidade enviada ao frontend.

5.
Diferença entre bruto e filtrado.

6.
Testes executados.

7.
Build.

8.
git status --short

9.
git diff --stat

10.
Sugestão de commit.

Não fazer commit.
Não fazer push.