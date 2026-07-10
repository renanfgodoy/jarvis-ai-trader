# FRIDAY TRADE V2.9

# DIRECTED CANDLE CORRELATION

Status

PLANNED

---

# Objetivo

Executar uma análise dirigida sobre a captura HAR autorizada para comprovar a correlação entre:

- ativo visual
- active_id
- timeframe visual
- duration/size
- candles
- subscriptions
- eventos do WebSocket

O objetivo NÃO é criar parser.

O objetivo NÃO é integrar ao runtime.

O objetivo é gerar evidência suficiente para a Sprint seguinte (Candle Parser).

---

# Regras obrigatórias

Não alterar:

- frontend
- backend funcional
- APIs
- Connector
- Providers
- package.json
- package-lock.json

Não adicionar dependências.

Não fazer commit.

Não fazer push.

---

# Antes de começar

Executar:

cd /Users/renangodoy/Desktop/jarvis-ai-trader

git status --short

git branch --show-current

.venv/bin/python -m pytest -q

cd frontend

npm run build

Tudo deve continuar verde.

---

# Entrada

Utilizar apenas:

.jarvis_cache/evidence/trade.polariumbroker.com.har

Nunca mover o HAR.

Nunca adicionar o HAR ao Git.

---

# Objetivo da investigação

Correlacionar:

ATIVO VISUAL

↓

active_id

↓

subscription

↓

eventos

↓

candles

↓

OHLC

↓

timeframe

---

# Confirmar

Investigar se é possível demonstrar:

EUR/USD OTC

↓

active_id = ?

↓

size = ?

↓

subscription = ?

↓

candle-generated

---

Repetir para:

GBP/USD OTC

---

E para:

M1

↓

size = ?

M5

↓

size = ?

M15

↓

size = ?

---

# Validar

Comparar:

open

close

min

max

volume

from

to

size

active_id

entre diferentes ativos e timeframes.

---

# Subscription

Descobrir:

qual mensagem gera:

first-candles

qual gera:

candle-generated

qual gera:

candles-generated

Documentar exatamente.

---

# Active ID

Investigar:

há algum request HTTP

ou payload WS

que contenha:

active_id

+

symbol

ou

instrument

ou

display_name

ou

asset

ou

ticker

Nunca assumir.

---

# Timeframe

Investigar:

60

300

900

Representam:

M1

M5

M15

Somente marcar como confirmado se houver evidência.

---

# Criar documento

Atualizar:

docs/REAL_MARKET_DATA_REPORT.md

Adicionar seção:

Sprint V2.9

---

Criar:

docs/ws/POLARIUM_DIRECTED_CORRELATION.md

Com:

Evento

↓

Subscription

↓

Ativo

↓

active_id

↓

Timeframe

↓

Payload

↓

Conclusão

---

# Adapter

Não alterar.

Ainda não.

---

# Não implementar

Não criar:

Parser

EMA

RSI

MACD

IA

Probability

Signals

Execution

AutoTrade

Ordens

---

# Como testar

Backend

.venv/bin/python -m uvicorn app.main:app --reload

Frontend

cd frontend

npm run dev

Confirmar que:

Nada do runtime mudou.

---

# Critérios de aprovação

Nenhuma alteração funcional.

Nenhuma API modificada.

Nenhum Connector modificado.

Nenhuma credencial exposta.

Correlação documentada.

---

# Entrega obrigatória

1. Objetivo

2. Arquivos criados

3. Arquivos modificados

4. Active IDs encontrados

5. Correlação ativa

6. Timeframes encontrados

7. Correlação de size

8. Subscription encontrada

9. Eventos confirmados

10. Eventos parciais

11. Estrutura final do candle

12. Limitações

13. Resultado do pytest

14. Resultado do build

15. git status --short

16. git diff --stat

17. Próxima Sprint recomendada

18. Sugestão de commit

Sugestão:

docs(market): document directed candle correlation

Não fazer commit.

Não fazer push.