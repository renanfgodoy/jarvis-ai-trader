# V0.16.0 — Real Market Data Foundation

## Objetivo

Preparar o J.A.R.V.I.S AI TRADER para sair gradualmente dos dados simulados e receber dados reais de mercado sem quebrar a arquitetura existente.

## Entregas

- Modelo `MarketAsset` com ativo, status, payout, timeframes suportados e qualidade do dado.
- Endpoint `GET /api/v1/market/assets`.
- Endpoint `GET /api/v1/providers/assets`.
- Provider Manager agora expõe ativos normalizados.
- Scanner passa a carregar payout/status/qualidade do provider.
- Dashboard passa a exibir se os dados são `SIMULATED`, `REAL`, `DELAYED` ou `UNAVAILABLE`.

## Regra operacional

Enquanto a integração real não estiver pronta, o sistema deve mostrar claramente quando está usando dados simulados. Nenhuma ordem real deve ser executada.

## Como testar

```bash
cd ~/Desktop/jarvis-ai-trader
source .venv/bin/activate
python -m pytest
python -m uvicorn app.main:app --reload
```

Valide no Swagger:

- `/api/v1/market/assets`
- `/api/v1/providers/assets`
- `/api/v1/scanner/top-assets`

No frontend:

```bash
cd ~/Desktop/jarvis-ai-trader/frontend
npm install
npm run dev
```

Abra `http://localhost:5173` e verifique se o scanner/header mostram a origem dos dados.
