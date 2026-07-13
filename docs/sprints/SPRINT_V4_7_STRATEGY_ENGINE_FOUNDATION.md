# FRIDAY TRADE
## Sprint V4.7 — Strategy Engine Foundation

---

## Objetivo

Iniciar oficialmente o Friday Strategy Engine.

Esta Sprint marca a transição do Friday de um visualizador de mercado para uma plataforma preparada para múltiplas estratégias.

O foco desta Sprint é exclusivamente criar a arquitetura do painel de estratégias.

Nenhuma lógica operacional será implementada.

---

## Escopo

Criar a fundação do Strategy Engine.

Criar o painel "Friday Strategy Engine".

Preparar a arquitetura para múltiplas estratégias.

Persistir apenas estados de interface.

---

## Estado Inicial

Exibir:

Estratégia
Nenhuma estratégia carregada

Status
Aguardando estratégia

Readiness
Inativo

Confluências
0 avaliadas

---

## Estrutura esperada

Cada estratégia deverá suportar futuramente:

- id
- nome
- descrição
- autor
- versão
- mercados suportados
- timeframes suportados
- status
- readiness
- lista de confluências

Nesta Sprint apenas criar a arquitetura.

---

## Fora do Escopo

NÃO criar:

- CALL
- PUT
- Compra
- Venda
- Score
- Probabilidade
- IA
- Entradas
- Backtest
- Estatísticas

---

## NÃO ALTERAR

- Backend
- Runtime
- Worker
- IQ Option
- SSE
- Polling
- CandleStore
- Chart API
- Lista de ativos
- Conexão
- Fluxo de candles

---

## Modificar apenas

Frontend.

Interface.

Componentização.

Arquitetura do painel.

---

## Critérios de Aceitação

O painel deve permanecer vazio quando não houver estratégia.

Toda a estrutura deverá permitir adicionar novas estratégias sem reescrever o painel.

Nenhuma regressão visual.

Nenhuma regressão no gráfico.

Nenhuma regressão na seleção de ativos.

Nenhuma regressão de SSE.

Nenhuma regressão de polling.

---

## Testes obrigatórios

- pytest frontend
- pytest completo
- npm run build

---

## Entregáveis

Informar:

- arquivos modificados
- diff funcional
- testes executados
- build
- validação visual
- git status
- git diff --stat

---

## Git

NÃO executar:

- git add
- git commit
- git push

Sem autorização explícita do Renan.