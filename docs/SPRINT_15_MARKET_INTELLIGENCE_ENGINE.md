# V0.15.0 — Market Intelligence Engine

## Objetivo

Transformar o scanner em um motor de inteligência operacional com score explicável de 0 a 100.

## Entregas

- `ConfluenceEngineService`
- `MarketIntelligenceService`
- Endpoint `GET /api/v1/intelligence/analyze`
- Endpoint `GET /api/v1/intelligence/scanner/top`
- Scanner Top 12 com payout, score, status e motivos
- Painel de Market Intelligence no dashboard
- Testes automatizados

## Regra operacional

O robô só deve gerar análise após:

1. Timeframe selecionado: M1, M5 ou M15.
2. AutoTrade ativado pelo operador.
3. Conta DEMO.
4. Moeda da conta detectada.
5. Entrada mínima respeitada.
6. Risk Manager aprovado.

## Como testar

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest
python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm install
npm run dev
```

URLs:

- `http://127.0.0.1:8000/docs`
- `http://localhost:5173`

## Critérios de validação

- Swagger mostra `Market Intelligence`.
- `/api/v1/intelligence/analyze` retorna score e fatores.
- `/api/v1/intelligence/scanner/top` retorna Top 12.
- Dashboard mostra score, payout e explicação.
- Testes passam.
