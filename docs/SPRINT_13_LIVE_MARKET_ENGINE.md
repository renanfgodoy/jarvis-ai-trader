# Sprint 13 — Live Market Engine

## Objetivo

Transformar o Live Trading Workspace em uma área mais viva, com candles simulados em tempo real, countdown da vela e canal WebSocket para atualizações contínuas.

## Entregas

- Novo `LiveMarketEngine` em `app/services/live_market.py`.
- Novos models em `app/models/live.py`.
- Endpoint REST `GET /api/v1/live/candles`.
- Endpoint REST `GET /api/v1/live/tick`.
- WebSocket `WS /api/v1/live/workspace/ws`.
- Dashboard consumindo atualizações em tempo real.
- Countdown da vela M1 no frontend.
- Candlestick com visual mais profissional, crosshair e labels.

## Segurança

Tudo permanece em modo `DEMO/DRY_RUN`.

Nenhuma ordem real é enviada.

## Como testar

```bash
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

Abra:

```text
http://127.0.0.1:8000/docs
```

Teste:

```text
GET /api/v1/live/candles
GET /api/v1/live/tick
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Abra:

```text
http://localhost:5173
```

## Critérios de validação

- API inicia sem erro.
- Swagger mostra Live Market Engine.
- `/live/tick` retorna `candles`, `signal`, `top_assets` e `countdown_seconds`.
- Dashboard exibe Candlestick e countdown.
- Testes passam.
