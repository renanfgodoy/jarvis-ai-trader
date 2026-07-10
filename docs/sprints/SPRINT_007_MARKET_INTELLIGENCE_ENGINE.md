# SPRINT 7 — MARKET INTELLIGENCE ENGINE

## Status

Planned

---

# Objetivo

Criar o primeiro núcleo do Market Intelligence Engine.

Esta Sprint NÃO tem como objetivo executar operações.

Esta Sprint NÃO implementa AutoTrade.

Esta Sprint NÃO altera Risk.

Esta Sprint NÃO altera Execution.

O objetivo é descobrir e organizar os dados de mercado necessários para alimentar a IA do Friday Trade.

O sistema deve aprender a observar o mercado.

Ainda não deve decidir.

---

# Objetivo Estratégico

O Friday Trade será um Copilot de Trading.

Fluxo futuro:

Mercado

↓

Market Intelligence

↓

AI Decision Engine

↓

Operador

↓

Execução Manual

AutoTrade permanece como evolução futura.

---

# Escopo

Criar uma camada responsável por coletar e organizar informações de mercado.

Criar:

```text
frontend/src/intelligence/

backend/app/market/
```

Caso parte da estrutura backend já exista, apenas organizar sem alterar comportamento.

---

# O que será analisado

O objetivo desta Sprint NÃO é interpretar.

É descobrir.

O sistema deve ser preparado para observar:

- ativos
- candles
- timeframe
- timestamps
- sincronização
- broker
- ambiente
- conta
- moeda
- atualização do mercado

Não criar indicadores técnicos ainda.

---

# Discovery

Criar uma camada chamada:

Market Discovery

Responsável por registrar:

Ativo selecionado

Timeframe

Status do mercado

Status do Connector

Última atualização

Fonte dos dados

Disponibilidade

Nunca registrar:

token

cookie

authorization

bearer

refresh token

HAR

payload sensível

---

# Estrutura

Preparar:

```text
Market Discovery

↓

Market Snapshot

↓

Future AI Engine
```

Ainda sem IA.

---

# Snapshot

Criar um modelo visual.

Mostrar:

Ativo

Timeframe

Broker

Conta

Moeda

Ambiente

Atualização

Market Ready

Tudo utilizando dados existentes.

Sem inventar estados.

---

# Frontend

Criar página:

/markets/intelligence

Adicionar no menu Markets.

A página deve mostrar:

Resumo

Snapshot

Fonte

Última atualização

Status

Sem gráficos complexos.

Sem indicadores.

---

# Componentes

Criar:

MarketSnapshotCard

MarketDiscoveryStatus

MarketSourceCard

MarketReadinessCard

DiscoveryTimeline

Todos reutilizáveis.

---

# Hooks

Criar apenas quando necessário.

Exemplos:

useMarketDiscovery

useMarketSnapshot

---

# Backend

Não alterar regras existentes.

Somente organizar diretórios caso necessário.

Não quebrar imports.

---

# Segurança

Nunca exibir:

tokens

cookies

authorization

headers

HAR

credenciais

payload bruto

---

# Não Fazer

Não criar AutoTrade.

Não criar IA.

Não criar indicadores.

Não criar EMA.

Não criar RSI.

Não criar MACD.

Não criar Probability Engine.

Não alterar Connector.

Não alterar Providers.

Não alterar APIs.

Não instalar dependências.

---

# Testes

Executar:

Frontend

npm run build

Backend

.venv/bin/python -m pytest -q

---

# COMO TESTAR

Ensinar o Renan.

Subir Backend.

Subir Frontend.

Abrir:

/markets/intelligence

Validar:

Snapshot

Discovery

Readiness

Fonte

Atualização

Console

Enviar prints.

---

# Critérios de Aprovação

Página criada.

Snapshot funcionando.

Discovery funcionando.

Readiness funcionando.

Sem backend alterado.

Sem Connector alterado.

Sem regressão.

Build aprovado.

Testes aprovados.

---

# Entrega Obrigatória

1. Objetivo

2. Arquitetura

3. Componentes criados

4. Hooks criados

5. Arquivos modificados

6. Build

7. Testes

8. Como testar

9. Critérios

10. Riscos

11. git status

12. Sugestão de commit

Mensagem sugerida:

feat(intelligence): introduce Market Intelligence discovery layer

---

# Regra Final

Não faça commit.

Não faça push.

Pare após entregar o relatório completo.