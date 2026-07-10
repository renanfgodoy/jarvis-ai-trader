# FRIDAY TRADE V2.7

# AUTHORIZED WEBSOCKET CANDLE CAPTURE

Status

PLANNED

---

# Objetivo

Esta Sprint tem um único objetivo:

Descobrir, usando uma sessão AUTORIZADA da Polarium, como capturar candles reais de mercado.

O Friday Trade NÃO fará operações.

NÃO enviará ordens.

NÃO clicará na plataforma.

NÃO automatizará trades.

Apenas observará dados de mercado.

---

# Regras obrigatórias

NÃO alterar:

- Frontend
- Dashboard
- Markets
- Analysis
- Replay
- Settings

NÃO alterar:

- APIs públicas

- Providers

- Connector em produção

- package.json

- package-lock.json

NÃO adicionar dependências.

NÃO fazer commit.

NÃO fazer push.

---

# Antes de começar

Executar

cd /Users/renangodoy/Desktop/jarvis-ai-trader

git status --short

git branch --show-current

.venv/bin/python -m pytest -q

cd frontend

npm run build

Tudo deve continuar verde.

---

# Objetivo técnico

Usar apenas ferramentas já existentes no projeto.

Especialmente:

OAuth Lab

WS Diagnostic

WS Recorder

Diagnostics

Session Inspector

---

# Fluxo esperado

Operador faz login manualmente na Polarium

↓

OAuth válido

↓

Sessão válida

↓

Abrir gráfico

↓

Selecionar ativo

↓

Selecionar timeframe

↓

WS Recorder captura frames

↓

Salvar frames

↓

Classificar mensagens

↓

Identificar candles

↓

Gerar relatório

---

# O que investigar

Precisamos confirmar:

Existe evento candle-generated?

Existe snapshot inicial?

Existe histórico?

Existe stream?

Existe heartbeat?

Existe active_id?

Existe symbol?

Existe timeframe?

Existe timestamp?

Existe OHLC?

Existe volume?

Existe sequência de subscription?

---

# Evidências

Cada descoberta deve ser classificada como:

CONFIRMADO

PARCIAL

NÃO ENCONTRADO

Nunca assumir.

Nunca inferir.

---

# Criar documento

Atualizar

docs/REAL_MARKET_DATA_REPORT.md

Adicionar:

Nova seção

Sprint V2.7

Com:

Frames observados

Eventos observados

Eventos descartados

Campos encontrados

Campos ausentes

Hipóteses

Próximos passos

---

# Criar artefato

Criar:

docs/ws/

Caso existam capturas sanitizadas.

Nunca salvar:

cookies

authorization

bearer

refresh token

headers privados

credenciais

SSID

HAR completo

---

# Candle

Caso exista payload confirmado

documentar exatamente:

symbol

active_id

timeframe

timestamp

open

high

low

close

volume (se existir)

Nunca preencher campos ausentes.

---

# Adapter

Se houver confirmação de payload,

atualizar apenas:

app/market/adapters/market_data_adapter.py

para refletir os campos realmente confirmados.

Não integrar ao runtime.

---

# Não implementar

Não criar:

EMA

RSI

MACD

CALL

PUT

BUY

SELL

Probability

Execution

AutoTrade

Signals

---

# Como testar

Backend

.venv/bin/python -m uvicorn app.main:app --reload

Frontend

cd frontend

npm run dev

Fluxo

Abrir:

Connections

↓

OAuth

↓

Sessão

↓

WS Recorder

↓

Abrir Polarium autorizada

↓

Selecionar gráfico

↓

Selecionar ativo

↓

Selecionar timeframe

↓

Capturar frames

↓

Analisar

↓

Atualizar relatório

---

# Critérios de aprovação

Nenhuma operação enviada.

Nenhum clique automatizado.

Nenhuma credencial exposta.

Nenhum segredo salvo.

Nenhuma alteração no runtime.

Relatório técnico atualizado.

Payloads classificados corretamente.

---

# Entrega obrigatória

1. Objetivo

2. Arquivos modificados

3. Arquivos criados

4. Frames capturados

5. Eventos confirmados

6. Eventos descartados

7. Estrutura real do payload

8. Campos confirmados

9. Campos ausentes

10. Atualização do MarketDataAdapter

11. Limitações

12. Próximos passos

13. Resultado do pytest

14. Resultado do build

15. git status --short

16. git diff --stat

17. Sugestão de commit

Sugestão:

feat(market): capture authorized websocket market evidence

Não fazer commit.

Não fazer push.