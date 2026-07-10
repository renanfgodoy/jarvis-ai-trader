# FRIDAY TRADE V2.5

# MARKET CONTEXT ENGINE

Status

PLANNED

---

# Objetivo

Criar o Market Context Engine.

Esta Sprint NÃO implementa IA.

Esta Sprint NÃO implementa indicadores.

Esta Sprint NÃO implementa Probability Engine.

Ela cria uma visão consolidada da qualidade e disponibilidade dos dados de mercado.

O Friday Trade deve informar claramente:

"Qual o contexto atual do mercado?"

---

# Regras

NÃO alterar:

- Backend
- APIs
- Connector
- Providers
- OAuth
- Dependências
- package.json
- package-lock.json

Não fazer commit.

Não fazer push.

---

# Antes de começar

Executar:

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short

.venv/bin/python -m pytest -q

cd frontend
npm run build
```

Tudo deve continuar verde.

---

# Objetivo visual

Criar uma tela extremamente limpa.

O operador deve bater o olho e entender:

• onde está conectado

• qual ativo está analisando

• se os dados são suficientes

• se existe bloqueio

• se a IA poderá trabalhar futuramente

---

# Layout

Cabeçalho

Ativo

Broker

Conta

Ambiente

Timeframe

Última atualização

---

Card 1

Status do Mercado

Aberto

Fechado

Indisponível

---

Card 2

Fonte dos Dados

Polarium

Provider

Desconhecida

---

Card 3

Qualidade dos Dados

Excelente

Boa

Parcial

Insuficiente

Baseado apenas em dados reais.

Nunca inventar qualidade.

---

Card 4

Conexão

Conectado

Reconectando

Desconectado

---

Card 5

Candles

Disponível

Não disponível

---

Card 6

Scanner

Disponível

Bloqueado

---

Card 7

AI Engine

Preparado

Aguardando

Bloqueado

---

Card 8

Motivos do bloqueio

Listar exatamente:

- sem ativo
- sem broker
- sem candles
- sem conexão
- sem fonte

Nunca mensagem genérica.

---

# Resultado final

Mostrar apenas:

READY

PARTIAL

BLOCKED

Baseado apenas no estado real.

---

# Sem dados fictícios

Não criar:

- EMA
- RSI
- MACD
- Probabilidade
- CALL
- PUT
- BUY
- SELL
- Score

---

# Integração

Consumir somente:

Market Data Context

Analysis Readiness

Broker

Conta

Ambiente

Ativo

Timeframe

Status

Última atualização

Sem endpoint novo.

---

# UX

Visual premium.

Poucos cards.

Muito espaço.

Sem widgets repetidos.

Sem dashboard poluído.

---

# Como testar

Backend

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m uvicorn app.main:app --reload
```

Frontend

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader/frontend

npm run dev
```

Testar:

/analysis

Sem ativo

↓

BLOCKED

Selecionar ativo

↓

PARTIAL

Se existir conexão

↓

Atualizar contexto

↓

READY apenas quando TODOS os requisitos reais existirem.

Console deve permanecer limpo.

---

# Critérios de aprovação

Nenhum backend alterado.

Nenhuma API alterada.

Nenhum endpoint novo.

Nenhum indicador criado.

Nenhuma IA criada.

Nenhuma probabilidade criada.

Nenhum dado inventado.

Tela preparada para futura AI Engine.

---

# Entrega Obrigatória

1. Objetivo

2. Arquivos modificados

3. Arquivos criados

4. Componentes criados

5. Fluxo READY / PARTIAL / BLOCKED

6. Resultado do pytest

7. Resultado do build

8. Como testar

9. git status --short

10. git diff --stat

11. Sugestão de commit

Sugestão:

feat(frontend): introduce Market Context Engine

Não fazer commit.

Não fazer push.