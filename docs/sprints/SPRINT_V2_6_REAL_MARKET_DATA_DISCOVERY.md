# FRIDAY TRADE V2.6

# REAL MARKET DATA DISCOVERY

Status

PLANNED

---

# Objetivo

Descobrir uma forma confiável e sustentável de obter dados reais de mercado para alimentar o Friday Trade.

Esta Sprint é INVESTIGATIVA.

Ela NÃO implementa IA.

Ela NÃO implementa AutoTrade.

Ela NÃO envia ordens.

Ela NÃO automatiza operações.

Ela NÃO tenta burlar autenticação.

O objetivo é descobrir como consumir dados de mercado de uma sessão autorizada.

---

# Regras

NÃO alterar:

- Frontend
- Dashboard
- Markets
- Analysis
- Replay
- Settings

Exceto se for absolutamente necessário para testes internos.

Não adicionar dependências.

Não alterar package.json.

Não alterar package-lock.json.

Não fazer commit.

Não fazer push.

---

# Antes de começar

Executar

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

# Objetivo Técnico

Mapear exatamente:

Como a Polarium entrega:

• ativos

• candles

• OHLC

• timestamps

• timeframe

• atualizações

• OTC

• eventos

• heartbeat

• reconnect

---

# Fontes permitidas

Usar apenas:

✔ sessão autorizada

✔ endpoints existentes

✔ WebSocket existente

✔ OAuth existente

✔ documentação pública

✔ evidências observadas

Nunca:

inventar endpoints

inventar payloads

inventar candles

---

# Investigar

Mapear:

HTTP

↓

OAuth

↓

Session

↓

WebSocket

↓

Subscriptions

↓

Mensagens

↓

Candles

↓

Parser

---

# Criar documento

Criar:

docs/REAL_MARKET_DATA_REPORT.md

Contendo:

Fluxo encontrado

Endpoints observados

Mensagens WS observadas

Payloads observados

Campos identificados

Eventos

Heartbeat

Reconnect

Limitações

Hipóteses

Próximos passos

---

# Criar Adapter

Criar apenas contratos internos.

Exemplo:

app/market/adapters/

market_data_adapter.py

Sem alterar runtime.

---

# Modelo de Candle

Definir apenas contrato.

Nunca preencher dados fictícios.

Estrutura esperada:

symbol

timeframe

open

high

low

close

timestamp

source

confirmed

---

# Confirmar

Identificar claramente:

Existe candle?

Existe OHLC?

Existe timestamp?

Existe stream?

Existe snapshot?

Existe histórico?

Ou ainda não?

Responder baseado apenas em evidências.

---

# NÃO IMPLEMENTAR

Não criar:

EMA

RSI

MACD

Probability

CALL

PUT

BUY

SELL

Execution

AutoTrade

---

# Resultado esperado

Ao final responder:

Conseguimos obter:

✓ ativos

✓ candles

✓ timestamps

✓ timeframe

✓ atualização

ou

Explicar exatamente

qual etapa bloqueou.

---

# Como testar

Backend

```bash
cd /Users/renangodoy/Desktop/jarvis-ai-trader

.venv/bin/python -m uvicorn app.main:app --reload
```

Frontend

```bash
cd frontend

npm run dev
```

Executar os diagnósticos já existentes.

Validar que nada do frontend foi quebrado.

---

# Critérios de aprovação

Nenhum backend funcional quebrado.

Nenhuma API quebrada.

Nenhuma tela alterada.

Nenhuma ordem enviada.

Nenhum segredo exposto.

Nenhum dado fictício criado.

Relatório técnico completo.

---

# Entrega Obrigatória

1. Objetivo

2. Arquivos modificados

3. Arquivos criados

4. Evidências encontradas

5. Endpoints identificados

6. Eventos WebSocket

7. Estrutura dos payloads

8. Fluxo HTTP → OAuth → WS

9. Modelo de Candle

10. Limitações

11. Próximos passos

12. Resultado do pytest

13. Resultado do build

14. git status --short

15. git diff --stat

16. Sugestão de commit

Sugestão:

docs(market): document real market data discovery

Não fazer commit.

Não fazer push.