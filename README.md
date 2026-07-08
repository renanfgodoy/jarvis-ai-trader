# J.A.R.V.I.S AI TRADER

Sistema proprietário de apoio à decisão em Trading desenvolvido para Renan Godoy.

> Primeiro proteger a banca. Depois crescer a banca.  
> Não buscamos mais operações. Buscamos operações melhores.

## Sprint atual

**Sprint 2 — Market Reader Foundation**

Esta Sprint cria a fundação de leitura de mercado com candles OHLC normalizados e provider simulado para desenvolvimento seguro.

## Funcionalidades atuais

- Backend em FastAPI
- Arquitetura modular
- Configuração centralizada
- Health check
- System info
- Market Reader Service
- Provider simulado de candles
- Models Pydantic para Candle e MarketSnapshot
- Endpoints de candles e snapshot
- Testes automatizados

## Tecnologias

- Python
- FastAPI
- Uvicorn
- Pydantic Settings
- Pytest

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/v1/health
http://127.0.0.1:8000/api/v1/market/snapshot
http://127.0.0.1:8000/api/v1/market/candles?symbol=EURUSD-OTC&timeframe=M1&limit=20
```

## Como testar

```bash
pytest
```

## Aviso operacional

Os candles da Sprint 2 são simulados. Eles servem apenas para validar arquitetura e fluxo técnico. Não devem ser usados como sinal real de operação.
