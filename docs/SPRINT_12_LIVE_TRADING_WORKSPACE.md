# Sprint 12 — Live Trading Workspace

## Objetivo

Criar a primeira versão do workspace operacional do J.A.R.V.I.S AI TRADER, substituindo o gráfico genérico por um gráfico de preço em **Candlestick**, conforme regra oficial do projeto.

## Regra oficial

Todo gráfico de preço do J.A.R.V.I.S AI TRADER deve usar formato **Candlestick / K-Line**. Gráficos de linha, área ou barras só devem ser usados para estatísticas, equity curve, performance, win rate ou métricas administrativas.

## O que foi implementado

- Novo endpoint REST:
  - `GET /api/v1/live/workspace`
- Novo WebSocket DEMO:
  - `WS /api/v1/live/workspace/ws`
- Novo componente frontend:
  - `CandlestickChart.tsx`
- Atualização do `ChartCard` para consumir o Live Workspace.
- Sincronização inicial entre melhor ativo do scanner e gráfico.
- Painel lateral de indicadores no gráfico:
  - EMA 9
  - EMA 21
  - RSI 14
  - ATR 14
  - Força do sinal
  - Último preço
- Testes automatizados do Live Workspace.

## Como testar

### Backend

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Abrir:

```text
http://127.0.0.1:8000/docs
```

Testar:

```text
GET /api/v1/live/workspace
```

### Frontend

Em outro terminal:

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm install
npm run dev
```

Abrir:

```text
http://localhost:5173
```

## Critérios de validação

- Swagger deve exibir a seção `Live Workspace`.
- `GET /api/v1/live/workspace` deve retornar candles OHLC, sinal técnico e Top 12.
- Dashboard deve exibir gráfico em Candlestick.
- O gráfico deve mostrar EMA 9, EMA 21 e volume.
- Testes devem passar.
- Nenhuma ordem real deve ser enviada.

## Status

Sprint 12 finalizada como base do Live Trading Workspace em modo DEMO/DRY_RUN.
