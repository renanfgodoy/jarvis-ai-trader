# J.A.R.V.I.S AI TRADER

Sistema proprietário de apoio à decisão em Trading desenvolvido para Renan Godoy.

> Primeiro proteger a banca. Depois crescer a banca.  
> Não buscamos mais operações. Buscamos operações melhores.

## Sprint atual

**Sprint 5 — Provider Engine**

Esta Sprint cria a camada oficial de provedores e adiciona o recebimento de alertas do TradingView por webhook.

## Funcionalidades atuais

- Backend em FastAPI
- Arquitetura modular
- Configuração centralizada
- Health check
- System info
- Market Reader Service
- Provider simulado de candles
- AI Decision Engine V1
- Risk Manager Foundation
- Provider Engine
- TradingView Webhook Receiver
- Models Pydantic
- Testes automatizados

## Tecnologias

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic Settings
- Pytest

## Como rodar

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
http://127.0.0.1:8000/api/v1/market/snapshot
http://127.0.0.1:8000/api/v1/ai/decision
http://127.0.0.1:8000/api/v1/risk/check
http://127.0.0.1:8000/api/v1/providers
```

## Como testar

```bash
python -m pytest
```

## Sprint 5 — Provider Engine

Novo endpoint para listar provedores:

```text
GET /api/v1/providers
```

Novo endpoint para receber alertas do TradingView:

```text
POST /api/v1/providers/tradingview/webhook
```

Payload de exemplo:

```json
{
  "symbol": "EURUSD-OTC",
  "timeframe": "M1",
  "signal": "BUY",
  "price": 1.17545,
  "strategy": "Jarvis v1"
}
```

Resposta esperada:

```json
{
  "received": true,
  "provider": "TradingView",
  "status": "queued"
}
```

## Aviso operacional

Os dados e alertas desta fase são usados apenas para desenvolvimento, validação de arquitetura e apoio à decisão. O sistema não promete lucro, não garante assertividade e não executa ordens automaticamente.
