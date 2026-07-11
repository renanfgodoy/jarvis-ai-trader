# FRIDAY TRADE V3.4

# REAL CANDLE CHART FOUNDATION

Status

PLANNED

---

# Objetivo

Criar a primeira visualização gráfica REAL do Friday Trade.

O gráfico deverá consumir exclusivamente candles existentes no Candle Store.

Nesta Sprint NÃO conectar ao WebSocket real.

Nesta Sprint NÃO alterar Connector.

Nesta Sprint NÃO alterar Providers.

Nesta Sprint NÃO alterar APIs existentes.

Nesta Sprint NÃO criar indicadores.

Nesta Sprint NÃO criar IA.

Nesta Sprint NÃO criar Probability Engine.

---

# Objetivo visual

Criar uma página capaz de renderizar candles reais armazenados no Candle Store.

A origem dos candles continua sendo o pipeline passivo criado nas Sprints anteriores.

O frontend deve ficar preparado para receber atualizações futuras em tempo real.

---

# Biblioteca

Utilizar:

TradingView Lightweight Charts

Não utilizar iframe.

Não utilizar screenshot.

Não utilizar espelhamento da tela da Polarium.

O gráfico deve ser totalmente nativo do Friday Trade.

---

# Backend

Criar uma camada somente leitura.

Criar:

app/market/chart/

    __init__.py

    service.py

    models.py

Ela apenas transforma candles do Candle Store em formato adequado para o frontend.

Não abrir WebSocket.

Não conectar Connector.

---

# Frontend

Criar:

frontend/src/components/chart/

    RealCandleChart/

Criar:

frontend/src/hooks/

    useRealCandles.ts

Criar:

frontend/src/pages/

    MarketChart.tsx

---

# Dados

O gráfico deve aceitar:

active_id

raw_size

lista de candles

Nada mais.

Não inventar:

symbol

M1

M5

M15

---

# Funcionalidades

Renderizar:

candles

zoom

pan

crosshair

escala automática

---

# Não implementar

EMA

RSI

MACD

Volume

ATR

VWAP

Probabilidade

IA

Replay

Sinais

AutoTrade

---

# Testes

Adicionar testes para:

transformação Candle Store → Chart

lista vazia

candle único

múltiplos candles

ordenação

---

# Critérios

Nenhuma dependência do Connector.

Nenhuma dependência da Polarium.

Somente Candle Store.

Sem runtime.

---

# Como testar

Backend:

.venv/bin/python -m pytest -q

Frontend:

npm run build

Rodar:

npm run dev

Abrir:

/market-chart

O gráfico deve aparecer utilizando candles existentes no Candle Store.

Mesmo que ainda sejam poucos.

---

# Entrega

Mesmo padrão das últimas Sprints.

Não fazer commit.

Não fazer push.