# Sprint 2 — Market Reader Foundation

## Objetivo

Criar a primeira fundação real de leitura de mercado do J.A.R.V.I.S AI TRADER, sem depender ainda de corretora ou API externa.

## Decisão técnica

Nesta Sprint usamos um provider simulado. Isso permite testar arquitetura, models, endpoints e validações sem risco operacional e sem violar termos de uso de plataformas externas.

## Arquivos criados

- `app/models/candle.py`
- `app/providers/base.py`
- `app/providers/simulated.py`
- `app/services/market_reader.py`
- `app/api/routes/market.py`
- `tests/test_market_reader.py`

## Arquivos alterados

- `app/api/router.py`
- `app/main.py`
- `app/core/config.py`
- `README.md`
- `.env.example`

## Endpoints novos

```text
GET /api/v1/market/candles
GET /api/v1/market/snapshot
```

## Como testar

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Depois acesse:

```text
http://127.0.0.1:8000/api/v1/market/snapshot
http://127.0.0.1:8000/api/v1/market/candles?symbol=EURUSD-OTC&timeframe=M1&limit=20
http://127.0.0.1:8000/docs
```

## Critérios de validação

- A API deve iniciar sem erro.
- `/api/v1/health` deve retornar status online.
- `/api/v1/market/snapshot` deve retornar o último candle simulado.
- `/api/v1/market/candles` deve retornar uma lista de candles OHLC.
- `pytest` deve passar.

## Importante

Os dados desta Sprint são simulados. Não são sinais reais de operação e não devem ser usados para entrada em mercado.

## Status

Sprint 2 pronta para validação local.
